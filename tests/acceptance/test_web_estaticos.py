"""Archivos estáticos de la interfaz (T100, spec 002, ADR-0004).

Verifica RF-024 (la guía visual usa las tipografías y el logotipo propios) y que nada se carga de
Google en ejecución: la app sirve sus propias tipografías, con su licencia (RNF-006, amenaza A6).
"""

import re

import pytest
from fastapi.testclient import TestClient

from evaluador.adaptadores.web.app import crear_app
from evaluador.casos_uso.diagnosticar import Diagnosticar
from evaluador.casos_uso.mejorar import Mejorar
from tests.dobles.modelo_falso import ModeloFalso

DOMINIOS_EXTERNOS = ("googleapis.com", "gstatic.com", "cdn.", "unpkg.com", "jsdelivr")


@pytest.fixture
def cliente() -> TestClient:
    modelo = ModeloFalso()
    return TestClient(crear_app(Diagnosticar(modelo), Mejorar(modelo), proveedor="falso", modelo="m"))


def test_las_tipografias_se_sirven_desde_la_propia_app(cliente: TestClient) -> None:
    """RF-024: Bricolage Grotesque y Figtree, en latino y latino extendido (ca, de, es, en)."""
    css = cliente.get("/static/fuentes.css")
    assert css.status_code == 200
    archivos = re.findall(r"url\('fuentes/([^']+\.woff2)'\)", css.text)
    assert len(archivos) == 4
    for archivo in archivos:
        respuesta = cliente.get(f"/static/fuentes/{archivo}")
        assert respuesta.status_code == 200 and respuesta.content[:4] == b"wOF2"


def test_las_licencias_de_las_tipografias_acompanan_a_los_archivos(cliente: TestClient) -> None:
    for familia in ("bricolage-grotesque", "figtree"):
        licencia = cliente.get(f"/static/fuentes/OFL-{familia}.txt")
        assert licencia.status_code == 200 and "SIL Open Font License" in licencia.text


def test_la_pagina_usa_las_tipografias_y_el_logotipo_propios(cliente: TestClient) -> None:
    """RF-024."""
    pagina = cliente.get("/").text
    assert 'href="/static/fuentes.css"' in pagina
    assert 'href="/static/logo.svg"' in pagina
    assert cliente.get("/static/logo.svg").status_code == 200


@pytest.mark.parametrize("ruta", ["/", "/static/fuentes.css"])
def test_nada_se_carga_de_servicios_externos(cliente: TestClient, ruta: str) -> None:
    """RNF-006 / amenaza A6: ni Google ni CDNs conocen la IP de quien usa la app."""
    contenido = cliente.get(ruta).text
    assert not any(dominio in contenido for dominio in DOMINIOS_EXTERNOS)
