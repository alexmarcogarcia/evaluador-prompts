"""Prompt de sistema de la mejora (T051, ADR-0003 decisión 5).

Verifica que no diverge del contrato ni de la spec: RF-009 (cambios ligados a problemas), RF-010
(marcador [COMPLETAR: …] para lo omitido) y RF-013 (mejora en el idioma del prompt; explicaciones
en el de la interfaz).
"""

import json
from pathlib import Path

from evaluador.casos_uso.mejorar import MARCADOR
from evaluador.prompts import cargar

CONTRATO = Path(__file__).resolve().parents[2] / "contracts" / "mejora.schema.json"


def test_el_prompt_de_mejora_pide_los_campos_del_contrato() -> None:
    contrato = json.loads(CONTRATO.read_text(encoding="utf-8"))
    texto = cargar("mejora")
    for campo in contrato["required"] + contrato["$defs"]["cambio"]["required"]:
        assert f'"{campo}"' in texto


def test_el_prompt_de_mejora_incluye_las_reglas_de_la_spec() -> None:
    texto = cargar("mejora")
    assert "{idioma}" in texto
    assert MARCADOR in texto
    assert "MISMO idioma del PROMPT ORIGINAL" in texto
    assert "No inventes" in texto
