"""Aceptación de la historia P3 · Obtener una versión mejorada explicada (T050).

Verifica RF-009 (cada cambio referencia problemas que existen), RF-010 (si se omite una pregunta,
queda un marcador visible aunque el modelo lo olvide), RF-011 (original y mejorado a la vez con
las diferencias marcadas) y RF-012 (el original no cambia). También RNF-010 (texto escapado) y que
un estado manipulado no llega al modelo.
"""

import pytest
from fastapi.testclient import TestClient

from evaluador.adaptadores.web.app import crear_app
from evaluador.adaptadores.web.estado import serializar
from evaluador.casos_uso.diagnosticar import Diagnosticar
from evaluador.casos_uso.mejorar import MARCADOR, Mejorar
from evaluador.dominio.modelos import (
    Diagnostico,
    DiagnosticoPropuesto,
    MejoraPropuesta,
    PreguntaPropuesta,
    ProblemaPropuesto,
)
from tests.dobles.modelo_falso import ModeloFalso

PROMPT = "Escribe un correo para mi cliente."
ESPERADO = "Un correo cortés que explique un retraso de dos semanas."
TONO = ProblemaPropuesto("ausencia", 3, None, "Tono del correo", "No dices el tono.", "media")
MOTIVO = ProblemaPropuesto("ausencia", 2, None, "Motivo del retraso", "No dices qué ha pasado.", "alta")
PREGUNTAS = (PreguntaPropuesta("¿Qué tono quieres?", 1), PreguntaPropuesta("¿Por qué hay retraso?", 2))
MEJORADO = "Escribe un correo cordial para mi cliente explicando que su pedido llegará dos semanas tarde."
MEJORA = MejoraPropuesta(
    texto=MEJORADO,
    cambios=(("Indico el tono cordial.", ("P1",)), ("Explico el retraso.", ("P2",)), ("Inventado.", ("P7",))),
)


def modelo(mejora: MejoraPropuesta = MEJORA) -> ModeloFalso:
    return ModeloFalso(diagnostico=DiagnosticoPropuesto((TONO, MOTIVO), PREGUNTAS, False), mejora=mejora)


def diagnostico(m: ModeloFalso) -> Diagnostico:
    return Diagnosticar(m).ejecutar(PROMPT, ESPERADO, idioma_interfaz="es")


def pedir_mejora(m: ModeloFalso, respuestas: dict[str, str], estado: str | None = None) -> str:
    app = crear_app(Diagnosticar(m), Mejorar(m), proveedor="falso", modelo="m")
    datos = {
        "idioma": "es",
        "estado": estado if estado is not None else serializar(diagnostico(m)),
        **respuestas,
    }
    respuesta = TestClient(app).post("/mejorar", data=datos)
    assert respuesta.status_code == 200
    return respuesta.text


def test_cada_cambio_indica_que_problema_resuelve_y_se_descartan_los_inventados() -> None:
    """P3 / RF-009."""
    m = modelo()
    version = Mejorar(m).ejecutar(diagnostico(m), {"Q1": "Cordial", "Q2": "Huelga de transporte"}, "es")
    assert [(c.explicacion, c.problema_ids) for c in version.cambios] == [
        ("Indico el tono cordial.", ("P1",)),
        ("Explico el retraso.", ("P2",)),
    ]


def test_el_modelo_recibe_las_respuestas_y_las_omitidas_como_omitidas() -> None:
    """RF-008 / RF-010."""
    m = modelo()
    Mejorar(m).ejecutar(diagnostico(m), {"Q1": "Cordial", "Q2": None}, "es")
    operacion, _, respuestas, *_ = m.llamadas[-1]
    assert operacion == "mejorar"
    assert respuestas == {"Q1": "Cordial", "Q2": None}


def test_el_codigo_no_anade_marcadores_por_su_cuenta() -> None:
    """RF-010 (spec 1.5): si el dato ya está en el resultado esperado no hace falta marcador, y eso solo
    lo puede juzgar quien entiende el texto. Que no se invente lo omitido lo vigilan las evals (RNF-011)."""
    m = modelo()
    version = Mejorar(m).ejecutar(diagnostico(m), {"Q1": "Cordial", "Q2": None}, "es")
    assert version.texto == MEJORADO


def test_el_idioma_se_detecta_con_el_prompt_y_el_resultado_esperado() -> None:
    """RF-013: un prompt catalán muy corto no basta para saber el idioma; con el resultado esperado, sí."""
    catalan = MejoraPropuesta(
        texto="Fes una llista de la compra per a un sopar vegà per a 6 persones.", cambios=()
    )
    m = ModeloFalso(diagnostico=DiagnosticoPropuesto((TONO,), (), False), mejora=catalan)
    d = Diagnosticar(m).ejecutar(
        "Fes una llista de la compra.",
        "La llista per a un sopar vegà per a 6 persones, amb les seccions.",
        "es",
    )
    Mejorar(m).ejecutar(d, {}, "es")
    assert m.llamadas[-1][-1] == "ca"


def test_si_el_modelo_ya_puso_los_marcadores_no_se_duplican() -> None:
    """RF-010."""
    m = modelo(MejoraPropuesta(texto=f"Escribe un correo. {MARCADOR} motivo del retraso]", cambios=()))
    version = Mejorar(m).ejecutar(diagnostico(m), {"Q1": "Cordial", "Q2": None}, "es")
    assert version.texto.count(MARCADOR) == 1


def test_el_original_y_el_mejorado_se_ven_a_la_vez_con_las_diferencias_marcadas() -> None:
    """P3 / RF-011."""
    pagina = pedir_mejora(modelo(), {"respuesta_Q1": "Cordial", "respuesta_Q2": "Huelga"})
    assert "<ins>" in pagina and "Escribe un correo" in pagina
    assert "Indico el tono cordial." in pagina and "Inventado." not in pagina


def test_el_original_no_se_modifica() -> None:
    """RF-012."""
    m = modelo()
    d = diagnostico(m)
    version = Mejorar(m).ejecutar(d, {"Q1": None, "Q2": None}, "es")
    assert version.original.texto == PROMPT == d.prompt.texto


def test_un_estado_manipulado_no_llega_al_modelo() -> None:
    """RNF-004 / RNF-009: el diagnóstico se revalida al volver."""
    m = modelo()
    pagina = pedir_mejora(m, {}, estado='{"prompt": "x"}')
    assert "No hemos podido recuperar el diagnóstico" in pagina
    assert not any(llamada[0] == "mejorar" for llamada in m.llamadas)


def test_el_texto_mejorado_se_muestra_escapado() -> None:
    """RNF-010."""
    pagina = pedir_mejora(modelo(MejoraPropuesta(texto="<script>alert(1)</script>", cambios=())), {})
    assert "<script>alert(1)</script>" not in pagina and "&lt;script&gt;" in pagina


@pytest.mark.parametrize("idioma", ["ca", "de"])
def test_la_pagina_de_mejora_esta_en_el_idioma_de_la_interfaz(idioma: str) -> None:
    """RF-013."""
    m = modelo()
    app = crear_app(Diagnosticar(m), Mejorar(m), proveedor="falso", modelo="m")
    pagina = (
        TestClient(app).post("/mejorar", data={"idioma": idioma, "estado": serializar(diagnostico(m))}).text
    )
    assert {"ca": "Què hem canviat i per què", "de": "Was wir geändert haben und warum"}[idioma] in pagina


def test_si_la_mejora_sale_en_otro_idioma_se_rehace_una_vez_indicando_el_idioma() -> None:
    """RF-013: la mejora va en el idioma del prompt original; el código lo comprueba."""
    prompt_en = "Write a short message for my client about the delay."
    espanol = MejoraPropuesta(
        texto="Escribe un mensaje breve y cordial para mi cliente sobre el retraso.", cambios=()
    )
    ingles = MejoraPropuesta(
        texto="Write a short, friendly message for my client about the delay.", cambios=()
    )
    m = ModeloFalso(diagnostico=DiagnosticoPropuesto((TONO,), (), False), mejora=(espanol, ingles))
    d = Diagnosticar(m).ejecutar(prompt_en, "A friendly two-sentence message.", idioma_interfaz="es")
    version = Mejorar(m).ejecutar(d, {}, "es")
    assert version.texto == ingles.texto
    llamadas = [llamada for llamada in m.llamadas if llamada[0] == "mejorar"]
    assert len(llamadas) == 2 and llamadas[-1][-1] == "en"


def test_si_el_modelo_deja_algun_marcador_no_se_anaden_mas() -> None:
    """RF-010 (spec 1.5): si el modelo ya decidió qué falta, no se añaden marcadores para lo que ya está."""
    m = modelo(
        MejoraPropuesta(texto=f"Escribe un correo cordial. {MARCADOR} motivo del retraso]", cambios=())
    )
    version = Mejorar(m).ejecutar(diagnostico(m), {"Q1": None, "Q2": None}, "es")
    assert version.texto.count(MARCADOR) == 1
