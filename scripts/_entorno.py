"""Utilidades compartidas por los scripts del proyecto."""

import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VENV = RAIZ / ".venv"


def python_del_venv() -> Path:
    """Ruta al intérprete del entorno virtual del proyecto (Windows o Unix)."""
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"
