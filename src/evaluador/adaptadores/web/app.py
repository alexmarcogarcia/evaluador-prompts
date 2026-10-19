"""Interfaz web de la historia P1 (ADR-0002, T032).

Adaptador en el borde: traduce formularios a llamadas al caso de uso y resultados a HTML. Todo el
texto del usuario o del modelo pasa por el autoescape de Jinja2 (RNF-010): nunca se marca como
seguro. El resaltado de fragmentos se construye por segmentos, sin insertar HTML.
"""

import json
from functools import cache
from importlib.resources import files
from typing import Annotated

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from jinja2 import Environment, PackageLoader

from evaluador.casos_uso.diagnosticar import Diagnosticar, EntradaInvalida, MotivoEntrada
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


def crear_app(diagnosticar: Diagnosticar, *, proveedor: str, modelo: str) -> FastAPI:
    app = FastAPI(title="Evaluador de prompts", docs_url=None, redoc_url=None, openapi_url=None)

    def pagina(idioma: str, **contexto: object) -> HTMLResponse:
        idioma = idioma if idioma in IDIOMAS else "es"
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

    @app.get("/", response_class=HTMLResponse)
    def inicio(idioma: str = "es") -> HTMLResponse:
        return pagina(idioma, prompt="", resultado="")

    @app.post("/diagnosticar", response_class=HTMLResponse)
    def enviar(
        prompt: Annotated[str, Form()] = "",
        resultado: Annotated[str, Form()] = "",
        idioma: Annotated[str, Form()] = "es",
    ) -> HTMLResponse:
        idioma = idioma if idioma in IDIOMAS else "es"
        t = textos(idioma)
        errores: list[str] = []
        diagnostico: Diagnostico | None = None
        try:
            diagnostico = diagnosticar.ejecutar(prompt, resultado, idioma_interfaz=idioma)
        except EntradaInvalida as error:
            errores.append(t[ERROR_POR_MOTIVO[error.motivo]].replace("{n}", str(error.caracteres_sobrantes)))
        except ErrorProveedor as error:
            errores.append(t[f"error_{error.tipo.value}"])
            if error.reintentar_en_s:
                errores.append(t["reintentar_en"].replace("{s}", str(error.reintentar_en_s)))
            errores.append(t["reintentar"])
        marcado = (
            segmentos(prompt, [p.fragmento for p in diagnostico.problemas if p.fragmento])
            if diagnostico
            else []
        )
        return pagina(
            idioma,
            prompt=prompt,
            resultado=resultado,
            errores=errores,
            diagnostico=diagnostico,
            marcado=marcado,
        )

    return app
