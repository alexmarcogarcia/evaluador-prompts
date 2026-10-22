"""Adaptador del puerto ModeloIA para cualquier API compatible con OpenAI (ADR-0001).

Sirve para Gemini (proveedor principal) y NVIDIA (alternativa) cambiando solo la configuración.
Valida la estructura de la respuesta (contracts/); los valores los valida el dominio (ADR-0003).
Los logs solo registran métricas, nunca texto ni claves (RNF-006).
"""

import json
import logging
import time
from typing import Any

import openai
from pydantic import BaseModel, ValidationError

from evaluador.dominio.modelos import (
    Diagnostico,
    DiagnosticoPropuesto,
    MejoraPropuesta,
    PreguntaPropuesta,
    ProblemaPropuesto,
    Prompt,
)
from evaluador.puertos.modelo_ia import ErrorProveedor, TipoError

registro = logging.getLogger("evaluador.modelo")

IDIOMAS = {"es": "español", "ca": "catalán", "en": "inglés", "de": "alemán"}


class RespuestaDiagnostico(BaseModel):
    """Estructura de contracts/diagnostico.schema.json."""

    class Problema(BaseModel):
        tipo: str
        categoria: int
        fragmento: str | None
        falta: str | None
        explicacion: str
        gravedad: str

    class Pregunta(BaseModel):
        texto: str
        problema: int

    rechazado: bool
    problemas: list[Problema]
    preguntas: list[Pregunta]
    motivo: str | None = None


class RespuestaMejora(BaseModel):
    """Estructura de contracts/mejora.schema.json."""

    class Cambio(BaseModel):
        explicacion: str
        problemas: list[str]

    texto: str
    cambios: list[Cambio]


def _extraer_json(texto: str) -> str:
    """Los modelos a veces envuelven el JSON en texto o en un bloque ```json."""
    inicio, fin = texto.find("{"), texto.rfind("}")
    if inicio < 0 or fin < inicio:
        registro.warning("respuesta_invalida motivo=sin_json longitud=%d", len(texto))
        raise ErrorProveedor(TipoError.RESPUESTA_INVALIDA)
    return texto[inicio : fin + 1]


def _registrar_invalida(contrato: str, error: ValidationError) -> None:
    """Registra qué campos fallaron y por qué, nunca sus valores (RNF-006)."""
    detalles = ", ".join(
        f"{'.'.join(str(x) for x in e['loc']) or '(raíz)'}:{e['type']}" for e in error.errors()
    )
    registro.warning("respuesta_invalida contrato=%s errores=%s", contrato, detalles)


def interpretar_diagnostico(texto: str) -> DiagnosticoPropuesto:
    try:
        r = RespuestaDiagnostico.model_validate_json(_extraer_json(texto))
    except ValidationError as error:
        _registrar_invalida("diagnostico", error)
        raise ErrorProveedor(TipoError.RESPUESTA_INVALIDA) from error
    return DiagnosticoPropuesto(
        problemas=tuple(
            ProblemaPropuesto(p.tipo, p.categoria, p.fragmento, p.falta, p.explicacion, p.gravedad)
            for p in r.problemas
        ),
        preguntas=tuple(PreguntaPropuesta(q.texto, q.problema) for q in r.preguntas),
        rechazado=r.rechazado,
    )


def interpretar_mejora(texto: str) -> MejoraPropuesta:
    try:
        r = RespuestaMejora.model_validate_json(_extraer_json(texto))
    except ValidationError as error:
        _registrar_invalida("mejora", error)
        raise ErrorProveedor(TipoError.RESPUESTA_INVALIDA) from error
    return MejoraPropuesta(
        texto=r.texto, cambios=tuple((c.explicacion, tuple(c.problemas)) for c in r.cambios)
    )


def _traducir_error(error: openai.OpenAIError) -> ErrorProveedor:
    if isinstance(error, openai.RateLimitError):
        espera = error.response.headers.get("retry-after", "")
        return ErrorProveedor(TipoError.LIMITE_DE_USO, int(espera) if espera.isdigit() else None)
    if isinstance(error, openai.APITimeoutError):  # Antes que APIConnectionError: es una subclase.
        return ErrorProveedor(TipoError.TIEMPO_AGOTADO)
    return ErrorProveedor(TipoError.NO_DISPONIBLE)


def _o_no_indicado(texto: str) -> str:
    """Un resultado esperado vacío se dice explícitamente, para que el modelo deduzca la intención."""
    return texto if texto.strip() else "(no indicado)"


def _bloque(etiqueta: str, contenido: str) -> str:
    """Delimita el texto del usuario para que el modelo lo trate como datos, no como órdenes (amenaza A4)."""
    return f"{etiqueta}:\n<<<\n{contenido}\n>>>"


class ModeloOpenAICompatible:
    def __init__(
        self,
        *,
        proveedor: str,
        modelo: str,
        base_url: str,
        api_key: str,
        prompt_diagnostico: str,
        prompt_mejora: str,
        timeout_s: float = 25,
        cliente: Any | None = None,
    ) -> None:
        self._proveedor, self._modelo = proveedor, modelo
        self._prompt_diagnostico, self._prompt_mejora = prompt_diagnostico, prompt_mejora
        # Un reintento del SDK ante 429/5xx; con 25 s de espera máxima se mantiene RNF-001 en lo posible.
        self._cliente = cliente or openai.OpenAI(
            api_key=api_key, base_url=base_url, timeout=timeout_s, max_retries=1
        )

    @property
    def proveedor(self) -> str:
        return self._proveedor

    @property
    def modelo(self) -> str:
        return self._modelo

    def diagnosticar(self, prompt: Prompt, idioma_interfaz: str) -> DiagnosticoPropuesto:
        usuario = (
            _bloque("PROMPT", prompt.texto)
            + "\n\n"
            + _bloque("RESULTADO ESPERADO", _o_no_indicado(prompt.resultado_esperado))
        )
        texto = self._completar("diagnosticar", self._prompt_diagnostico, idioma_interfaz, usuario)
        return interpretar_diagnostico(texto)

    def mejorar(
        self,
        diagnostico: Diagnostico,
        respuestas: dict[str, str | None],
        idioma_interfaz: str,
        idioma_prompt: str | None = None,
    ) -> MejoraPropuesta:
        problemas = [
            {
                "id": p.id,
                "tipo": p.tipo.value,
                "categoria": p.categoria.value,
                "fragmento": p.fragmento,
                "falta": p.falta,
                "explicacion": p.explicacion,
            }
            for p in diagnostico.problemas
        ]
        preguntas = [
            {"pregunta": q.texto, "problema": q.problema_id, "respuesta": respuestas.get(q.id) or "OMITIDA"}
            for q in diagnostico.preguntas
        ]
        usuario = "\n\n".join(
            [
                _bloque("PROMPT ORIGINAL", diagnostico.prompt.texto),
                _bloque("RESULTADO ESPERADO", _o_no_indicado(diagnostico.prompt.resultado_esperado)),
                _bloque("PROBLEMAS", json.dumps(problemas, ensure_ascii=False)),
                _bloque("PREGUNTAS Y RESPUESTAS", json.dumps(preguntas, ensure_ascii=False)),
                *(
                    [f'IDIOMA DEL PROMPT ORIGINAL: {IDIOMAS[idioma_prompt]}. Escribe "texto" en este idioma.']
                    if idioma_prompt in IDIOMAS
                    else []
                ),
            ]
        )
        texto = self._completar("mejorar", self._prompt_mejora, idioma_interfaz, usuario)
        return interpretar_mejora(texto)

    def _completar(self, operacion: str, plantilla: str, idioma_interfaz: str, usuario: str) -> str:
        sistema = plantilla.replace("{idioma}", IDIOMAS.get(idioma_interfaz, IDIOMAS["es"]))
        inicio = time.monotonic()
        try:
            respuesta = self._cliente.chat.completions.create(
                model=self._modelo,
                messages=[{"role": "system", "content": sistema}, {"role": "user", "content": usuario}],
                temperature=0,
            )
        except openai.OpenAIError as error:
            traducido = _traducir_error(error)
            registro.warning(
                "error operacion=%s proveedor=%s modelo=%s tipo=%s codigo=%s duracion_ms=%d",
                operacion,
                self._proveedor,
                self._modelo,
                traducido.tipo.value,
                getattr(error, "status_code", "-"),
                (time.monotonic() - inicio) * 1000,
            )
            raise traducido from error
        uso = getattr(respuesta, "usage", None)
        registro.info(
            "llamada operacion=%s proveedor=%s modelo=%s duracion_ms=%d tokens_entrada=%s tokens_salida=%s",
            operacion,
            self._proveedor,
            self._modelo,
            (time.monotonic() - inicio) * 1000,
            getattr(uso, "prompt_tokens", "-"),
            getattr(uso, "completion_tokens", "-"),
        )
        contenido: str = respuesta.choices[0].message.content or ""
        return contenido
