"""Diferencias palabra a palabra entre el prompt original y el mejorado (RF-011, T053).

Devuelve tramos (texto, tipo) para que la plantilla los marque con <del>/<ins>; el texto siempre
pasa por el autoescape (RNF-010).
"""

import re
from difflib import SequenceMatcher

Tramo = tuple[str, str]  # (texto, "igual" | "quitado" | "anadido")


def _juntar(tramos: list[Tramo]) -> list[Tramo]:
    """Une tramos contiguos del mismo tipo; un espacio entre dos cambios pasa a formar parte del cambio."""
    tramos = [t for t in tramos if t[0]]
    for i in range(1, len(tramos) - 1):
        texto, tipo = tramos[i]
        if tipo == "igual" and not texto.strip() and tramos[i - 1][1] == tramos[i + 1][1] != "igual":
            tramos[i] = (texto, tramos[i - 1][1])
    juntos: list[Tramo] = []
    for texto, tipo in tramos:
        if juntos and juntos[-1][1] == tipo:
            juntos[-1] = (juntos[-1][0] + texto, tipo)
        elif texto:
            juntos.append((texto, tipo))
    return juntos


def comparar(original: str, mejorado: str) -> tuple[list[Tramo], list[Tramo]]:
    a, b = re.findall(r"\S+|\s+", original), re.findall(r"\S+|\s+", mejorado)
    izquierda: list[Tramo] = []
    derecha: list[Tramo] = []
    for operacion, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if operacion == "equal":
            izquierda.append(("".join(a[i1:i2]), "igual"))
            derecha.append(("".join(b[j1:j2]), "igual"))
        else:
            izquierda.append(("".join(a[i1:i2]), "quitado"))
            derecha.append(("".join(b[j1:j2]), "anadido"))
    return _juntar(izquierda), _juntar(derecha)
