"""Aceptación de T141: cambiar de idioma sin perder el texto (spec 002, RF-022, RNF-006).

Al cambiar de idioma se vuelve al inicio con el prompt tal cual: no se traduce, porque es del usuario
(RF-012) y se acepta en cualquier idioma (RF-013); el idioma solo cambia la interfaz. El texto viaja
por POST, nunca en la URL (RNF-006).
"""

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from evaluador.adaptadores.web.app import crear_app
from evaluador.casos_uso.diagnosticar import Diagnosticar
from evaluador.casos_uso.mejorar import Mejorar
from evaluador.dominio.modelos import DiagnosticoPropuesto, ProblemaPropuesto
from tests.dobles.modelo_falso import ModeloFalso

WEB = Path(__file__).resolve().parents[2] / "src" / "evaluador" / "adaptadores" / "web"
PROMPT = "Escríbeme algo que esté bien & <rápido>."
VAGO = ProblemaPropuesto("texto", 9, "que esté bien", None, "«Bien» no dice qué quieres.", "alta")


def textos(idioma: str) -> dict[str, str]:
    datos: dict[str, str] = json.loads((WEB / "i18n" / f"{idioma}.json").read_text(encoding="utf-8"))
    return datos


def cliente() -> TestClient:
    modelo = ModeloFalso(diagnostico=DiagnosticoPropuesto((VAGO,), (), False))
    return TestClient(crear_app(Diagnosticar(modelo), Mejorar(modelo), proveedor="falso", modelo="m"))


def campo_prompt(html: str) -> str:
    campo = re.search(r'<textarea id="prompt"[^>]*>(.*?)</textarea>', html, flags=re.S)
    assert campo is not None
    return campo.group(1)


def botones_de_idioma(html: str) -> list[str]:
    return re.findall(r'<button[^>]*name="nuevo_idioma"[^>]*>', html)


@pytest.mark.parametrize("destino", ["ca", "en", "de"])
def test_cambiar_de_idioma_conserva_el_prompt_sin_traducirlo(destino: str) -> None:
    pagina = cliente().post("/idioma", data={"nuevo_idioma": destino, "prompt": PROMPT}).text
    assert f'<html lang="{destino}">' in pagina
    assert textos(destino)["titulo"] in pagina
    assert campo_prompt(pagina) == "Escríbeme algo que esté bien &amp; &lt;rápido&gt;."


def test_en_el_inicio_los_botones_envian_lo_que_hay_escrito_en_el_formulario() -> None:
    """Sin scripts: el botón pertenece al formulario del prompt, así que se envía lo escrito."""
    pagina = cliente().get("/").text
    botones = botones_de_idioma(pagina)
    assert len(botones) == 4
    assert all('form="formulario"' in b and 'formaction="/idioma"' in b for b in botones)
    assert 'id="formulario"' in pagina


def test_con_un_resultado_en_pantalla_se_vuelve_al_inicio_con_el_prompt() -> None:
    c = cliente()
    revision = c.post("/diagnosticar", data={"prompt": PROMPT, "idioma": "es"}).text
    # El formulario del prompt sigue en la pantalla de revisión: los botones envían lo que contiene.
    assert campo_prompt(revision) == "Escríbeme algo que esté bien &amp; &lt;rápido&gt;."
    assert all('form="formulario"' in b for b in botones_de_idioma(revision))
    pagina = c.post("/idioma", data={"nuevo_idioma": "ca", "prompt": PROMPT}).text
    assert 'aria-current="step">' + textos("ca")["paso_escribir"] in pagina
    assert campo_prompt(pagina) == "Escríbeme algo que esté bien &amp; &lt;rápido&gt;."


def test_el_texto_nunca_viaja_en_la_url() -> None:
    """RNF-006: ni enlaces ni acciones con el prompt en la dirección."""
    c = cliente()
    for pagina in (c.get("/").text, c.post("/diagnosticar", data={"prompt": PROMPT, "idioma": "es"}).text):
        assert re.search(r"[?&]prompt=", pagina) is None
        selector = re.search(r'<div class="idiomas"[^>]*>.*?</div>', pagina, flags=re.S)
        assert selector is not None and "href=" not in selector.group(0)


def test_un_idioma_desconocido_vuelve_al_espanol() -> None:
    pagina = cliente().post("/idioma", data={"nuevo_idioma": "xx", "prompt": "hola"}).text
    assert '<html lang="es">' in pagina
    assert campo_prompt(pagina) == "hola"


def test_el_idioma_actual_se_marca_y_cada_boton_lleva_su_nombre() -> None:
    """RNF-014: el lector de pantalla dice «Català», no «CA»."""
    botones = botones_de_idioma(cliente().get("/?idioma=ca").text)
    actual = [b for b in botones if 'aria-current="true"' in b]
    assert len(actual) == 1 and 'value="ca"' in actual[0]
    assert all("aria-label=" in b for b in botones)
