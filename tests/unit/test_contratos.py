"""Los contratos JSON coinciden con el dominio (T010).

Verifica que contracts/ y el catálogo del dominio no divergen: RF-003 (campos del problema),
RF-004 (categorías), RF-007 (máximo de preguntas), RF-009 (cambios con problemas) y RF-015 (rechazo).
"""

import json
from pathlib import Path
from typing import Any

from evaluador.dominio import reglas
from evaluador.dominio.modelos import Categoria, Gravedad, TipoProblema

CONTRATOS = Path(__file__).resolve().parents[2] / "contracts"


def cargar(nombre: str) -> dict[str, Any]:
    datos: dict[str, Any] = json.loads((CONTRATOS / nombre).read_text(encoding="utf-8"))
    return datos


def test_el_contrato_de_diagnostico_usa_el_catalogo_del_dominio() -> None:
    problema = cargar("diagnostico.schema.json")["$defs"]["problema"]["properties"]
    assert problema["categoria"]["enum"] == [c.value for c in Categoria]
    assert problema["tipo"]["enum"] == [t.value for t in TipoProblema]
    assert problema["gravedad"]["enum"] == [g.value for g in Gravedad]


def test_el_contrato_de_diagnostico_exige_los_campos_de_la_spec() -> None:
    esquema = cargar("diagnostico.schema.json")
    assert set(esquema["required"]) == {"rechazado", "problemas", "preguntas"}
    assert set(esquema["$defs"]["problema"]["required"]) == {
        "tipo",
        "categoria",
        "fragmento",
        "falta",
        "explicacion",
        "gravedad",
    }
    assert esquema["properties"]["preguntas"]["maxItems"] == reglas.MAX_PREGUNTAS


def test_el_contrato_de_mejora_liga_cada_cambio_a_problemas() -> None:
    cambio = cargar("mejora.schema.json")["$defs"]["cambio"]
    assert cambio["properties"]["problemas"]["minItems"] == 1
