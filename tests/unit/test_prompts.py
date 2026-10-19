"""Prompts de sistema versionados (T021, ADR-0003 decisión 5).

Verifica que el prompt de diagnóstico no diverge de la spec ni del contrato: RF-004 (las 9
categorías y sus fronteras), RF-007 (máximo de preguntas), RF-013 (idioma de la interfaz),
RF-015 (rechazo) y RF-016 (solo lo relevante para el resultado esperado).
"""

import json
from pathlib import Path

from evaluador.dominio import reglas
from evaluador.dominio.modelos import Categoria
from evaluador.prompts import cargar

CONTRATO = Path(__file__).resolve().parents[2] / "contracts" / "diagnostico.schema.json"


def test_el_prompt_de_diagnostico_existe_y_lleva_el_marcador_de_idioma() -> None:
    """RF-013: el adaptador sustituye {idioma} por el idioma de la interfaz."""
    texto = cargar("diagnostico")
    assert "{idioma}" in texto


def test_el_prompt_enumera_las_9_categorias_del_catalogo_en_orden() -> None:
    """RF-004."""
    texto = cargar("diagnostico")
    posiciones = [texto.find(f"\n  {c.value} ") for c in Categoria]
    assert all(p >= 0 for p in posiciones), "falta alguna categoría"
    assert posiciones == sorted(posiciones)


def test_el_prompt_pide_exactamente_los_campos_del_contrato() -> None:
    contrato = json.loads(CONTRATO.read_text(encoding="utf-8"))
    texto = cargar("diagnostico")
    for campo in contrato["required"] + contrato["$defs"]["problema"]["required"]:
        assert f'"{campo}"' in texto, f"el prompt no menciona el campo {campo}"


def test_el_prompt_incluye_las_reglas_de_la_spec() -> None:
    """RF-007, RF-015, RF-016 y reglas de clasificación 1 y 4."""
    texto = cargar("diagnostico").lower()
    assert f"máximo {reglas.MAX_PREGUNTAS}" in texto
    assert "rechaz" in texto
    assert "resultado esperado" in texto
    assert "5, 7, 8, 9, 4, 6, 3, 2, 1" in texto
    assert "misma categoría" in texto
