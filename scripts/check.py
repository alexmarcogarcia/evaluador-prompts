"""Ejecuta todas las comprobaciones de la definición de hecho: python scripts/check.py

Es el mismo conjunto que ejecuta la CI. Termina con error si cualquiera falla.
"""

import io
import subprocess
import sys

from _entorno import RAIZ, python_del_venv

COMPROBACIONES = [
    ("Linter", ["-m", "ruff", "check", "."]),
    ("Formato", ["-m", "ruff", "format", "--check", "."]),
    ("Tipos", ["-m", "mypy"]),
    ("Pruebas", ["-m", "pytest", "-q"]),
    ("Coherencia spec ↔ tareas ↔ pruebas", ["scripts/coherencia.py"]),
    # Solo dependencias del proyecto, no las del sistema (constitución: dependencias y licencias).
    ("Dependencias vulnerables", ["-m", "pip_audit", "--skip-editable", "--progress-spinner", "off"]),
]


def main() -> None:
    if isinstance(sys.stdout, io.TextIOWrapper):  # La consola de Windows usa cp1252 por defecto.
        sys.stdout.reconfigure(encoding="utf-8")
    python = python_del_venv()
    if not python.exists():
        sys.exit("No existe .venv. Ejecuta primero:  python scripts/setup.py")
    fallos = []
    for nombre, argumentos in COMPROBACIONES:
        print(f"\n=== {nombre}")
        if subprocess.run([str(python), *argumentos], cwd=RAIZ).returncode != 0:
            fallos.append(nombre)
    print("\n" + ("✅ Todo en verde." if not fallos else f"❌ Fallan: {', '.join(fallos)}"))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
