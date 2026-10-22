"""Pruebas de contrato del adaptador (T020): respuesta del modelo -> propuestas del dominio.

El adaptador valida la ESTRUCTURA de contracts/*.schema.json; los VALORES (categoría, tipo, citas…)
los valida el dominio, para descartar un problema malo sin perder el resto (ADR-0003).
Verifica RF-003, RF-007, RF-009, RF-014 (respuesta inválida) y RF-015.
"""

import json
from pathlib import Path

import pytest
from pydantic import BaseModel

from evaluador.adaptadores.modelo_openai_compatible import (
    RespuestaDiagnostico,
    RespuestaMejora,
    interpretar_diagnostico,
    interpretar_mejora,
)
from evaluador.dominio.modelos import PreguntaPropuesta, ProblemaPropuesto
from evaluador.puertos.modelo_ia import ErrorProveedor, TipoError

CONTRATOS = Path(__file__).resolve().parents[2] / "contracts"

DIAGNOSTICO = {
    "rechazado": False,
    "problemas": [
        {
            "tipo": "texto",
            "categoria": 9,
            "fragmento": "que esté bien",
            "falta": None,
            "explicacion": "Es subjetivo.",
            "gravedad": "alta",
        }
    ],
    "preguntas": [{"texto": "¿Para quién es?", "problema": 1}],
}


def test_un_diagnostico_valido_se_convierte_en_propuesta_del_dominio() -> None:
    """RF-003 y RF-007."""
    propuesta = interpretar_diagnostico(json.dumps(DIAGNOSTICO))
    assert propuesta.problemas == (
        ProblemaPropuesto("texto", 9, "que esté bien", None, "Es subjetivo.", "alta"),
    )
    assert propuesta.preguntas == (PreguntaPropuesta("¿Para quién es?", 1),)
    assert not propuesta.rechazado


def test_se_acepta_el_json_envuelto_en_texto_o_en_bloque_de_codigo() -> None:
    texto = "Aquí tienes:\n```json\n" + json.dumps(DIAGNOSTICO) + "\n```"
    assert len(interpretar_diagnostico(texto).problemas) == 1


def test_los_valores_fuera_de_catalogo_llegan_al_dominio_para_que_los_descarte() -> None:
    """La estructura es válida; el dominio descartará solo ese problema."""
    datos = json.loads(json.dumps(DIAGNOSTICO))
    datos["problemas"][0]["categoria"] = 10
    assert interpretar_diagnostico(json.dumps(datos)).problemas[0].categoria == 10


def test_un_rechazo_se_interpreta() -> None:
    """RF-015."""
    rechazo = {"rechazado": True, "motivo": "Peligroso.", "problemas": [], "preguntas": []}
    assert interpretar_diagnostico(json.dumps(rechazo)).rechazado


@pytest.mark.parametrize(
    "texto",
    [
        "no es JSON",
        json.dumps({"problemas": [], "preguntas": []}),  # falta «rechazado»
        json.dumps({**DIAGNOSTICO, "problemas": [{"tipo": "texto"}]}),  # problema incompleto
        json.dumps({**DIAGNOSTICO, "preguntas": [{"texto": "¿?", "problema": "uno"}]}),
    ],
)
def test_una_respuesta_con_estructura_invalida_es_respuesta_invalida(texto: str) -> None:
    """RF-014: respuesta inválida."""
    with pytest.raises(ErrorProveedor) as fallo:
        interpretar_diagnostico(texto)
    assert fallo.value.tipo is TipoError.RESPUESTA_INVALIDA


def test_una_mejora_valida_se_convierte_en_propuesta_del_dominio() -> None:
    """RF-009."""
    texto = json.dumps(
        {"texto": "Escribe un artículo.", "cambios": [{"explicacion": "Tipo.", "problemas": ["P1"]}]}
    )
    mejora = interpretar_mejora(texto)
    assert mejora.texto == "Escribe un artículo."
    assert mejora.cambios == (("Tipo.", ("P1",)),)


def test_una_mejora_sin_texto_es_respuesta_invalida() -> None:
    """RF-014."""
    with pytest.raises(ErrorProveedor):
        interpretar_mejora(json.dumps({"cambios": []}))


@pytest.mark.parametrize(
    ("esquema", "modelo", "definicion"),
    [
        ("diagnostico.schema.json", RespuestaDiagnostico, None),
        ("diagnostico.schema.json", RespuestaDiagnostico.Problema, "problema"),
        ("diagnostico.schema.json", RespuestaDiagnostico.Pregunta, "pregunta"),
        ("mejora.schema.json", RespuestaMejora, None),
        ("mejora.schema.json", RespuestaMejora.Cambio, "cambio"),
    ],
)
def test_los_campos_obligatorios_coinciden_con_el_contrato(
    esquema: str, modelo: type[BaseModel], definicion: str | None
) -> None:
    contrato = json.loads((CONTRATOS / esquema).read_text(encoding="utf-8"))
    parte = contrato["$defs"][definicion] if definicion else contrato
    obligatorios = {nombre for nombre, campo in modelo.model_fields.items() if campo.is_required()}
    assert obligatorios == set(parte["required"])


def test_una_respuesta_invalida_registra_que_campo_fallo_sin_su_contenido(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """RF-014 y RNF-006: para diagnosticar hace falta saber qué campo falló, pero el log nunca lleva texto."""
    malo = {**DIAGNOSTICO, "preguntas": [{"texto": "¿SECRETO-PRIVADO?", "problema": "uno"}]}
    with pytest.raises(ErrorProveedor):
        interpretar_diagnostico(json.dumps(malo))
    assert "preguntas.0.problema" in caplog.text and "int_parsing" in caplog.text
    assert "SECRETO-PRIVADO" not in caplog.text and "uno" not in caplog.text


def test_una_respuesta_sin_json_tambien_se_registra(caplog: pytest.LogCaptureFixture) -> None:
    """RF-014: si el modelo no devuelve ningún JSON, también queda constancia (sin el texto)."""
    with pytest.raises(ErrorProveedor):
        interpretar_diagnostico("Lo siento, no puedo ayudar con eso. TEXTO-PRIVADO")
    assert "sin_json" in caplog.text and "TEXTO-PRIVADO" not in caplog.text
