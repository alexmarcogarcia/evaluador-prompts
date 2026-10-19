"""Doble de prueba del puerto ModeloIA: respuestas configurables, sin red."""

from evaluador.dominio.modelos import Diagnostico, DiagnosticoPropuesto, MejoraPropuesta, Prompt
from evaluador.puertos.modelo_ia import ErrorProveedor

SIN_PROBLEMAS = DiagnosticoPropuesto(problemas=(), preguntas=(), rechazado=False)


class ModeloFalso:
    proveedor = "falso"
    modelo = "modelo-de-prueba"

    def __init__(
        self,
        diagnostico: DiagnosticoPropuesto = SIN_PROBLEMAS,
        mejora: MejoraPropuesta | None = None,
        error: ErrorProveedor | None = None,
    ) -> None:
        self._diagnostico = diagnostico
        self._mejora = mejora or MejoraPropuesta(texto="", cambios=())
        self._error = error
        self.llamadas: list[tuple[object, ...]] = []

    def diagnosticar(self, prompt: Prompt, idioma_interfaz: str) -> DiagnosticoPropuesto:
        self.llamadas.append(("diagnosticar", prompt, idioma_interfaz))
        if self._error:
            raise self._error
        return self._diagnostico

    def mejorar(
        self, diagnostico: Diagnostico, respuestas: dict[str, str | None], idioma_interfaz: str
    ) -> MejoraPropuesta:
        self.llamadas.append(("mejorar", diagnostico, respuestas, idioma_interfaz))
        if self._error:
            raise self._error
        return self._mejora
