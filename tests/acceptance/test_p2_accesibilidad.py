"""Revisión automática de accesibilidad (T160, RNF-014): lo que se puede comprobar en el HTML.

Cada pantalla del recorrido (inicio, revisión con preguntas, mejora y error) y en los 4 idiomas:
- cada campo tiene su etiqueta y cada botón un nombre legible por un lector de pantalla;
- un solo h1 y títulos sin saltos de nivel;
- enlace para saltar al contenido, sin tabindex positivos, identificadores únicos y SVG decorativos
  ocultos al lector.
Lo que no se puede comprobar así (teclado real, lector de pantalla y 360 px) va en la lista manual de
`specs/002-interfaz/research.md`.
"""

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from evaluador.adaptadores.web.app import IDIOMAS, crear_app
from evaluador.adaptadores.web.estado import serializar
from evaluador.casos_uso.diagnosticar import Diagnosticar
from evaluador.casos_uso.mejorar import Mejorar
from evaluador.dominio.modelos import (
    DiagnosticoPropuesto,
    MejoraPropuesta,
    PreguntaPropuesta,
    ProblemaPropuesto,
)
from tests.dobles.modelo_falso import ModeloFalso

WEB = Path(__file__).resolve().parents[2] / "src" / "evaluador" / "adaptadores" / "web"
PROMPT = "Escríbeme algo que esté bien."
VAGO = ProblemaPropuesto("texto", 9, "que esté bien", None, "«Bien» no dice qué quieres.", "alta")
PREGUNTA = PreguntaPropuesta("¿Para quién es?", 1)


class Analisis(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.etiquetas_for: set[str] = set()
        self.campos: list[dict[str, str | None]] = []
        self.botones: list[dict[str, str | None]] = []
        self.titulos: list[int] = []
        self.ids: list[str] = []
        self.tabindex: list[str] = []
        self.svgs: list[dict[str, str | None]] = []
        self.enlaces: list[dict[str, str | None]] = []
        self._boton: dict[str, str | None] | None = None
        self._texto_boton = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(str(a["id"]))
        if a.get("tabindex"):
            self.tabindex.append(str(a["tabindex"]))
        if tag == "label" and a.get("for"):
            self.etiquetas_for.add(str(a["for"]))
        if tag in ("textarea", "select") or (tag == "input" and a.get("type") != "hidden"):
            self.campos.append(a)
        if tag == "button":
            self._boton, self._texto_boton = a, ""
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.titulos.append(int(tag[1]))
        if tag == "svg":
            self.svgs.append(a)
        if tag == "a":
            self.enlaces.append(a)

    def handle_data(self, data: str) -> None:
        if self._boton is not None:
            self._texto_boton += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "button" and self._boton is not None:
            self.botones.append({**self._boton, "_texto": self._texto_boton.strip()})
            self._boton = None


def pantallas(idioma: str) -> dict[str, str]:
    modelo = ModeloFalso(
        diagnostico=DiagnosticoPropuesto((VAGO,), (PREGUNTA,), False),
        mejora=MejoraPropuesta("Escribe un poema de 8 versos para mi abuela.", ()),
    )
    c = TestClient(crear_app(Diagnosticar(modelo), Mejorar(modelo), proveedor="falso", modelo="m"))
    diagnostico = Diagnosticar(modelo).ejecutar(PROMPT, idioma_interfaz=idioma)
    return {
        "inicio": c.get(f"/?idioma={idioma}").text,
        "revision": c.post("/diagnosticar", data={"prompt": PROMPT, "idioma": idioma}).text,
        "mejora": c.post("/mejorar", data={"idioma": idioma, "estado": serializar(diagnostico)}).text,
        "error": c.post("/diagnosticar", data={"prompt": "  ", "idioma": idioma}).text,
    }


CASOS = [(idioma, nombre) for idioma in IDIOMAS for nombre in ("inicio", "revision", "mejora", "error")]


def analizar(idioma: str, nombre: str) -> Analisis:
    analisis = Analisis()
    analisis.feed(pantallas(idioma)[nombre])
    return analisis


@pytest.mark.parametrize(("idioma", "nombre"), CASOS)
def test_cada_campo_tiene_su_etiqueta(idioma: str, nombre: str) -> None:
    a = analizar(idioma, nombre)
    assert a.campos, "la pantalla debería tener al menos el campo del prompt"
    for campo in a.campos:
        assert campo.get("id") in a.etiquetas_for or campo.get("aria-label"), campo


@pytest.mark.parametrize(("idioma", "nombre"), CASOS)
def test_cada_boton_tiene_un_nombre_legible(idioma: str, nombre: str) -> None:
    for boton in analizar(idioma, nombre).botones:
        assert boton["_texto"] or boton.get("aria-label"), boton


@pytest.mark.parametrize(("idioma", "nombre"), CASOS)
def test_un_solo_h1_y_titulos_sin_saltos(idioma: str, nombre: str) -> None:
    titulos = analizar(idioma, nombre).titulos
    assert titulos[0] == 1 and titulos.count(1) == 1
    assert all(despues - antes <= 1 for antes, despues in zip(titulos, titulos[1:], strict=False))


@pytest.mark.parametrize(("idioma", "nombre"), CASOS)
def test_teclado_e_identificadores(idioma: str, nombre: str) -> None:
    a = analizar(idioma, nombre)
    assert a.enlaces[0].get("href") == "#contenido" and "contenido" in a.ids  # saltar al contenido
    assert all(int(t) <= 0 for t in a.tabindex)  # el orden del teclado es el del documento
    assert len(a.ids) == len(set(a.ids))
    assert all(svg.get("aria-hidden") == "true" for svg in a.svgs)


def test_nada_obliga_a_un_ancho_mayor_que_un_movil_de_360_px() -> None:
    """RNF-015: la comprobación con capturas a 360 px está en research.md; esto evita que se rompa.
    Ningún ancho fijo supera 328 px (360 menos los 16 px de margen a cada lado) y las rejillas se
    apilan con min(100%, …)."""
    css = (WEB / "static" / "sharpener.css").read_text(encoding="utf-8")
    for valor, unidad in re.findall(r"(?<![-\w])(?:min-)?width:\s*([0-9.]+)(px|rem)", css):
        assert float(valor) * (16 if unidad == "rem" else 1) <= 328, f"{valor}{unidad}"
    for minimo in re.findall(r"minmax\(([^,]+),", css):
        assert minimo.strip() == "0" or minimo.strip().startswith("min(100%"), minimo
    base = (WEB / "plantillas" / "base.html").read_text(encoding="utf-8")
    assert 'name="viewport" content="width=device-width' in base
