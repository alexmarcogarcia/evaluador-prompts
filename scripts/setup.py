"""Prepara el entorno de desarrollo con un solo comando: python scripts/setup.py

1. Comprueba la versión de Python (la de .python-version).
2. Crea el entorno virtual .venv si no existe.
3. Instala el proyecto y las herramientas de desarrollo con las versiones fijadas.
4. Crea .env a partir de .env.example si no existe (sin valores reales).
"""

import io
import shutil
import subprocess
import sys
import venv

from _entorno import RAIZ, VENV, python_del_venv


def main() -> None:
    if isinstance(sys.stdout, io.TextIOWrapper):  # La consola de Windows usa cp1252 por defecto.
        sys.stdout.reconfigure(encoding="utf-8")
    esperada = (RAIZ / ".python-version").read_text(encoding="utf-8").strip()
    actual = f"{sys.version_info.major}.{sys.version_info.minor}"
    if actual != esperada:
        sys.exit(f"Hace falta Python {esperada} y se está usando {actual}.")

    if not python_del_venv().exists():
        print(f"Creando el entorno virtual en {VENV} ...")
        venv.create(VENV, with_pip=True)

    print("Instalando dependencias ...")
    pip = [str(python_del_venv()), "-m", "pip"]
    subprocess.run([*pip, "install", "--quiet", "--upgrade", "pip"], check=True)
    subprocess.run([*pip, "install", "--quiet", "-e", f"{RAIZ}[dev]"], check=True)

    env, ejemplo = RAIZ / ".env", RAIZ / ".env.example"
    if not env.exists():
        shutil.copy(ejemplo, env)
        print("Creado .env desde .env.example: añade tus claves de API.")

    print("\nListo. Comprueba que todo está en verde con:  python scripts/check.py")


if __name__ == "__main__":
    main()
