"""Aceptación de la historia P1 · Diagnosticar un prompt (T030), a nivel de caso de uso.

Criterios dado/cuando/entonces de P1 y de RF-001, RF-002, RF-005, RF-014 y RF-015, con el doble del
modelo (sin red). La parte de interfaz se prueba con la web, en T032.
"""

import pytest

from evaluador.casos_uso.diagnosticar import Diagnosticar, EntradaInvalida, MotivoEntrada
from evaluador.dominio.modelos import (
    Categoria,
    DiagnosticoPropuesto,
    PreguntaPropuesta,
    ProblemaPropuesto,
    TipoProblema,
)
from evaluador.puertos.modelo_ia import ErrorProveedor, TipoError
from tests.dobles.modelo_falso import ModeloFalso

PROMPT = "Escríbeme algo sobre el cambio climático que esté bien."
ESPERADO = "Un artículo de 500 palabras para alumnos de 15 años."

AMBIGUO = ProblemaPropuesto("texto", 1, "Escríbeme algo", None, "No dices qué tipo de texto quieres.", "alta")
SIN_FORMATO = ProblemaPropuesto(
    "ausencia", 4, None, "Longitud: 500 palabras", "No dices la extensión.", "media"
)


def test_un_objetivo_ambiguo_aparece_con_su_fragmento_y_explicacion() -> None:
    """P1: dado un prompt con objetivo ambiguo, el problema cita el fragmento y lo explica en llano."""
    caso = Diagnosticar(ModeloFalso(diagnostico=DiagnosticoPropuesto((AMBIGUO,), (), False)))
    diagnostico = caso.ejecutar(PROMPT, ESPERADO, idioma_interfaz="es")
    [problema] = diagnostico.problemas
    assert problema.categoria is Categoria.OBJETIVO_AMBIGUO
    assert problema.fragmento == "Escríbeme algo"
    assert problema.explicacion


def test_cada_problema_tiene_tipo_categoria_explicacion_y_gravedad() -> None:
    """P1 / RF-003: en el texto cita fragmento; por ausencia indica qué falta."""
    caso = Diagnosticar(ModeloFalso(diagnostico=DiagnosticoPropuesto((AMBIGUO, SIN_FORMATO), (), False)))
    texto, ausencia = caso.ejecutar(PROMPT, ESPERADO, idioma_interfaz="es").problemas
    assert texto.tipo is TipoProblema.EN_TEXTO and texto.fragmento
    assert ausencia.tipo is TipoProblema.POR_AUSENCIA and ausencia.falta and ausencia.fragmento is None


def test_un_prompt_sin_problemas_lo_dice_y_no_inventa_ninguno() -> None:
    """P1 / RF-005."""
    diagnostico = Diagnosticar(ModeloFalso()).ejecutar(PROMPT, ESPERADO, idioma_interfaz="es")
    assert diagnostico.sin_problemas


def test_sin_resultado_esperado_no_se_envia_y_se_pide() -> None:
    """P1 / RF-002: el modelo ni siquiera se llama."""
    modelo = ModeloFalso()
    with pytest.raises(EntradaInvalida) as fallo:
        Diagnosticar(modelo).ejecutar(PROMPT, "   ", idioma_interfaz="es")
    assert fallo.value.motivo is MotivoEntrada.FALTA_RESULTADO_ESPERADO
    assert modelo.llamadas == []


def test_un_prompt_vacio_no_se_envia() -> None:
    """Caso límite de la spec: prompt vacío o solo con espacios."""
    modelo = ModeloFalso()
    with pytest.raises(EntradaInvalida) as fallo:
        Diagnosticar(modelo).ejecutar(" \n ", ESPERADO, idioma_interfaz="es")
    assert fallo.value.motivo is MotivoEntrada.PROMPT_VACIO
    assert modelo.llamadas == []


def test_8000_caracteres_se_envian_y_8001_no_indicando_cuanto_sobra() -> None:
    """RF-001."""
    modelo = ModeloFalso()
    Diagnosticar(modelo).ejecutar("a" * 8000, ESPERADO, idioma_interfaz="es")
    with pytest.raises(EntradaInvalida) as fallo:
        Diagnosticar(modelo).ejecutar("a" * 8001, ESPERADO, idioma_interfaz="es")
    assert fallo.value.motivo is MotivoEntrada.DEMASIADO_LARGO
    assert fallo.value.caracteres_sobrantes == 1
    assert len(modelo.llamadas) == 1


def test_un_prompt_peligroso_se_rechaza_sin_diagnostico() -> None:
    """RF-015."""
    propuesta = DiagnosticoPropuesto((AMBIGUO,), (PreguntaPropuesta("¿?", 1),), rechazado=True)
    diagnostico = Diagnosticar(ModeloFalso(diagnostico=propuesta)).ejecutar(PROMPT, ESPERADO, "es")
    assert diagnostico.rechazado and not diagnostico.problemas and not diagnostico.preguntas


def test_un_fallo_del_proveedor_llega_a_la_interfaz_con_su_tipo() -> None:
    """RF-014: la interfaz lo explicará y conservará lo escrito."""
    caso = Diagnosticar(ModeloFalso(error=ErrorProveedor(TipoError.NO_DISPONIBLE)))
    with pytest.raises(ErrorProveedor) as fallo:
        caso.ejecutar(PROMPT, ESPERADO, idioma_interfaz="es")
    assert fallo.value.tipo is TipoError.NO_DISPONIBLE


def test_el_original_no_se_modifica() -> None:
    """RF-012."""
    diagnostico = Diagnosticar(ModeloFalso()).ejecutar(PROMPT, ESPERADO, idioma_interfaz="es")
    assert (diagnostico.prompt.texto, diagnostico.prompt.resultado_esperado) == (PROMPT, ESPERADO)
