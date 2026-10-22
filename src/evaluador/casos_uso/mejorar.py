"""Caso de uso de la historia P3 · Obtener una versión mejorada explicada (T052).

Pide la mejora al modelo y la depura con el dominio: los cambios que no enlazan problemas reales se
descartan (RF-009). Además, el código vigila el idioma (RF-013): la mejora va en el idioma del
prompt original y, si sale en otro, se pide otra vez indicando el idioma (un solo reintento).

RF-010 (spec 1.5) no se impone en código: si un dato omitido ya está en el prompt no hace
falta marcador, y eso solo puede juzgarlo quien entiende el texto.
Que la mejora no invente lo omitido lo vigilan las evals con el juez (RNF-011).
"""

import logging

from evaluador.casos_uso.reintento import con_reintento
from evaluador.dominio import reglas
from evaluador.dominio.idioma import detectar
from evaluador.dominio.modelos import Diagnostico, MejoraPropuesta, VersionMejorada
from evaluador.puertos.modelo_ia import ModeloIA

MARCADOR = "[COMPLETAR:"
registro = logging.getLogger("evaluador.mejora")


class Mejorar:
    def __init__(self, modelo: ModeloIA) -> None:
        self._modelo = modelo

    def _pedir(
        self,
        diagnostico: Diagnostico,
        respuestas: dict[str, str | None],
        idioma: str,
        idioma_prompt: str | None,
    ) -> tuple[MejoraPropuesta, bool]:
        """Devuelve (propuesta, ¿hubo que reintentar por el idioma?)."""

        def pedir() -> MejoraPropuesta:
            return self._modelo.mejorar(diagnostico, respuestas, idioma, idioma_prompt)

        propuesta = con_reintento(pedir)  # RF-018
        idioma_mejora = detectar(propuesta.texto)
        if idioma_prompt and idioma_mejora and idioma_mejora != idioma_prompt:
            return con_reintento(pedir), True
        return propuesta, False

    def ejecutar(
        self, diagnostico: Diagnostico, respuestas: dict[str, str | None], idioma_interfaz: str
    ) -> VersionMejorada:
        if diagnostico.rechazado:
            raise ValueError("Un diagnóstico rechazado no se puede mejorar (RF-015).")
        idioma_prompt = detectar(diagnostico.prompt.texto)
        propuesta, reintentado = self._pedir(diagnostico, respuestas, idioma_interfaz, idioma_prompt)
        version = reglas.depurar_mejora(diagnostico, propuesta)
        registro.info(
            "mejora cambios=%d descartados=%d omitidas=%d marcadores=%d reintento_idioma=%s",
            len(version.cambios),
            len(propuesta.cambios) - len(version.cambios),
            sum(1 for q in diagnostico.preguntas if respuestas.get(q.id) is None),
            version.texto.count(MARCADOR),
            reintentado,
        )
        return version
