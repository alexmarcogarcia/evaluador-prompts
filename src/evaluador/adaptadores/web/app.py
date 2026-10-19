"""Interfaz web de las historias P1, P2 y P3 (ADR-0002, T032, T041, T053).

Adaptador en el borde: traduce formularios a llamadas al caso de uso y resultados a HTML. Todo el
texto del usuario o del modelo pasa por el autoescape de Jinja2 (RNF-010): nunca se marca como
seguro. El resaltado de fragmentos se construye por segmentos, sin insertar HTML.
"""

import json
from functools import cache
from importlib.resources import files
from typing import Annotated

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, PackageLoader

from evaluador.adaptadores.web.comparacion import comparar
from evaluador.adaptadores.web.estado import EstadoInvalido, leer_respuestas, restaurar, serializar
from evaluador.casos_uso.diagnosticar import Diagnosticar, EntradaInvalida, MotivoEntrada
from evaluador.casos_uso.mejorar import Mejorar
from evaluador.dominio.modelos import Diagnostico
from evaluador.puertos.modelo_ia import ErrorProveedor

IDIOMAS = ("es", "ca", "en", "de")
ERROR_POR_MOTIVO = {
    MotivoEntrada.PROMPT_VACIO: "error_prompt_vacio",
    MotivoEntrada.FALTA_RESULTADO_ESPERADO: "error_falta_resultado",
    MotivoEntrada.DEMASIADO_LARGO: "error_demasiado_largo",
}

plantillas = Environment(loader=PackageLoader("evaluador.adaptadores.web", "plantillas"), autoescape=True)


@cache
def textos(idioma: str) -> dict[str, str]:
    datos: dict[str, str] = json.loads(
        files("evaluador.adaptadores.web").joinpath(f"i18n/{idioma}.json").read_text(encoding="utf-8")
    )
    return datos


def segmentos(texto: str, fragmentos: list[str]) -> list[tuple[str, bool]]:
    """Parte el texto en tramos (texto, ¿marcado?) con la primera aparición de cada fragmento."""
    tramos: list[tuple[int, int]] = []
    for fragmento in fragmentos:
        inicio = texto.find(fragmento)
        fin = inicio + len(fragmento)
        if inicio >= 0 and fragmento and not any(a < fin and inicio < b for a, b in tramos):
            tramos.append((inicio, fin))
    resultado, cursor = [], 0
    for inicio, fin in sorted(tramos):
        resultado += [(texto[cursor:inicio], False), (texto[inicio:fin], True)]
        cursor = fin
    resultado.append((texto[cursor:], False))
    return [(t, m) for t, m in resultado if t]


def mensajes_de_error(t: dict[str, str], error: EntradaInvalida | ErrorProveedor) -> list[str]:
    """Errores en lenguaje llano (RF-001, RF-002, RF-014)."""
    if isinstance(error, EntradaInvalida):
        return [t[ERROR_POR_MOTIVO[error.motivo]].replace("{n}", str(error.caracteres_sobrantes))]
    mensajes = [t[f"error_{error.tipo.value}"]]
    if error.reintentar_en_s:
        mensajes.append(t["reintentar_en"].replace("{s}", str(error.reintentar_en_s)))
    return [*mensajes, t["reintentar"]]


def crear_app(diagnosticar: Diagnosticar, mejorar: Mejorar, *, proveedor: str, modelo: str) -> FastAPI:
    app = FastAPI(title="Evaluador de prompts", docs_url=None, redoc_url=None, openapi_url=None)

    def pagina(idioma: str, **contexto: object) -> HTMLResponse:
        t = textos(idioma)
        aviso = t["aviso_envio"].replace("{proveedor}", proveedor).replace("{modelo}", modelo)
        html = plantillas.get_template("pagina.html").render(
            t=t,
            idioma=idioma,
            idiomas=[(i, textos(i)["idioma_nombre"]) for i in IDIOMAS],
            aviso=aviso,
            **contexto,
        )
        return HTMLResponse(html)

    def resultado_del_diagnostico(idioma: str, diagnostico: Diagnostico, errores: list[str]) -> HTMLResponse:
        marcado = segmentos(
            diagnostico.prompt.texto, [p.fragmento for p in diagnostico.problemas if p.fragmento]
        )
        return pagina(
            idioma,
            prompt=diagnostico.prompt.texto,
            resultado=diagnostico.prompt.resultado_esperado,
            errores=errores,
            diagnostico=diagnostico,
            marcado=marcado,
            estado=serializar(diagnostico) if diagnostico.problemas else "",
        )

    @app.get("/", response_class=HTMLResponse)
    def inicio(idioma: str = "es") -> HTMLResponse:
        return pagina(idioma if idioma in IDIOMAS else "es", prompt="", resultado="")

    @app.post("/diagnosticar", response_class=HTMLResponse)
    def enviar(
        prompt: Annotated[str, Form()] = "",
        resultado: Annotated[str, Form()] = "",
        idioma: Annotated[str, Form()] = "es",
    ) -> HTMLResponse:
        idioma = idioma if idioma in IDIOMAS else "es"
        try:
            diagnostico = diagnosticar.ejecutar(prompt, resultado, idioma_interfaz=idioma)
        except (EntradaInvalida, ErrorProveedor) as error:
            return pagina(
                idioma, prompt=prompt, resultado=resultado, errores=mensajes_de_error(textos(idioma), error)
            )
        return resultado_del_diagnostico(idioma, diagnostico, [])

    @app.post("/mejorar", response_class=HTMLResponse)
    async def mejorar_prompt(request: Request) -> HTMLResponse:
        formulario = {clave: str(valor) for clave, valor in (await request.form()).items()}
        idioma = formulario.get("idioma", "es")
        idioma = idioma if idioma in IDIOMAS else "es"
        t = textos(idioma)
        try:
            diagnostico = restaurar(formulario.get("estado", ""))
        except EstadoInvalido:
            return pagina(idioma, prompt="", resultado="", errores=[t["error_estado_invalido"]])
        try:
            version = mejorar.ejecutar(diagnostico, leer_respuestas(diagnostico, formulario), idioma)
        except ErrorProveedor as error:
            return resultado_del_diagnostico(idioma, diagnostico, mensajes_de_error(t, error))
        original, mejorado = comparar(version.original.texto, version.texto)
        return pagina(
            idioma,
            prompt=version.original.texto,
            resultado=version.original.resultado_esperado,
            version=version,
            comparacion_original=original,
            comparacion_mejorado=mejorado,
            categorias={p.id: t[f"cat_{p.categoria.value}"] for p in diagnostico.problemas},
        )

    return app
