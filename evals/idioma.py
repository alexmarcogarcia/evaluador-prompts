"""Las evals usan la misma detección de idioma que la app (RF-013)."""

from evaluador.dominio.idioma import detectar

__all__ = ["detectar"]
