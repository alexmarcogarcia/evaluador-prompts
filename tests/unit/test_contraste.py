"""Paleta «Amarillo lápiz» en `static/sharpener.css` (T101, spec 002).

Verifica RNF-014 (contraste WCAG 2.2 AA ≥ 4,5:1 en cada par de la guía visual, en modo claro y oscuro),
RF-025 (los dos bloques oscuros, el automático y el del interruptor, son idénticos) y RF-024 (los
componentes solo usan tokens; los colores literales viven en los bloques de tokens).
"""

import re
from pathlib import Path

import pytest

WEB = Path(__file__).resolve().parents[2] / "src" / "evaluador" / "adaptadores" / "web"
CSS = (WEB / "static" / "sharpener.css").read_text(encoding="utf-8")

# Pares (texto, fondo) que la guía visual promete legibles.
PARES = [
    ("--tinta", "--hoja"),
    ("--tinta", "--fondo"),
    ("--tinta-suave", "--hoja"),
    ("--tinta-suave", "--velo"),
    ("--grafito", "--amarillo"),
    ("--sobre-accion", "--accion"),
    ("--error", "--hoja"),
    ("--tinta", "--velo"),
    ("--sobre-portada", "--portada"),
    ("--tinta", "--portada"),
]


def bloque(selector: str) -> dict[str, str]:
    """Tokens `--nombre: #hex` del primer bloque cuyo selector coincide exactamente."""
    inicio = CSS.index(selector + " {")
    cuerpo = CSS[inicio : CSS.index("}", inicio)]
    return dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{6})", cuerpo))


CLARO = bloque(":root")
OSCURO = {**CLARO, **bloque(':root[data-theme="dark"]')}


def luminancia(color: str) -> float:
    canales = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    lineal = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
    return 0.2126 * lineal[0] + 0.7152 * lineal[1] + 0.0722 * lineal[2]


def contraste(a: str, b: str) -> float:
    claro, oscuro = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (claro + 0.05) / (oscuro + 0.05)


@pytest.mark.parametrize(("texto", "fondo"), PARES)
@pytest.mark.parametrize("modo", ["claro", "oscuro"])
def test_cada_par_de_la_guia_cumple_el_contraste_aa(modo: str, texto: str, fondo: str) -> None:
    """RNF-014."""
    tokens = CLARO if modo == "claro" else OSCURO
    assert contraste(tokens[texto], tokens[fondo]) >= 4.5


def test_el_modo_oscuro_automatico_y_el_del_interruptor_son_iguales() -> None:
    """RF-025: el interruptor manda en los dos sentidos solo si los dos bloques coinciden."""
    automatico = re.search(r':root:not\(\[data-theme="light"\]\) \{(.*?)\}', CSS, flags=re.S)
    assert automatico is not None
    assert dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{6})", automatico.group(1))) == bloque(
        ':root[data-theme="dark"]'
    )


def test_los_componentes_no_usan_colores_literales() -> None:
    """RF-024: fuera de los bloques de tokens, todo color sale de un token."""
    sin_tokens = re.sub(r":root[^{]*\{[^}]*\}", "", CSS)
    assert re.findall(r"#[0-9a-fA-F]{3,8}\b", sin_tokens) == []


def test_la_plantilla_usa_la_hoja_de_estilos_y_no_lleva_estilos_propios() -> None:
    base = (WEB / "plantillas" / "base.html").read_text(encoding="utf-8")
    assert 'href="/static/sharpener.css?v={{ huella }}"' in base
    for plantilla in (WEB / "plantillas").rglob("*.html"):
        texto = plantilla.read_text(encoding="utf-8")
        assert "<style" not in texto and 'style="' not in texto, plantilla.name
