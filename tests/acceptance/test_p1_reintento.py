"""Aceptación de la historia P1 (spec 002) · reintento automático (T110).

Verifica RF-018: si la IA devuelve una respuesta inválida, se reintenta una vez sin que el usuario lo
note; si vuelve a fallar, el usuario ve el error y conserva su texto (RF-014); los demás errores no se
reintentan, porque alargarían la espera.
"""

import pytest
from fastapi.testclient import TestClient

from evaluador.adaptadores.web.app import crear_app
from evaluador.casos_uso.diagnosticar import Diagnosticar
from evaluador.casos_uso.mejorar import Mejorar
from evaluador.dominio.modelos import DiagnosticoPropuesto, MejoraPropuesta, ProblemaPropuesto
from evaluador.puertos.modelo_ia import ErrorProveedor, TipoError
from tests.dobles.modelo_falso import ModeloFalso

PROMPT = "Escríbeme algo que esté bien."
ESPERADO = "Un artículo de 500 palabras."
VAGO = ProblemaPropuesto("texto", 9, "que esté bien", None, "«Bien» no dice qué quieres.", "alta")
DIAGNOSTICO = DiagnosticoPropuesto((VAGO,), (), False)


def invalida() -> ErrorProveedor:
    return ErrorProveedor(TipoError.RESPUESTA_INVALIDA)


def llamadas(modelo: ModeloFalso, operacion: str) -> int:
    return sum(1 for llamada in modelo.llamadas if llamada[0] == operacion)


def test_una_respuesta_invalida_se_reintenta_y_el_usuario_ve_el_diagnostico() -> None:
    """RF-018."""
    modelo = ModeloFalso(diagnostico=DIAGNOSTICO, fallos=(invalida(),))
    diagnostico = Diagnosticar(modelo).ejecutar(PROMPT, ESPERADO, idioma_interfaz="es")
    assert [p.fragmento for p in diagnostico.problemas] == ["que esté bien"]
    assert llamadas(modelo, "diagnosticar") == 2


def test_dos_respuestas_invalidas_seguidas_llegan_como_error() -> None:
    """RF-018: un solo reintento; después, el error en lenguaje llano (RF-014)."""
    modelo = ModeloFalso(diagnostico=DIAGNOSTICO, fallos=(invalida(), invalida()))
    with pytest.raises(ErrorProveedor) as fallo:
        Diagnosticar(modelo).ejecutar(PROMPT, ESPERADO, idioma_interfaz="es")
    assert fallo.value.tipo is TipoError.RESPUESTA_INVALIDA
    assert llamadas(modelo, "diagnosticar") == 2


@pytest.mark.parametrize("tipo", [TipoError.NO_DISPONIBLE, TipoError.TIEMPO_AGOTADO, TipoError.LIMITE_DE_USO])
def test_los_demas_errores_no_se_reintentan(tipo: TipoError) -> None:
    """RF-018: si el servicio no está o tarda, reintentar solo alarga la espera."""
    modelo = ModeloFalso(diagnostico=DIAGNOSTICO, fallos=(ErrorProveedor(tipo),))
    with pytest.raises(ErrorProveedor):
        Diagnosticar(modelo).ejecutar(PROMPT, ESPERADO, idioma_interfaz="es")
    assert llamadas(modelo, "diagnosticar") == 1


def test_la_mejora_tambien_se_reintenta_ante_una_respuesta_invalida() -> None:
    """RF-018."""
    modelo = ModeloFalso(diagnostico=DIAGNOSTICO, mejora=MejoraPropuesta("Escribe un artículo.", ()))
    diagnostico = Diagnosticar(modelo).ejecutar(PROMPT, ESPERADO, idioma_interfaz="es")
    modelo.fallos.append(invalida())  # El fallo llega en la mejora, no en el diagnóstico.
    version = Mejorar(modelo).ejecutar(diagnostico, {}, "es")
    assert version.texto == "Escribe un artículo."
    assert llamadas(modelo, "mejorar") == 2


def test_en_la_web_un_fallo_puntual_no_llega_al_usuario() -> None:
    """RF-018 de extremo a extremo: el usuario ve el diagnóstico, no el error."""
    modelo = ModeloFalso(diagnostico=DIAGNOSTICO, fallos=(invalida(),))
    app = crear_app(Diagnosticar(modelo), Mejorar(modelo), proveedor="falso", modelo="m")
    pagina = TestClient(app).post("/diagnosticar", data={"prompt": PROMPT, "resultado": ESPERADO}).text
    assert "<mark>que esté bien</mark>" in pagina
    assert "no hem pogut entendre" not in pagina and "no hemos podido entender" not in pagina
