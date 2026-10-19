"""Caso de uso de la historia P3 · Obtener una versión mejorada explicada (T052).

Pide la mejora al modelo y la depura con el dominio: los cambios que no enlazan problemas reales se
descartan (RF-009). Si el usuario omitió preguntas y el modelo no dejó marcadores, el código los
añade (RF-010): la información omitida nunca se da por inventada.
"""

import logging
from dataclasses import replace

from evaluador.dominio import reglas
from evaluador.dominio.modelos import Diagnostico, VersionMejorada
from evaluador.puertos.modelo_ia import ModeloIA

MARCADOR = "[COMPLETAR:"
registro = logging.getLogger("evaluador.mejora")


class Mejorar:
    def __init__(self, modelo: ModeloIA) -> None:
        self._modelo = modelo

    def ejecutar(
        self, diagnostico: Diagnostico, respuestas: dict[str, str | None], idioma_interfaz: str
    ) -> VersionMejorada:
        if diagnostico.rechazado:
            raise ValueError("Un diagnóstico rechazado no se puede mejorar (RF-015).")
        propuesta = self._modelo.mejorar(diagnostico, respuestas, idioma_interfaz)
        version = reglas.depurar_mejora(diagnostico, propuesta)

        omitidas = [q for q in diagnostico.preguntas if respuestas.get(q.id) is None]
        presentes = version.texto.count(MARCADOR)
        if presentes < len(omitidas):
            faltan = "\n".join(f"{MARCADOR} {q.texto}]" for q in omitidas[presentes:])
            version = replace(version, texto=f"{version.texto.rstrip()}\n\n{faltan}")
        registro.info(
            "mejora cambios=%d descartados=%d omitidas=%d marcadores_anadidos=%d",
            len(version.cambios),
            len(propuesta.cambios) - len(version.cambios),
            len(omitidas),
            max(0, len(omitidas) - presentes),
        )
        return version
