"""Prompts de sistema versionados (ADR-0003, decisión 5).

Viven como archivos de texto, no dentro del código, y cualquier cambio pasa por las evals.
"""

from importlib.resources import files


def cargar(nombre: str) -> str:
    """Devuelve el prompt `<nombre>.md` de este paquete."""
    return files(__package__).joinpath(f"{nombre}.md").read_text(encoding="utf-8")
