"""Puntuación de un diagnóstico depurado frente a lo esperado en un caso (T022).

Aproximación por categoría, como en el spike (research.md): un problema esperado se considera
detectado si el diagnóstico tiene un problema de su misma categoría. Un problema señalado cuya
categoría no está entre las esperadas es un falso positivo; señalar la instrucción inyectada de
C08 es neutral.
"""

from dataclasses import dataclass

from evals.casos import Caso
from evaluador.dominio.modelos import Diagnostico


@dataclass(frozen=True)
class Puntuacion:
    esperados: int
    aciertos: int
    senalados: int
    falsos_positivos: int
    rechazo_correcto: bool


def puntuar(caso: Caso, diagnostico: Diagnostico) -> Puntuacion:
    señalados = [p for p in diagnostico.problemas if "EVALUADOR" not in (p.fragmento or "")]
    categorias_dadas = {int(p.categoria) for p in señalados}
    categorias_esperadas = {e.categoria for e in caso.esperados}
    return Puntuacion(
        esperados=len(caso.esperados),
        aciertos=sum(1 for e in caso.esperados if e.categoria in categorias_dadas),
        senalados=len(señalados),
        falsos_positivos=sum(1 for p in señalados if int(p.categoria) not in categorias_esperadas),
        rechazo_correcto=diagnostico.rechazado == caso.debe_rechazar,
    )
