"""Entidades del dominio (T011).

Verifica RF-003 (campos de cada problema), RF-004 (catálogo cerrado de 9 categorías),
RF-012 (el prompt original es inmutable) y el invariante de la constitución 1.1 sobre los dos
tipos de problema.
"""

import dataclasses

import pytest

from evaluador.dominio.modelos import (
    Cambio,
    Categoria,
    Diagnostico,
    Gravedad,
    Pregunta,
    Problema,
    Prompt,
    TipoProblema,
)

PROMPT = Prompt(texto="Escríbeme algo que esté bien.")


def problema_en_texto(**cambios: object) -> Problema:
    datos: dict[str, object] = {
        "id": "P1",
        "tipo": TipoProblema.EN_TEXTO,
        "categoria": Categoria.VAGUEDAD_LEXICA,
        "explicacion": "«bien» no dice qué quieres.",
        "gravedad": Gravedad.ALTA,
        "fragmento": "que esté bien",
        "falta": None,
    }
    datos.update(cambios)
    return Problema(**datos)  # type: ignore[arg-type]


def test_el_catalogo_tiene_exactamente_las_9_categorias_de_la_spec() -> None:
    """RF-004: catálogo cerrado."""
    assert [c.value for c in Categoria] == list(range(1, 10))
    assert Categoria(4) is Categoria.FORMATO_DE_SALIDA


def test_el_prompt_original_no_se_puede_modificar() -> None:
    """RF-012."""
    with pytest.raises(dataclasses.FrozenInstanceError):
        PROMPT.texto = "otro"  # type: ignore[misc]


def test_un_problema_en_el_texto_tiene_todos_sus_campos() -> None:
    """RF-003: tipo, categoría, explicación, gravedad y fragmento."""
    p = problema_en_texto()
    assert (p.tipo, p.categoria, p.gravedad, p.fragmento) == (
        TipoProblema.EN_TEXTO,
        Categoria.VAGUEDAD_LEXICA,
        Gravedad.ALTA,
        "que esté bien",
    )


def test_un_problema_en_el_texto_sin_fragmento_es_invalido() -> None:
    """RF-003 / constitución 1.1: «en el texto» señala su fragmento."""
    with pytest.raises(ValueError, match="fragmento"):
        problema_en_texto(fragmento=None)


def test_un_problema_por_ausencia_indica_que_falta_y_no_cita_fragmento() -> None:
    """RF-003 / constitución 1.1: «por ausencia» indica qué falta."""
    p = problema_en_texto(
        tipo=TipoProblema.POR_AUSENCIA,
        categoria=Categoria.DESTINATARIO_O_TONO,
        fragmento=None,
        falta="Para quién es",
    )
    assert p.falta == "Para quién es"
    with pytest.raises(ValueError, match="falta"):
        problema_en_texto(tipo=TipoProblema.POR_AUSENCIA, fragmento=None, falta=None)
    with pytest.raises(ValueError, match="fragmento"):
        problema_en_texto(tipo=TipoProblema.POR_AUSENCIA, falta="algo")


def test_un_problema_necesita_explicacion() -> None:
    """RF-003: explicación en lenguaje llano obligatoria."""
    with pytest.raises(ValueError, match="explicación"):
        problema_en_texto(explicacion="  ")


def test_diagnostico_sin_problemas_lo_indica() -> None:
    """RF-005: sin problemas relevantes, se dice explícitamente."""
    assert Diagnostico(prompt=PROMPT, problemas=(), preguntas=()).sin_problemas
    assert not Diagnostico(prompt=PROMPT, problemas=(problema_en_texto(),), preguntas=()).sin_problemas


def test_un_diagnostico_rechazado_no_tiene_problemas_ni_preguntas() -> None:
    """RF-015: rechazo sin diagnóstico ni versión mejorada."""
    with pytest.raises(ValueError, match="rechaz"):
        Diagnostico(prompt=PROMPT, problemas=(problema_en_texto(),), preguntas=(), rechazado=True)


def test_una_pregunta_esta_ligada_al_problema_que_la_motiva() -> None:
    """RF-007."""
    assert Pregunta(id="Q1", texto="¿Para quién es?", problema_id="P1").problema_id == "P1"


def test_un_cambio_referencia_al_menos_un_problema() -> None:
    """RF-009."""
    with pytest.raises(ValueError, match="problema"):
        Cambio(explicacion="Añado el público.", problema_ids=())
