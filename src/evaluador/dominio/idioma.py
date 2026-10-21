"""Detección aproximada del idioma de un texto (RF-013).

Cuenta palabras funcionales frecuentes de cada idioma de la interfaz. Basta para comprobar que la
versión mejorada sigue en el idioma del prompt original; no es un detector general. Sin dependencias.
"""

import re

PALABRAS = {
    "es": {
        "el",
        "la",
        "los",
        "las",
        "de",
        "del",
        "que",
        "y",
        "en",
        "un",
        "una",
        "para",
        "con",
        "por",
        "es",
        "mi",
        "tu",
        "su",
        "al",
        "lo",
        "como",
        "sobre",
        "dirigido",
    },
    "ca": {
        "el",
        "la",
        "els",
        "les",
        "de",
        "del",
        "que",
        "i",
        "en",
        "un",
        "una",
        "per",
        "amb",
        "és",
        "meu",
        "teu",
        "seu",
        "al",
        "als",
        "com",
        "sobre",
        "l",
        "d",
        "adreçat",
    },
    "en": {
        "the",
        "of",
        "and",
        "to",
        "a",
        "in",
        "for",
        "with",
        "is",
        "my",
        "your",
        "on",
        "at",
        "that",
        "it",
        "as",
        "about",
        "an",
        "aimed",
    },
    "de": {
        "der",
        "die",
        "das",
        "den",
        "dem",
        "und",
        "zu",
        "ein",
        "eine",
        "einen",
        "für",
        "mit",
        "ist",
        "mein",
        "dein",
        "von",
        "im",
        "auf",
        "an",
        "sich",
        "nicht",
        "schule",
    },
}
EXCLUSIVAS = {
    "es": {"los", "las", "y", "para", "con", "por", "mi", "lo", "como", "dirigido"},
    "ca": {"els", "les", "i", "per", "amb", "meu", "als", "com", "adreçat"},
}


def detectar(texto: str) -> str | None:
    # Los marcadores [COMPLETAR: …] van en el idioma de la interfaz, no en el del prompt: no cuentan.
    texto = re.sub(r"\[COMPLETAR:[^\]]*\]", " ", texto)
    palabras = re.findall(r"[a-zà-ÿß]+", texto.lower())
    if not palabras:
        return None
    puntos = {idioma: sum(p in lista for p in palabras) for idioma, lista in PALABRAS.items()}
    # Español y catalán comparten muchas palabras: desempata con las que solo usa cada uno.
    if puntos["es"] and puntos["ca"]:
        puntos["es"] += 2 * sum(p in EXCLUSIVAS["es"] for p in palabras)
        puntos["ca"] += 2 * sum(p in EXCLUSIVAS["ca"] for p in palabras)
    ordenados = sorted(puntos.values(), reverse=True)
    if not ordenados[0] or ordenados[0] == ordenados[1]:
        return None  # Sin señal o empate: mejor «no lo sé» que equivocarse.
    return max(puntos, key=lambda idioma: puntos[idioma])
