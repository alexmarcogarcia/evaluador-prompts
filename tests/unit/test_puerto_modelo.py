"""Puerto ModeloIA y su doble de prueba (T013, ADR-0001).

Verifica RF-006 (el puerto expone proveedor y modelo para mostrarlos antes de enviar) y
RF-014 (los fallos del proveedor llegan como un error con su tipo).
"""

import pytest

from evaluador.dominio.modelos import DiagnosticoPropuesto, MejoraPropuesta, Prompt
from evaluador.puertos.modelo_ia import ErrorProveedor, ModeloIA, TipoError
from tests.dobles.modelo_falso import ModeloFalso

PROMPT = Prompt(texto="hola", resultado_esperado="Una explicación.")
VACIO = DiagnosticoPropuesto(problemas=(), preguntas=(), rechazado=False)


def test_el_doble_cumple_el_puerto_y_expone_proveedor_y_modelo() -> None:
    """RF-006."""
    modelo: ModeloIA = ModeloFalso(diagnostico=VACIO)
    assert (modelo.proveedor, modelo.modelo) == ("falso", "modelo-de-prueba")


def test_el_doble_devuelve_lo_configurado_y_registra_las_llamadas() -> None:
    mejora = MejoraPropuesta(texto="mejorado", cambios=())
    modelo = ModeloFalso(diagnostico=VACIO, mejora=mejora)
    assert modelo.diagnosticar(PROMPT, idioma_interfaz="es") is VACIO
    assert modelo.llamadas == [("diagnosticar", PROMPT, "es")]


def test_un_fallo_del_proveedor_llega_como_error_con_tipo() -> None:
    """RF-014: límite de uso, caída, tiempo agotado o respuesta inválida."""
    modelo = ModeloFalso(error=ErrorProveedor(TipoError.LIMITE_DE_USO))
    with pytest.raises(ErrorProveedor) as fallo:
        modelo.diagnosticar(PROMPT, idioma_interfaz="es")
    assert fallo.value.tipo is TipoError.LIMITE_DE_USO
    assert {t.value for t in TipoError} == {
        "limite_de_uso",
        "no_disponible",
        "tiempo_agotado",
        "respuesta_invalida",
    }
