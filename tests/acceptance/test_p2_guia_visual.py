"""Aceptación de la guía visual completa (spec 002): T120, T130, T131, T140.

Verifica RF-020 (botón «Copiar» con el texto exacto y aviso de [COMPLETAR]), RF-022 (pasos del
recorrido con el actual marcado), RF-024 (la guía aplicada: marca, títulos con la voz «afilar») y
RF-025 (interruptor de modo oscuro que recuerda la preferencia y, sin scripts, no aparece).
"""

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from evaluador.adaptadores.web.app import crear_app
from evaluador.adaptadores.web.estado import serializar
from evaluador.casos_uso.diagnosticar import Diagnosticar
from evaluador.casos_uso.mejorar import MARCADOR, Mejorar
from evaluador.dominio.modelos import DiagnosticoPropuesto, MejoraPropuesta, ProblemaPropuesto
from tests.dobles.modelo_falso import ModeloFalso

WEB = Path(__file__).resolve().parents[2] / "src" / "evaluador" / "adaptadores" / "web"
PROMPT = "Escríbeme algo que esté bien."
ESPERADO = "Un artículo de 500 palabras."
VAGO = ProblemaPropuesto("texto", 9, "que esté bien", None, "«Bien» no dice qué quieres.", "alta")
MEJORADO = "Escribe un artículo de 500 palabras para el blog del instituto."


def textos(idioma: str) -> dict[str, str]:
    datos: dict[str, str] = json.loads((WEB / "i18n" / f"{idioma}.json").read_text(encoding="utf-8"))
    return datos


def cliente(mejorado: str = MEJORADO) -> tuple[TestClient, ModeloFalso]:
    modelo = ModeloFalso(
        diagnostico=DiagnosticoPropuesto((VAGO,), (), False), mejora=MejoraPropuesta(mejorado, ())
    )
    app = crear_app(Diagnosticar(modelo), Mejorar(modelo), proveedor="falso", modelo="m")
    return TestClient(app), modelo


def paginas(idioma: str = "es", mejorado: str = MEJORADO) -> dict[str, str]:
    c, modelo = cliente(mejorado)
    inicio = c.get(f"/?idioma={idioma}").text
    datos = {"prompt": PROMPT, "resultado": ESPERADO, "idioma": idioma}
    revisar = c.post("/diagnosticar", data=datos).text
    diagnostico = Diagnosticar(modelo).ejecutar(PROMPT, ESPERADO, idioma_interfaz=idioma)
    mejorar = c.post("/mejorar", data={"idioma": idioma, "estado": serializar(diagnostico)}).text
    return {"escribir": inicio, "revisar": revisar, "mejorar": mejorar}


def paso_actual(html: str) -> str:
    actual = re.search(r'<li[^>]*aria-current="step"[^>]*>([^<]+)</li>', html)
    assert actual is not None
    return actual.group(1)


@pytest.mark.parametrize("idioma", ["es", "ca", "en", "de"])
def test_los_pasos_marcan_el_actual_en_cada_pantalla(idioma: str) -> None:
    """RF-022."""
    t = textos(idioma)
    for paso, html in paginas(idioma).items():
        assert paso_actual(html) == t[f"paso_{paso}"]
        assert html.count('aria-current="step"') == 1


def test_los_pasos_anteriores_se_marcan_como_hechos() -> None:
    """RF-022: en «Mejorar», «Escribir» y «Revisar» ya están hechos."""
    html = paginas()["mejorar"]
    assert len(re.findall(r'<li class="hecho"', html)) == 2


def test_el_boton_copiar_lleva_el_texto_exacto_de_la_mejora_y_sin_scripts_no_aparece() -> None:
    """RF-020: el script copia `data-copiar`; sin scripts el botón no se ve y el texto se selecciona."""
    html = paginas()["mejorar"]
    boton = re.search(r'<button[^>]*class="copiar"[^>]*>', html)
    assert boton is not None
    assert f'data-copiar="{MEJORADO}"' in boton.group(0)
    assert " hidden" in boton.group(0)
    assert 'id="texto-mejorado"' in html


def test_el_aviso_de_completar_solo_aparece_si_hay_marcadores() -> None:
    """RF-020: al copiar, se recuerda completar los [COMPLETAR: …] si los hay."""
    sin = re.search(r'<button[^>]*class="copiar"[^>]*>', paginas()["mejorar"])
    con = re.search(
        r'<button[^>]*class="copiar"[^>]*>', paginas(mejorado=f"Escribe. {MARCADOR} público]")["mejorar"]
    )
    assert sin is not None and con is not None
    assert "data-aviso-completar" not in sin.group(0)
    assert "data-aviso-completar" in con.group(0)


def test_el_interruptor_de_tema_esta_en_la_barra_y_sin_scripts_no_aparece() -> None:
    """RF-025: modo oscuro automático siempre; interruptor solo con scripts."""
    html = paginas()["escribir"]
    interruptor = re.search(r'<button[^>]*id="tema"[^>]*>', html)
    assert interruptor is not None
    assert " hidden" in interruptor.group(0) and "aria-pressed" in interruptor.group(0)


def test_la_preferencia_de_tema_se_aplica_antes_de_pintar() -> None:
    """RF-025: sin parpadeo; la preferencia guardada se aplica en el <head>."""
    cabecera = paginas()["escribir"].split("</head>")[0]
    assert "sharpener-tema" in cabecera and "dataset.theme" in cabecera


@pytest.mark.parametrize("idioma", ["es", "ca", "en", "de"])
def test_el_titulo_usa_la_voz_de_la_marca(idioma: str) -> None:
    """RF-024: la guía visual pide hablar de tú con el verbo «afilar»."""
    assert textos(idioma)["titulo"] in paginas(idioma)["escribir"]
    assert textos(idioma)["titulo"] != "Evaluador de prompts"
