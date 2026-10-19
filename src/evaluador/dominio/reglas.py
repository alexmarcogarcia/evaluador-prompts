"""Reglas que el código garantiza sin confiar en el modelo (ADR-0003, decisión 2).

Todo lo que la spec exige con carácter absoluto se comprueba aquí: lo que no cumple se descarta,
nunca se muestra como válido.
"""

from dataclasses import dataclass

from evaluador.dominio.modelos import (
    Cambio,
    Categoria,
    Diagnostico,
    DiagnosticoPropuesto,
    Gravedad,
    MejoraPropuesta,
    Pregunta,
    Problema,
    ProblemaPropuesto,
    Prompt,
    TipoProblema,
    VersionMejorada,
)

LONGITUD_MAXIMA = 8000
MAX_PREGUNTAS = 5


@dataclass(frozen=True)
class Depuracion:
    diagnostico: Diagnostico
    descartados: int
    """Problemas de la propuesta que no cumplían las reglas (se registra la cifra, nunca el texto)."""


def caracteres_sobrantes(texto: str) -> int:
    return max(0, len(texto) - LONGITUD_MAXIMA)


def _validar_problema(prompt: Prompt, propuesto: ProblemaPropuesto, ident: str) -> Problema | None:
    try:
        problema = Problema(
            id=ident,
            tipo=TipoProblema(propuesto.tipo),
            categoria=Categoria(propuesto.categoria),
            explicacion=propuesto.explicacion,
            gravedad=Gravedad(propuesto.gravedad),
            fragmento=propuesto.fragmento,
            falta=propuesto.falta,
        )
    except ValueError:
        return None
    if problema.fragmento is not None and problema.fragmento not in prompt.texto:
        return None  # Una cita que no es literal nunca se muestra.
    return problema


def depurar_diagnostico(prompt: Prompt, propuesta: DiagnosticoPropuesto) -> Depuracion:
    if propuesta.rechazado:
        return Depuracion(Diagnostico(prompt=prompt, problemas=(), preguntas=(), rechazado=True), 0)

    validos: list[Problema] = []
    id_por_posicion: dict[int, str] = {}
    for posicion, propuesto in enumerate(propuesta.problemas, start=1):
        problema = _validar_problema(prompt, propuesto, f"P{len(validos) + 1}")
        if problema is not None:
            validos.append(problema)
            id_por_posicion[posicion] = problema.id

    preguntas: list[Pregunta] = []
    for propuesta_pregunta in propuesta.preguntas:
        problema_id = id_por_posicion.get(propuesta_pregunta.problema)
        if problema_id is not None and propuesta_pregunta.texto.strip() and len(preguntas) < MAX_PREGUNTAS:
            preguntas.append(Pregunta(f"Q{len(preguntas) + 1}", propuesta_pregunta.texto, problema_id))

    diagnostico = Diagnostico(prompt=prompt, problemas=tuple(validos), preguntas=tuple(preguntas))
    return Depuracion(diagnostico, descartados=len(propuesta.problemas) - len(validos))


def depurar_mejora(diagnostico: Diagnostico, propuesta: MejoraPropuesta) -> VersionMejorada:
    existentes = {p.id for p in diagnostico.problemas}
    cambios = tuple(
        Cambio(explicacion, ids)
        for explicacion, ids in propuesta.cambios
        if ids and set(ids) <= existentes and explicacion.strip()
    )
    return VersionMejorada(original=diagnostico.prompt, texto=propuesta.texto, cambios=cambios)
