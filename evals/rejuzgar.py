"""Recalibra un juez nuevo con las mismas 12 mejoras y las etiquetas ya decididas (RNF-011).

Sirve cuando el juez cambia (por ejemplo, porque el proveedor retira el modelo, riesgo R-01): no
hace falta volver a etiquetar, solo comparar los veredictos del juez nuevo con las decisiones de
Àlex Marco.

Uso:  .venv/Scripts/python -m evals.rejuzgar --modelo openai/gpt-oss-20b
"""

import argparse
import io
import json
import os
import sys

from dotenv import load_dotenv

from evals.calibracion import ETIQUETAS, MINIMO, REVISION, coincidencias, leer_etiquetas
from evals.casos import RAIZ
from evals.juez import Juez

MEJORAS = RAIZ / "evals" / "resultados" / "2026-10-19_mejora_calibracion.json"


def main() -> None:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    argumentos = argparse.ArgumentParser()
    argumentos.add_argument("--modelo", required=True)
    opciones = argumentos.parse_args()

    load_dotenv(RAIZ / ".env")
    juez = Juez(os.environ.get("NVIDIA_API_KEY", ""), modelo=opciones.modelo)
    etiquetas = leer_etiquetas(ETIQUETAS.read_text(encoding="utf-8"))
    if REVISION.exists():
        etiquetas |= leer_etiquetas(REVISION.read_text(encoding="utf-8"))

    veredictos: dict[str, tuple[bool, bool]] = {}
    for fila in json.loads(MEJORAS.read_text(encoding="utf-8"))["casos"]:
        if "mejorado" not in fila:
            continue
        try:
            v = juez.juzgar(str(fila["prompt"]), str(fila["resultado"]), "", str(fila["mejorado"]))
        except Exception as error:  # noqa: BLE001  # Un juez que falla no cuenta como coincidencia.
            print(f"{fila['caso']}  ERROR del juez: {type(error).__name__}")
            continue
        caso = str(fila["caso"])
        veredictos[caso] = (v.inventa_datos, v.anade_requisitos)
        marca = "=" if etiquetas.get(caso) == veredictos[caso] else "≠"
        print(f"{caso}  persona {etiquetas.get(caso)}  {marca}  juez {veredictos[caso]}")

    nombre = opciones.modelo.replace("/", "__")
    salida = ETIQUETAS.parent / f"veredictos-juez-v1_{nombre}.json"
    salida.write_text(json.dumps(veredictos, indent=2), encoding="utf-8")
    iguales, total = coincidencias(etiquetas, veredictos)
    veredicto = "FIABLE" if iguales >= MINIMO else "NO FIABLE"
    print(f"\nCoincidencia: {iguales}/{total} · {veredicto} (mínimo {MINIMO})")


if __name__ == "__main__":
    main()
