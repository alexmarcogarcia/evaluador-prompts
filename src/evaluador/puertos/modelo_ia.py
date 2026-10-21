"""Puerto hacia el modelo de IA (ADR-0001, principio 7: independencia del proveedor).

Los casos de uso dependen solo de esta interfaz; los adaptadores (Gemini, NVIDIA…) la implementan.
"""

from enum import StrEnum
from typing import Protocol

from evaluador.dominio.modelos import Diagnostico, DiagnosticoPropuesto, MejoraPropuesta, Prompt


class TipoError(StrEnum):
    """Fallos del proveedor que la interfaz explica en lenguaje llano (RF-014)."""

    LIMITE_DE_USO = "limite_de_uso"
    NO_DISPONIBLE = "no_disponible"
    TIEMPO_AGOTADO = "tiempo_agotado"
    RESPUESTA_INVALIDA = "respuesta_invalida"


class ErrorProveedor(Exception):
    def __init__(self, tipo: TipoError, reintentar_en_s: int | None = None) -> None:
        super().__init__(tipo.value)
        self.tipo = tipo
        self.reintentar_en_s = reintentar_en_s


class ModeloIA(Protocol):
    @property
    def proveedor(self) -> str:
        """Nombre del proveedor, para mostrarlo antes de enviar (RF-006)."""
        ...

    @property
    def modelo(self) -> str:
        """Nombre del modelo, para mostrarlo antes de enviar (RF-006)."""
        ...

    def diagnosticar(self, prompt: Prompt, idioma_interfaz: str) -> DiagnosticoPropuesto: ...

    def mejorar(
        self,
        diagnostico: Diagnostico,
        respuestas: dict[str, str | None],
        idioma_interfaz: str,
        idioma_prompt: str | None = None,
    ) -> MejoraPropuesta:
        """`respuestas`: pregunta -> respuesta, o None si se omitió.

        `idioma_prompt`: idioma detectado del prompt original (es, ca, en, de), si se sabe (RF-013).
        """
        ...
