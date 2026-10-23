"""Aceptación de T150 y T151: ejemplos y pantalla inicial (spec 002 v1.1, RF-021; spec 001 v1.6, RF-002).

La pantalla inicial solo pide el prompt y ofrece 4 ejemplos en el idioma de la interfaz. Elegir uno
rellena el prompt: con scripts, al momento; sin scripts, el servidor devuelve el inicio relleno.
"""

import re

import pytest
from fastapi.testclient import TestClient

from evals.casos import ARCHIVOS, leer_casos
from evaluador.adaptadores.web.app import IDIOMAS, crear_app
from evaluador.adaptadores.web.ejemplos import EJEMPLOS
from evaluador.casos_uso.diagnosticar import Diagnosticar
from evaluador.casos_uso.mejorar import Mejorar
from tests.dobles.modelo_falso import ModeloFalso


def cliente() -> TestClient:
    modelo = ModeloFalso()
    return TestClient(crear_app(Diagnosticar(modelo), Mejorar(modelo), proveedor="falso", modelo="m"))


def campo_prompt(html: str) -> str:
    campo = re.search(r'<textarea id="prompt"[^>]*>(.*?)</textarea>', html, flags=re.S)
    assert campo is not None
    return campo.group(1)


def test_hay_4_ejemplos_en_cada_idioma_de_la_interfaz() -> None:
    assert set(EJEMPLOS) == set(IDIOMAS)
    assert all(len(ejemplos) == 4 for ejemplos in EJEMPLOS.values())


@pytest.mark.parametrize("idioma", IDIOMAS)
def test_el_inicio_muestra_los_ejemplos_del_idioma_y_solo_pide_el_prompt(idioma: str) -> None:
    pagina = cliente().get(f"/?idioma={idioma}").text
    botones = re.findall(r'<button[^>]*class="ejemplo"[^>]*>', pagina)
    assert len(botones) == 4
    assert all('formaction="/ejemplo"' in b and 'form="formulario"' in b for b in botones)
    for e in EJEMPLOS[idioma]:
        assert e.etiqueta.replace("'", "&#39;") in pagina
    assert pagina.count("<textarea") == 1  # RF-002 (spec 001 v1.6)


@pytest.mark.parametrize("idioma", IDIOMAS)
def test_elegir_un_ejemplo_sin_scripts_rellena_el_prompt(idioma: str) -> None:
    pagina = cliente().post("/ejemplo", data={"ejemplo": "2", "idioma": idioma, "prompt": ""}).text
    esperado = EJEMPLOS[idioma][2].prompt.replace("'", "&#39;")
    assert campo_prompt(pagina) == esperado
    assert f'<html lang="{idioma}">' in pagina


def test_un_ejemplo_inexistente_deja_el_texto_como_estaba() -> None:
    pagina = cliente().post("/ejemplo", data={"ejemplo": "9", "idioma": "es", "prompt": "mi texto"}).text
    assert campo_prompt(pagina) == "mi texto"


def test_los_ejemplos_no_repiten_casos_de_evals() -> None:
    prompts_de_evals = {c.prompt for a in ARCHIVOS for c in leer_casos(a.read_text(encoding="utf-8"))}
    assert not {e.prompt for ejemplos in EJEMPLOS.values() for e in ejemplos} & prompts_de_evals
