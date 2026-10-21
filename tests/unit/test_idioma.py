"""Detección del idioma de un texto (RF-013), usada por la mejora y por las evals."""

from evaluador.dominio.idioma import detectar


def test_detecta_los_4_idiomas_de_la_interfaz() -> None:
    assert detectar("Escribe un artículo para el blog de mi instituto, dirigido a los alumnos.") == "es"
    assert detectar("Escriu un article per al blog de l'institut, adreçat als alumnes.") == "ca"
    assert detectar("Write an article for the school blog, aimed at the students.") == "en"
    assert detectar("Schreib einen Artikel für den Blog der Schule, der sich an die Schüler richtet.") == "de"


def test_ignora_los_marcadores_completar_que_van_en_el_idioma_de_la_interfaz() -> None:
    texto = "Rewrite my cover letter, keeping it under one page. [COMPLETAR: pega aquí el texto de tu carta]"
    assert detectar(texto) == "en"


def test_un_texto_sin_palabras_reconocibles_no_tiene_idioma() -> None:
    assert detectar("hola") is None or detectar("") is None
    assert detectar("") is None


def test_un_empate_entre_espanol_y_catalan_no_se_adivina() -> None:
    """Prompt corto con palabras comunes a los dos idiomas: mejor «no lo sé» que equivocarse."""
    assert detectar("Fes una llista de la compra.") is None


def test_con_mas_texto_el_empate_se_resuelve() -> None:
    texto = "Fes una llista de la compra. La llista per a un sopar vegà per a 6 persones, amb les seccions."
    assert detectar(texto) == "ca"
