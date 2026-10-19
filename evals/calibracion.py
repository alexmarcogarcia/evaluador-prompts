"""Calibración del juez con las etiquetas de Àlex Marco (RNF-011, T054).

Las etiquetas viven en evals/calibracion/mejora-v1.md. El juez es fiable si coincide con ellas en
al menos 10 de 12 casos, en los dos niveles a la vez (dato inventado y requisito añadido).

Uso:  .venv/Scripts/python -m evals.calibracion
"""

import io
import json
import re
import sys

from evals.casos import RAIZ

ETIQUETAS = RAIZ / "evals" / "calibracion" / "mejora-v1.md"
VEREDICTOS = RAIZ / "evals" / "calibracion" / "veredictos-juez-v1.json"
MINIMO = 10
PLANTILLA = r"(?:\[sí/no\] *· *)?"

Etiqueta = tuple[bool, bool]  # (¿dato inventado?, ¿requisito añadido?)


def leer_etiquetas(md: str) -> dict[str, Etiqueta]:
    etiquetas: dict[str, Etiqueta] = {}
    for bloque in re.split(r"^### ", md, flags=re.M)[1:]:
        caso = re.search(r"· (C\d\d)", bloque.splitlines()[0])
        # Acepta «sí · …» y también «[sí/no] · sí» (respuesta escrita tras la plantilla).
        dato = re.search(rf"\*\*¿Dato inventado\?\*\* *{PLANTILLA}(sí|si|no)\b", bloque, flags=re.I)
        requisito = re.search(rf"\*\*¿Requisito añadido\?\*\* *{PLANTILLA}(sí|si|no)\b", bloque, flags=re.I)
        if caso and dato and requisito:
            etiquetas[caso.group(1)] = (dato.group(1).lower() != "no", requisito.group(1).lower() != "no")
    return etiquetas


def coincidencias(etiquetas: dict[str, Etiqueta], juez: dict[str, Etiqueta]) -> tuple[int, int]:
    """(casos en los que juez y persona coinciden en los dos niveles, casos etiquetados)."""
    comunes = [c for c in etiquetas if c in juez]
    return sum(etiquetas[c] == juez[c] for c in comunes), len(comunes)


def main() -> None:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    etiquetas = leer_etiquetas(ETIQUETAS.read_text(encoding="utf-8"))
    juez = {
        c: (bool(v[0]), bool(v[1])) for c, v in json.loads(VEREDICTOS.read_text(encoding="utf-8")).items()
    }
    iguales, total = coincidencias(etiquetas, juez)
    for caso in sorted(etiquetas):
        marca = "=" if etiquetas[caso] == juez.get(caso) else "≠"
        print(f"{caso}  persona {etiquetas[caso]}  {marca}  juez {juez.get(caso)}")
    veredicto = "FIABLE" if iguales >= MINIMO else "NO FIABLE"
    print(f"\nCoincidencia: {iguales}/{total} · {veredicto} (mínimo {MINIMO})")
    sys.exit(0 if iguales >= MINIMO else 1)


if __name__ == "__main__":
    main()
