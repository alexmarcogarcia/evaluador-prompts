"""Aceptación de la historia P2 · Responder a preguntas aclaratorias (T040, T041).

Verifica RF-007 (como máximo 5 preguntas, cada una ligada a su problema) y RF-008 (cada pregunta se
puede responder u omitir). Para RF-010, una pregunta omitida llega como «sin respuesta», nunca
inventada. Verifica también que el diagnóstico viaja en el formulario sin guardarse (RNF-009) y se
vuelve a validar al volver (RF-012, RNF-004).
"""

import re

import pytest
from fastapi.testclient import TestClient

from evaluador.adaptadores.web.app import crear_app
from evaluador.adaptadores.web.estado import EstadoInvalido, leer_respuestas, restaurar, serializar
from evaluador.casos_uso.diagnosticar import Diagnosticar
from evaluador.dominio.modelos import Diagnostico, DiagnosticoPropuesto, PreguntaPropuesta, ProblemaPropuesto
from tests.dobles.modelo_falso import ModeloFalso

PROMPT = "Escribe un correo para mi cliente."
ESPERADO = "Un correo cortés que explique un retraso de dos semanas."
DESTINATARIO = ProblemaPropuesto("ausencia", 3, None, "Tono del correo", "No dices el tono.", "media")
CONTEXTO = ProblemaPropuesto("ausencia", 2, None, "Motivo del retraso", "No dices qué ha pasado.", "alta")
PREGUNTAS = (PreguntaPropuesta("¿Qué tono quieres?", 1), PreguntaPropuesta("¿Por qué hay retraso?", 2))


def diagnostico_con_preguntas(preguntas: tuple[PreguntaPropuesta, ...] = PREGUNTAS) -> str:
    propuesta = DiagnosticoPropuesto((DESTINATARIO, CONTEXTO), preguntas, False)
    modelo = ModeloFalso(diagnostico=propuesta)
    app = crear_app(Diagnosticar(modelo), proveedor="falso", modelo="m")
    respuesta = TestClient(app).post(
        "/diagnosticar", data={"prompt": PROMPT, "resultado": ESPERADO, "idioma": "es"}
    )
    return respuesta.text


def diagnostico_de_dominio() -> Diagnostico:
    return Diagnosticar(
        ModeloFalso(diagnostico=DiagnosticoPropuesto((DESTINATARIO, CONTEXTO), PREGUNTAS, False))
    ).ejecutar(PROMPT, ESPERADO, idioma_interfaz="es")


def test_las_preguntas_se_muestran_y_cada_una_se_puede_dejar_en_blanco() -> None:
    """P2 / RF-007, RF-008: ninguna respuesta es obligatoria."""
    pagina = diagnostico_con_preguntas()
    assert "¿Qué tono quieres?" in pagina and "¿Por qué hay retraso?" in pagina
    campos = re.findall(r"<textarea[^>]*name=\"respuesta_Q\d\"[^>]*>", pagina)
    assert len(campos) == 2
    assert not any("required" in campo for campo in campos)


def test_como_maximo_se_muestran_5_preguntas() -> None:
    """RF-007."""
    pagina = diagnostico_con_preguntas(tuple(PreguntaPropuesta(f"¿Pregunta {i}?", 1) for i in range(8)))
    assert len(re.findall(r"name=\"respuesta_Q\d\"", pagina)) == 5


def test_responder_una_y_omitir_otra_deja_la_omitida_sin_respuesta() -> None:
    """RF-008 y RF-010: lo omitido no se inventa ni se rellena."""
    diagnostico = diagnostico_de_dominio()
    respuestas = leer_respuestas(diagnostico, {"respuesta_Q1": "Cordial", "respuesta_Q2": "   "})
    assert respuestas == {"Q1": "Cordial", "Q2": None}


def test_el_diagnostico_viaja_en_el_formulario_y_vuelve_identico() -> None:
    """RNF-009 (sin almacenamiento) y RF-012 (original intacto)."""
    diagnostico = diagnostico_de_dominio()
    assert restaurar(serializar(diagnostico)) == diagnostico
    assert 'name="estado"' in diagnostico_con_preguntas()


def test_un_estado_manipulado_se_rechaza() -> None:
    """RNF-004: al volver se valida otra vez; una cita inventada no pasa."""
    estado = serializar(diagnostico_de_dominio())
    manipulado = estado.replace('"fragmento": null', '"fragmento": "texto que no está"', 1).replace(
        '"tipo": "ausencia"', '"tipo": "texto"', 1
    )
    with pytest.raises(EstadoInvalido):
        restaurar(manipulado)
    with pytest.raises(EstadoInvalido):
        restaurar("no es json")


def test_el_texto_de_las_preguntas_se_muestra_escapado() -> None:
    """RNF-010."""
    pagina = diagnostico_con_preguntas((PreguntaPropuesta("<b>¿tono?</b>", 1),))
    assert "<b>¿tono?</b>" not in pagina and "&lt;b&gt;" in pagina
