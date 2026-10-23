"""Aceptación de la historia P1 (spec 002) · progreso, sin doble envío y sin saltos (T112, T113).

La parte del servidor: el marcado que usa `static/sharpener.js` y los textos del progreso en los 4
idiomas. El comportamiento en el navegador (aparece en < 200 ms, botón bloqueado, desplazamiento al
contenido nuevo) se verifica con la lista manual de la T161 (ADR-0004).
Verifica RF-017, RF-019 y RF-023 en lo que toca al servidor, y que sin scripts todo sigue igual.
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
VAGO = ProblemaPropuesto("texto", 9, "que esté bien", None, "«Bien» no dice qué quieres.", "alta")


def textos(idioma: str) -> dict[str, str]:
    datos: dict[str, str] = json.loads((WEB / "i18n" / f"{idioma}.json").read_text(encoding="utf-8"))
    return datos


@pytest.fixture
def cliente() -> TestClient:
    modelo = ModeloFalso(diagnostico=DiagnosticoPropuesto((VAGO,), (), False))
    return TestClient(crear_app(Diagnosticar(modelo), Mejorar(modelo), proveedor="falso", modelo="m"))


def test_la_pagina_carga_el_script_propio_sin_bloquear_la_lectura(cliente: TestClient) -> None:
    pagina = cliente.get("/").text
    assert re.search(r'<script src="/static/sharpener\.js\?v=[0-9a-f]{8}" defer></script>', pagina)
    assert cliente.get("/static/sharpener.js").status_code == 200


@pytest.mark.parametrize("idioma", ["es", "ca", "en", "de"])
def test_cada_formulario_lleva_el_texto_de_su_paso_en_el_idioma_de_la_interfaz(
    cliente: TestClient, idioma: str
) -> None:
    """RF-017: «Afilando tu prompt…» al revisar y «Puliendo la versión mejorada…» al mejorar."""
    t = textos(idioma)
    inicio = cliente.get(f"/?idioma={idioma}").text
    assert f'data-progreso="{t["progreso_revisar"]}"' in inicio
    diagnostico = cliente.post(
        "/diagnosticar",
        data={"prompt": "Escríbeme algo que esté bien.", "idioma": idioma},
    ).text
    assert f'data-progreso="{t["progreso_mejorar"]}"' in diagnostico


def test_hay_una_region_de_estado_para_anunciar_el_progreso(cliente: TestClient) -> None:
    """RF-017 y RNF-014: el progreso se anuncia también a los lectores de pantalla."""
    pagina = cliente.get("/").text
    region = re.search(r'<div id="progreso"[^>]*>', pagina)
    assert region is not None
    assert 'role="status"' in region.group(0) and 'aria-live="polite"' in region.group(0)
    assert " hidden" in region.group(0)  # Sin scripts no se ve nunca.


def test_cada_seccion_nueva_se_puede_enfocar_para_llevar_la_vista_a_ella(cliente: TestClient) -> None:
    """RF-023: el script desplaza la vista y el foco al título de la sección nueva."""
    pagina = cliente.post("/diagnosticar", data={"prompt": "Escríbeme algo que esté bien."}).text
    assert re.search(r'<h2 id="titulo-diagnostico" tabindex="-1"', pagina)


def test_el_script_no_construye_html_con_datos_del_usuario() -> None:
    """ADR-0004 / RNF-010: el script solo coloca HTML generado (y escapado) por el servidor."""
    script = (WEB / "static" / "sharpener.js").read_text(encoding="utf-8")
    assert "eval(" not in script and "document.write" not in script and "innerHTML" not in script
    assert "DOMParser" in script  # Toma los nodos de la respuesta del servidor, ya escapada por Jinja2.
