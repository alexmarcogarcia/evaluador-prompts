"""Ejemplos resueltos del prompt de diagnóstico (T035, ADR-0003 estrategia 3a).

Los ejemplos tienen que ser coherentes con lo que exigen la spec y el dominio: RESPUESTA con
estructura válida del contrato (RF-003) y citas literales (RNF-004). Si no lo son, enseñan al
modelo a incumplirlos. Tampoco pueden repetir casos de las evals, porque la medición dejaría de valer.
Las variantes en evaluación (evals/variantes/*.md, si las hay) se comprueban igual.
"""

from pathlib import Path

import pytest

from evals.casos import ARCHIVOS, leer_casos
from evaluador.adaptadores.modelo_openai_compatible import interpretar_diagnostico
from evaluador.dominio import reglas
from evaluador.dominio.modelos import Prompt
from evaluador.prompts import cargar

VARIANTES = Path(__file__).resolve().parents[2] / "evals" / "variantes"
FUENTES = {"diagnostico.md": cargar("diagnostico")} | {
    archivo.name: archivo.read_text(encoding="utf-8") for archivo in sorted(VARIANTES.glob("*.md"))
}


def ejemplos(texto: str) -> list[tuple[str, str, str]]:
    """(prompt, resultado esperado, respuesta) de cada ejemplo."""
    campos: dict[str, list[str]] = {"PROMPT: ": [], "RESULTADO ESPERADO: ": [], "RESPUESTA: ": []}
    for linea in texto.splitlines():
        for prefijo, lista in campos.items():
            if linea.startswith(prefijo):
                lista.append(linea.removeprefix(prefijo))
    return list(zip(*campos.values(), strict=True))


def test_el_prompt_oficial_tiene_ejemplos_resueltos() -> None:
    assert len(ejemplos(FUENTES["diagnostico.md"])) == 5


@pytest.mark.parametrize("nombre", FUENTES)
def test_los_ejemplos_cumplen_el_contrato_y_las_reglas_del_dominio(nombre: str) -> None:
    for texto, resultado, respuesta in ejemplos(FUENTES[nombre]):
        depurado = reglas.depurar_diagnostico(Prompt(texto, resultado), interpretar_diagnostico(respuesta))
        assert depurado.descartados == 0, f"ejemplo inválido: {texto[:40]}"


@pytest.mark.parametrize("nombre", FUENTES)
def test_los_ejemplos_no_repiten_casos_de_evals(nombre: str) -> None:
    prompts_de_evals = {c.prompt for a in ARCHIVOS for c in leer_casos(a.read_text(encoding="utf-8"))}
    for texto, _, _ in ejemplos(FUENTES[nombre]):
        assert texto not in prompts_de_evals
