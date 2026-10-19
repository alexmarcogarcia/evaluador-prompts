"""Prueba de humo del harness: el paquete se instala y se importa."""

import evaluador


def test_el_paquete_se_importa() -> None:
    assert evaluador.__version__ == "0.1.0"
