"""Lectura y puntuación de las evals (T022).

Valida también los propios datos de prueba: todo fragmento esperado debe ser literal en su prompt,
igual que exige RNF-004 al diagnóstico.
"""

from pathlib import Path

import pytest

from evals.casos import ARCHIVOS, cargar_validados, esta_validado, leer_casos
from evals.puntuacion import puntuar
from evaluador.dominio.modelos import Categoria, Diagnostico, Gravedad, Problema, Prompt, TipoProblema

MD = """**Estado:** validado
### C90 · Prueba
**Prompt:**
> Escribe algo bonito.

**Resultado esperado:** Un poema.

| Tipo | Cat. | Fragmento / qué falta |
|---|---|---|
| T | 9 | «bonito» |
| A | 4 | Longitud |

### C91 · Pendiente
**Prompt:**
> [PENDIENTE]

**Comportamiento esperado:** **rechazo**.
"""


def test_lee_prompt_resultado_y_esperados_y_salta_los_pendientes() -> None:
    casos = leer_casos(MD)
    assert [c.id for c in casos] == ["C90"]
    assert casos[0].prompt == "Escribe algo bonito."
    assert [(e.tipo, e.categoria, e.fragmento) for e in casos[0].esperados] == [
        ("T", 9, "bonito"),
        ("A", 4, None),
    ]


def test_solo_cuentan_los_archivos_validados(tmp_path: Path) -> None:
    validado, borrador = tmp_path / "a.md", tmp_path / "b.md"
    validado.write_text(MD, encoding="utf-8")
    borrador.write_text(MD.replace("validado", "pendiente de validación"), encoding="utf-8")
    casos, ignorados = cargar_validados((validado, borrador))
    assert [c.id for c in casos] == ["C90"]
    assert ignorados == [borrador]
    assert not esta_validado(borrador.read_text(encoding="utf-8"))


@pytest.mark.parametrize("archivo", ARCHIVOS, ids=lambda a: a.name)
def test_los_fragmentos_esperados_de_los_casos_reales_son_literales(archivo: Path) -> None:
    for caso in leer_casos(archivo.read_text(encoding="utf-8")):
        for esperado in caso.esperados:
            if esperado.fragmento:
                assert esperado.fragmento in caso.prompt, f"{caso.id}: «{esperado.fragmento}» no es literal"


def test_puntua_aciertos_y_falsos_positivos_por_categoria() -> None:
    caso = leer_casos(MD)[0]
    prompt = Prompt(caso.prompt, caso.resultado)
    vago = Problema(
        "P1", TipoProblema.EN_TEXTO, Categoria.VAGUEDAD_LEXICA, "Vago.", Gravedad.ALTA, "bonito", None
    )
    sobra = Problema(
        "P2", TipoProblema.POR_AUSENCIA, Categoria.FALTA_DE_CONTEXTO, "x", Gravedad.BAJA, None, "x"
    )
    puntos = puntuar(caso, Diagnostico(prompt=prompt, problemas=(vago, sobra), preguntas=()))
    assert (puntos.esperados, puntos.aciertos, puntos.senalados, puntos.falsos_positivos) == (2, 1, 2, 1)
    assert puntos.rechazo_correcto
