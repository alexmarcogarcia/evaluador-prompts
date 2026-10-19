"""Comparación palabra a palabra entre el original y el mejorado (T053, RF-011)."""

from evaluador.adaptadores.web.comparacion import comparar


def test_marca_lo_quitado_en_el_original_y_lo_anadido_en_el_mejorado() -> None:
    original, mejorado = comparar("Escribe algo bonito.", "Escribe un poema de 12 versos.")
    assert ("Escribe ", "igual") in original and ("algo bonito.", "quitado") in original
    assert ("un poema de 12 versos.", "anadido") in mejorado


def test_reconstruye_los_dos_textos_sin_perder_nada() -> None:
    a, b = "Hola, ¿qué tal?\nAdiós.", "Hola, buenos días.\nAdiós y gracias."
    original, mejorado = comparar(a, b)
    assert "".join(t for t, _ in original) == a
    assert "".join(t for t, _ in mejorado) == b
