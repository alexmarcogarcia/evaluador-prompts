"""Integración del adaptador con el SDK openai, con un cliente simulado (T020).

Verifica RF-006 (proveedor y modelo), RF-013 (idioma de la interfaz en el prompt de sistema),
RF-014 (errores del proveedor traducidos) y RNF-006 (los logs solo llevan métricas).
"""

import json
import logging
from types import SimpleNamespace
from typing import Any

import httpx2
import openai
import pytest

from evaluador.adaptadores.modelo_openai_compatible import ModeloOpenAICompatible
from evaluador.dominio.modelos import (
    Categoria,
    Diagnostico,
    Gravedad,
    Pregunta,
    Problema,
    Prompt,
    TipoProblema,
)
from evaluador.puertos.modelo_ia import ErrorProveedor, TipoError

PROMPT = Prompt(texto="Escribe algo SECRETO-DEL-USUARIO")
RESPUESTA = json.dumps({"rechazado": False, "problemas": [], "preguntas": []})
PETICION = httpx2.Request("POST", "https://proveedor.invalid/chat/completions")


class ClienteSimulado:
    """Imita `OpenAI().chat.completions.create`: devuelve un texto o lanza una excepción del SDK."""

    def __init__(self, respuesta: str = RESPUESTA, error: Exception | None = None) -> None:
        self.respuesta, self.error = respuesta, error
        self.peticiones: list[dict[str, Any]] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **peticion: Any) -> Any:
        self.peticiones.append(peticion)
        if self.error:
            raise self.error
        mensaje = SimpleNamespace(content=self.respuesta)
        uso = SimpleNamespace(prompt_tokens=120, completion_tokens=80)
        return SimpleNamespace(choices=[SimpleNamespace(message=mensaje)], usage=uso)


def adaptador(cliente: ClienteSimulado) -> ModeloOpenAICompatible:
    return ModeloOpenAICompatible(
        proveedor="Google Gemini",
        modelo="gemini-3.5-flash-lite",
        base_url="https://proveedor.invalid",
        api_key="clave-de-prueba",
        prompt_diagnostico="Explica en {idioma}.",
        prompt_mejora="Mejora. Explica en {idioma}.",
        cliente=cliente,
    )


def respuesta_http(codigo: int, cabeceras: dict[str, str] | None = None) -> httpx2.Response:
    return httpx2.Response(codigo, request=PETICION, headers=cabeceras or {})


def test_expone_proveedor_y_modelo() -> None:
    """RF-006."""
    modelo = adaptador(ClienteSimulado())
    assert (modelo.proveedor, modelo.modelo) == ("Google Gemini", "gemini-3.5-flash-lite")


def test_envia_el_modelo_y_el_idioma_de_la_interfaz_en_el_prompt_de_sistema() -> None:
    """RF-013: explicaciones en el idioma de la interfaz."""
    cliente = ClienteSimulado()
    adaptador(cliente).diagnosticar(PROMPT, idioma_interfaz="ca")
    peticion = cliente.peticiones[0]
    assert peticion["model"] == "gemini-3.5-flash-lite"
    assert peticion["messages"][0] == {"role": "system", "content": "Explica en catalán."}
    assert "SECRETO-DEL-USUARIO" in peticion["messages"][1]["content"]
    assert "RESULTADO" not in peticion["messages"][1]["content"]  # RF-002 (spec 1.6)


def test_la_mejora_envia_diagnostico_y_respuestas() -> None:
    """RF-009, RF-010: el modelo recibe los problemas validados y qué preguntas se omitieron."""
    cliente = ClienteSimulado(respuesta=json.dumps({"texto": "Mejorado.", "cambios": []}))
    problema = Problema(
        id="P1",
        tipo=TipoProblema.POR_AUSENCIA,
        categoria=Categoria.DESTINATARIO_O_TONO,
        explicacion="No dices para quién es.",
        gravedad=Gravedad.ALTA,
        fragmento=None,
        falta="Destinatario",
    )
    preguntas = (Pregunta("Q1", "¿Para quién es?", "P1"), Pregunta("Q2", "¿Qué tono?", "P1"))
    diagnostico = Diagnostico(prompt=PROMPT, problemas=(problema,), preguntas=preguntas)
    mejora = adaptador(cliente).mejorar(diagnostico, {"Q1": "Para mi jefa", "Q2": None}, idioma_interfaz="es")
    contenido = cliente.peticiones[0]["messages"][1]["content"]
    assert mejora.texto == "Mejorado."
    assert "Para mi jefa" in contenido and "OMITIDA" in contenido


@pytest.mark.parametrize(
    ("error", "tipo"),
    [
        (openai.RateLimitError("límite", response=respuesta_http(429), body=None), TipoError.LIMITE_DE_USO),
        (
            openai.InternalServerError("caído", response=respuesta_http(503), body=None),
            TipoError.NO_DISPONIBLE,
        ),
        (openai.APITimeoutError(request=PETICION), TipoError.TIEMPO_AGOTADO),
        (openai.APIConnectionError(request=PETICION), TipoError.NO_DISPONIBLE),
        (
            openai.AuthenticationError("clave", response=respuesta_http(401), body=None),
            TipoError.NO_DISPONIBLE,
        ),
    ],
)
def test_los_errores_del_sdk_se_traducen_a_errores_del_puerto(error: Exception, tipo: TipoError) -> None:
    """RF-014."""
    with pytest.raises(ErrorProveedor) as fallo:
        adaptador(ClienteSimulado(error=error)).diagnosticar(PROMPT, idioma_interfaz="es")
    assert fallo.value.tipo is tipo


def test_el_limite_de_uso_indica_cuando_reintentar_si_el_proveedor_lo_dice() -> None:
    """RF-014: «se indica cuándo se podrá reintentar, si se sabe»."""
    error = openai.RateLimitError("límite", response=respuesta_http(429, {"retry-after": "7"}), body=None)
    with pytest.raises(ErrorProveedor) as fallo:
        adaptador(ClienteSimulado(error=error)).diagnosticar(PROMPT, idioma_interfaz="es")
    assert fallo.value.reintentar_en_s == 7


def test_los_logs_solo_llevan_metricas_nunca_texto_ni_claves(caplog: pytest.LogCaptureFixture) -> None:
    """RNF-006."""
    caplog.set_level(logging.DEBUG)
    adaptador(ClienteSimulado()).diagnosticar(PROMPT, idioma_interfaz="es")
    with pytest.raises(ErrorProveedor):
        adaptador(ClienteSimulado(error=openai.APITimeoutError(request=PETICION))).diagnosticar(PROMPT, "es")
    registro = caplog.text
    assert "gemini-3.5-flash-lite" in registro and "tokens" in registro
    for privado in ("SECRETO-DEL-USUARIO", "clave-de-prueba", "Explica en"):
        assert privado not in registro
