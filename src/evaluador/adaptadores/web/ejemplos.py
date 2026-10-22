"""Ejemplos de la pantalla inicial (T150, RF-021).

Cuatro prompts típicos por idioma de la interfaz, sintéticos y con problemas distintos que la app sabe
señalar: falta de datos, material ausente, destinatario y palabras vagas. Sirven para probar la app en
segundos sin saber qué escribir.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Ejemplo:
    etiqueta: str
    prompt: str


EJEMPLOS: dict[str, tuple[Ejemplo, ...]] = {
    "es": (
        Ejemplo("Correo al jefe", "Escríbele un correo a mi jefe para pedirle unos días de vacaciones."),
        Ejemplo("Resumir un texto", "Resume este artículo de forma clara."),
        Ejemplo("Ideas para una fiesta", "Dame ideas para el cumpleaños de mi hija."),
        Ejemplo("Presentación", "Hazme una presentación sobre el cambio climático que quede bien."),
    ),
    "ca": (
        Ejemplo("Correu al cap", "Escriu un correu al meu cap per demanar-li uns dies de vacances."),
        Ejemplo("Resumir un text", "Resumeix aquest article de manera clara."),
        Ejemplo("Idees per a una festa", "Dona'm idees per a l'aniversari de la meva filla."),
        Ejemplo("Presentació", "Fes-me una presentació sobre el canvi climàtic que quedi bé."),
    ),
    "en": (
        Ejemplo("Email to your boss", "Write an email to my boss asking for a few days off."),
        Ejemplo("Summarise a text", "Summarise this article clearly."),
        Ejemplo("Party ideas", "Give me ideas for my daughter's birthday."),
        Ejemplo("Presentation", "Make me a nice presentation about climate change."),
    ),
    "de": (
        Ejemplo(
            "E-Mail an die Chefin",
            "Schreib eine E-Mail an meine Chefin, in der ich um ein paar Tage Urlaub bitte.",
        ),
        Ejemplo("Text zusammenfassen", "Fass diesen Artikel verständlich zusammen."),
        Ejemplo("Ideen für eine Feier", "Gib mir Ideen für den Geburtstag meiner Tochter."),
        Ejemplo("Präsentation", "Mach mir eine schöne Präsentation über den Klimawandel."),
    ),
}


def ejemplo(idioma: str, posicion: str) -> Ejemplo | None:
    """El ejemplo elegido, o None si la posición no es válida."""
    ejemplos = EJEMPLOS.get(idioma, EJEMPLOS["es"])
    return ejemplos[int(posicion)] if posicion.isdigit() and int(posicion) < len(ejemplos) else None
