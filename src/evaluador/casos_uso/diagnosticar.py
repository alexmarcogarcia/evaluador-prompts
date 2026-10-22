"""Caso de uso de la historia P1 · Diagnosticar un prompt (T031).

Comprueba la entrada antes de gastar una llamada (RF-001, RF-002), pide el diagnóstico al modelo y
lo depura con las reglas del dominio (ADR-0003). Los errores del proveedor (RF-014) se propagan
con su tipo para que la interfaz los explique.
"""

import logging
from enum import StrEnum

from evaluador.casos_uso.reintento import con_reintento
from evaluador.dominio import reglas
from evaluador.dominio.modelos import Diagnostico, Prompt
from evaluador.puertos.modelo_ia import ModeloIA

registro = logging.getLogger("evaluador.diagnostico")


class MotivoEntrada(StrEnum):
    PROMPT_VACIO = "prompt_vacio"
    FALTA_RESULTADO_ESPERADO = "falta_resultado_esperado"
    DEMASIADO_LARGO = "demasiado_largo"


class EntradaInvalida(Exception):
    def __init__(self, motivo: MotivoEntrada, caracteres_sobrantes: int = 0) -> None:
        super().__init__(motivo.value)
        self.motivo = motivo
        self.caracteres_sobrantes = caracteres_sobrantes


class Diagnosticar:
    def __init__(self, modelo: ModeloIA) -> None:
        self._modelo = modelo

    def ejecutar(self, texto: str, resultado_esperado: str, idioma_interfaz: str) -> Diagnostico:
        if not texto.strip():
            raise EntradaInvalida(MotivoEntrada.PROMPT_VACIO)
        if not resultado_esperado.strip():
            raise EntradaInvalida(MotivoEntrada.FALTA_RESULTADO_ESPERADO)
        sobrantes = reglas.caracteres_sobrantes(texto)
        if sobrantes:
            raise EntradaInvalida(MotivoEntrada.DEMASIADO_LARGO, sobrantes)

        prompt = Prompt(texto=texto, resultado_esperado=resultado_esperado)
        propuesta = con_reintento(lambda: self._modelo.diagnosticar(prompt, idioma_interfaz))  # RF-018
        depurado = reglas.depurar_diagnostico(prompt, propuesta)
        registro.info(
            "diagnostico problemas=%d preguntas=%d descartados=%d rechazado=%s",
            len(depurado.diagnostico.problemas),
            len(depurado.diagnostico.preguntas),
            depurado.descartados,
            depurado.diagnostico.rechazado,
        )
        return depurado.diagnostico
