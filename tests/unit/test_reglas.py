"""Reglas que el código garantiza sin confiar en el modelo (T012, ADR-0003 decisión 2).

Verifica RF-001 (longitud), RF-007 (máximo de preguntas), RF-009 (cambios ligados a problemas
existentes) y RNF-004 (citas literales).
"""

from evaluador.dominio import reglas
from evaluador.dominio.modelos import (
    Categoria,
    DiagnosticoPropuesto,
    MejoraPropuesta,
    PreguntaPropuesta,
    ProblemaPropuesto,
    Prompt,
    TipoProblema,
)

PROMPT = Prompt(texto="Escríbeme algo sobre el clima que esté bien.")


def propuesto(**cambios: object) -> ProblemaPropuesto:
    datos: dict[str, object] = {
        "tipo": "texto",
        "categoria": 9,
        "fragmento": "que esté bien",
        "falta": None,
        "explicacion": "Es subjetivo.",
        "gravedad": "alta",
    }
    datos.update(cambios)
    return ProblemaPropuesto(**datos)  # type: ignore[arg-type]


def depurar(
    *problemas: ProblemaPropuesto, preguntas: tuple[PreguntaPropuesta, ...] = ()
) -> reglas.Depuracion:
    return reglas.depurar_diagnostico(
        PROMPT, DiagnosticoPropuesto(problemas=problemas, preguntas=preguntas, rechazado=False)
    )


def test_longitud_maxima_8000_caracteres() -> None:
    """RF-001: 8.000 se acepta; 8.001 sobra 1 carácter."""
    assert reglas.caracteres_sobrantes("a" * 8000) == 0
    assert reglas.caracteres_sobrantes("a" * 8001) == 1


def test_un_problema_valido_pasa_la_depuracion() -> None:
    resultado = depurar(propuesto())
    assert [p.categoria for p in resultado.diagnostico.problemas] == [Categoria.VAGUEDAD_LEXICA]
    assert resultado.descartados == 0


def test_se_descarta_una_cita_que_no_existe_literalmente_en_el_prompt() -> None:
    """RNF-004: nunca se cita un fragmento que no está en el prompt."""
    resultado = depurar(propuesto(fragmento="que quede bonito"))
    assert resultado.diagnostico.problemas == ()
    assert resultado.descartados == 1


def test_se_descartan_categoria_fuera_de_catalogo_y_tipo_desconocido() -> None:
    """RF-004: catálogo cerrado."""
    resultado = depurar(propuesto(categoria=10), propuesto(tipo="otro"), propuesto(gravedad="enorme"))
    assert resultado.diagnostico.problemas == ()
    assert resultado.descartados == 3


def test_se_descarta_un_problema_incoherente_con_su_tipo() -> None:
    """Constitución 1.1: «por ausencia» no cita fragmento."""
    resultado = depurar(propuesto(tipo="ausencia", falta="Para quién es"))
    assert resultado.descartados == 1


def test_los_problemas_validos_reciben_identificadores_correlativos() -> None:
    ausencia = propuesto(tipo="ausencia", categoria=3, fragmento=None, falta="Para quién es")
    resultado = depurar(propuesto(), propuesto(categoria=10), ausencia)
    assert [p.id for p in resultado.diagnostico.problemas] == ["P1", "P2"]
    assert resultado.diagnostico.problemas[1].tipo is TipoProblema.POR_AUSENCIA


def test_como_maximo_5_preguntas() -> None:
    """RF-007."""
    resultado = depurar(
        propuesto(), preguntas=tuple(PreguntaPropuesta(f"¿Pregunta {i}?", 1) for i in range(7))
    )
    assert len(resultado.diagnostico.preguntas) == 5


def test_un_rechazo_descarta_problemas_y_preguntas() -> None:
    """RF-015."""
    resultado = reglas.depurar_diagnostico(
        PROMPT,
        DiagnosticoPropuesto(
            problemas=(propuesto(),), preguntas=(PreguntaPropuesta("¿?", 1),), rechazado=True
        ),
    )
    assert resultado.diagnostico.rechazado
    assert resultado.diagnostico.problemas == ()
    assert resultado.diagnostico.preguntas == ()


def test_se_descartan_cambios_que_no_enlazan_problemas_existentes() -> None:
    """RF-009: cada cambio referencia problemas que existen."""
    diagnostico = depurar(propuesto()).diagnostico
    mejora = MejoraPropuesta(
        texto="Escribe un artículo de 500 palabras.",
        cambios=(("Concreto la longitud.", ("P1",)), ("Cambio inventado.", ("P9",)), ("Sin vínculo.", ())),
    )
    version = reglas.depurar_mejora(diagnostico, mejora)
    assert [c.problema_ids for c in version.cambios] == [("P1",)]
    assert version.original is PROMPT


def test_cada_pregunta_queda_ligada_al_identificador_de_su_problema() -> None:
    """RF-007: la pregunta apunta al problema por su posición en la propuesta del modelo."""
    ausencia = propuesto(tipo="ausencia", categoria=3, fragmento=None, falta="Para quién es")
    resultado = depurar(propuesto(), ausencia, preguntas=(PreguntaPropuesta("¿Para quién es?", 2),))
    assert [(q.id, q.problema_id) for q in resultado.diagnostico.preguntas] == [("Q1", "P2")]


def test_se_descarta_una_pregunta_ligada_a_un_problema_descartado_o_inexistente() -> None:
    """RF-007: sin problema válido, la pregunta no tiene motivo."""
    preguntas = (PreguntaPropuesta("¿Inventada?", 1), PreguntaPropuesta("¿Fuera?", 9))
    resultado = depurar(propuesto(fragmento="no existe"), preguntas=preguntas)
    assert resultado.diagnostico.preguntas == ()
