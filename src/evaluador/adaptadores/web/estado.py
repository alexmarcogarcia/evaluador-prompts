"""El diagnóstico viaja en el formulario, sin guardarse en ningún sitio (RNF-009, T041).

Al volver se reconstruye pasando otra vez por las reglas del dominio, así que un estado manipulado
no puede colar citas inventadas ni problemas fuera del catálogo (RNF-004, ADR-0003).
"""

import json
from collections.abc import Mapping

from evaluador.dominio import reglas
from evaluador.dominio.modelos import (
    Diagnostico,
    DiagnosticoPropuesto,
    PreguntaPropuesta,
    ProblemaPropuesto,
    Prompt,
)


class EstadoInvalido(Exception):
    """El estado recibido no reconstruye un diagnóstico válido."""


def serializar(diagnostico: Diagnostico) -> str:
    return json.dumps(
        {
            "prompt": diagnostico.prompt.texto,
            "resultado": diagnostico.prompt.resultado_esperado,
            "rechazado": diagnostico.rechazado,
            "problemas": [
                {
                    "tipo": p.tipo.value,
                    "categoria": p.categoria.value,
                    "fragmento": p.fragmento,
                    "falta": p.falta,
                    "explicacion": p.explicacion,
                    "gravedad": p.gravedad.value,
                }
                for p in diagnostico.problemas
            ],
            # Los problemas se numeran P1, P2… en orden: la posición se deduce del identificador.
            "preguntas": [
                {"texto": q.texto, "problema": int(q.problema_id[1:])} for q in diagnostico.preguntas
            ],
        },
        ensure_ascii=False,
    )


def restaurar(estado: str) -> Diagnostico:
    try:
        datos = json.loads(estado)
        prompt = Prompt(texto=str(datos["prompt"]), resultado_esperado=str(datos["resultado"]))
        propuesta = DiagnosticoPropuesto(
            problemas=tuple(
                ProblemaPropuesto(
                    str(p["tipo"]),
                    int(p["categoria"]),
                    p["fragmento"],
                    p["falta"],
                    str(p["explicacion"]),
                    str(p["gravedad"]),
                )
                for p in datos["problemas"]
            ),
            preguntas=tuple(
                PreguntaPropuesta(str(q["texto"]), int(q["problema"])) for q in datos["preguntas"]
            ),
            rechazado=bool(datos["rechazado"]),
        )
    except (ValueError, KeyError, TypeError) as error:
        raise EstadoInvalido from error
    depurado = reglas.depurar_diagnostico(prompt, propuesta)
    if depurado.descartados or len(depurado.diagnostico.preguntas) != len(propuesta.preguntas):
        raise EstadoInvalido
    return depurado.diagnostico


def leer_respuestas(diagnostico: Diagnostico, formulario: Mapping[str, str]) -> dict[str, str | None]:
    """Pregunta -> respuesta; una respuesta en blanco es una pregunta omitida (None), nunca se inventa."""
    respuestas: dict[str, str | None] = {}
    for pregunta in diagnostico.preguntas:
        texto = formulario.get(f"respuesta_{pregunta.id}", "").strip()
        respuestas[pregunta.id] = texto or None
    return respuestas
