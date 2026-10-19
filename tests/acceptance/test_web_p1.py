"""Aceptación de P1 en la interfaz web (T032, T033, T034).

Verifica RF-006 (proveedor, modelo y aviso antes de enviar), RF-013 (los 4 idiomas), RF-014 (errores
en lenguaje llano conservando lo escrito), RNF-008 (solo 127.0.0.1), RNF-009 (sin escrituras a disco)
y RNF-010 (todo texto del usuario o del modelo se muestra escapado).
"""

import json
from pathlib import Path

import pytest
import uvicorn
from fastapi.testclient import TestClient

from evaluador import composicion
from evaluador.adaptadores.web.app import crear_app
from evaluador.casos_uso.diagnosticar import Diagnosticar
from evaluador.dominio.modelos import DiagnosticoPropuesto, ProblemaPropuesto
from evaluador.puertos.modelo_ia import ErrorProveedor, TipoError
from tests.dobles.modelo_falso import ModeloFalso

I18N = Path(composicion.__file__).parent / "adaptadores" / "web" / "i18n"
PROMPT = "Escríbeme algo que esté bien."
ESPERADO = "Un artículo de 500 palabras."
VAGO = ProblemaPropuesto("texto", 9, "que esté bien", None, "«Bien» no dice qué quieres.", "alta")


def cliente(modelo: ModeloFalso | None = None) -> TestClient:
    modelo = modelo or ModeloFalso(diagnostico=DiagnosticoPropuesto((VAGO,), (), False))
    return TestClient(crear_app(Diagnosticar(modelo), proveedor=modelo.proveedor, modelo=modelo.modelo))


def enviar(c: TestClient, prompt: str = PROMPT, esperado: str = ESPERADO, idioma: str = "es") -> str:
    respuesta = c.post("/diagnosticar", data={"prompt": prompt, "resultado": esperado, "idioma": idioma})
    assert respuesta.status_code == 200
    return respuesta.text


def textos(idioma: str) -> dict[str, str]:
    datos: dict[str, str] = json.loads((I18N / f"{idioma}.json").read_text(encoding="utf-8"))
    return datos


def test_antes_de_enviar_se_ven_proveedor_modelo_y_aviso_de_datos() -> None:
    """RF-006."""
    pagina = cliente().get("/").text
    assert "falso" in pagina and "modelo-de-prueba" in pagina
    assert "datos personales" in pagina


@pytest.mark.parametrize("idioma", ["es", "ca", "en", "de"])
def test_la_interfaz_esta_en_los_4_idiomas(idioma: str) -> None:
    """RF-013: cada idioma usa sus propios textos, también en el diagnóstico."""
    c = cliente()
    assert textos(idioma)["titulo"] in c.get(f"/?idioma={idioma}").text
    assert textos(idioma)["cat_9"] in enviar(c, idioma=idioma)


def test_los_4_idiomas_tienen_exactamente_las_mismas_claves() -> None:
    """RF-013 (T033)."""
    claves = {idioma: set(textos(idioma)) for idioma in ("es", "ca", "en", "de")}
    assert claves["ca"] == claves["en"] == claves["de"] == claves["es"]


def test_el_diagnostico_muestra_el_problema_y_marca_el_fragmento() -> None:
    """P1 / RF-003."""
    pagina = enviar(cliente())
    assert "«Bien» no dice qué quieres." in pagina.replace("&#171;", "«").replace("&#187;", "»")
    assert "<mark>que esté bien</mark>" in pagina


def test_un_prompt_sin_problemas_lo_dice() -> None:
    """RF-005."""
    assert textos("es")["sin_problemas"] in enviar(cliente(ModeloFalso()))


def test_el_texto_del_usuario_y_del_modelo_se_muestra_escapado() -> None:
    """RNF-010: nada se interpreta como HTML."""
    malicioso = "<script>alert(1)</script>"
    modelo = ModeloFalso(
        diagnostico=DiagnosticoPropuesto(
            (ProblemaPropuesto("texto", 9, malicioso, None, malicioso, "alta"),), (), False
        )
    )
    pagina = enviar(cliente(modelo), prompt=f"Hola {malicioso}")
    assert "<script>alert(1)</script>" not in pagina
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in pagina


def test_sin_resultado_esperado_se_pide_y_se_conserva_el_prompt() -> None:
    """RF-002 / RF-014: lo escrito no se pierde."""
    pagina = enviar(cliente(), esperado="")
    assert textos("es")["error_falta_resultado"] in pagina
    assert PROMPT in pagina


def test_un_prompt_demasiado_largo_indica_cuanto_sobra() -> None:
    """RF-001."""
    pagina = enviar(cliente(), prompt="a" * 8003)
    assert textos("es")["error_demasiado_largo"].replace("{n}", "3") in pagina


def test_un_limite_de_uso_se_explica_y_se_puede_reintentar_sin_reescribir() -> None:
    """RF-014."""
    modelo = ModeloFalso(error=ErrorProveedor(TipoError.LIMITE_DE_USO, reintentar_en_s=7))
    pagina = enviar(cliente(modelo))
    assert textos("es")["error_limite_de_uso"] in pagina
    assert textos("es")["reintentar_en"].replace("{s}", "7") in pagina
    assert PROMPT in pagina and ESPERADO in pagina


def test_el_servidor_solo_escucha_en_el_propio_equipo(monkeypatch: pytest.MonkeyPatch) -> None:
    """RNF-008."""
    llamadas: list[dict[str, object]] = []
    monkeypatch.setattr(uvicorn, "run", lambda app, **kw: llamadas.append(kw))
    monkeypatch.setattr(composicion, "construir_app", lambda: object())
    composicion.main()
    assert llamadas[0]["host"] == "127.0.0.1"


def test_un_diagnostico_no_escribe_nada_en_disco(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """RNF-009."""
    monkeypatch.chdir(tmp_path)
    enviar(cliente())
    assert list(tmp_path.iterdir()) == []
