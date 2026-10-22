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
        mejora: MejoraPropuesta | tuple[MejoraPropuesta, ...] | None = None,
        error: ErrorProveedor | None = None,
        fallos: tuple[ErrorProveedor, ...] = (),
    ) -> None:
        self._diagnostico = diagnostico
        # Una mejora fija, o una secuencia que se devuelve llamada a llamada (la última se repite).
        mejoras = mejora if isinstance(mejora, tuple) else (mejora or MejoraPropuesta(texto="", cambios=()),)
        self._mejoras = list(mejoras)
        self._error = error
        # Errores que se lanzan una sola vez, en orden, antes de responder (reintentos, RF-018).
        self.fallos = list(fallos)
        self.llamadas: list[tuple[object, ...]] = []

    def diagnosticar(self, prompt: Prompt, idioma_interfaz: str) -> DiagnosticoPropuesto:
        self.llamadas.append(("diagnosticar", prompt, idioma_interfaz))
        if self.fallos:
            raise self.fallos.pop(0)
        if self._error:
            raise self._error
        return self._diagnostico

    def mejorar(
        self,
        diagnostico: Diagnostico,
        respuestas: dict[str, str | None],
        idioma_interfaz: str,
        idioma_prompt: str | None = None,
    ) -> MejoraPropuesta:
        self.llamadas.append(("mejorar", diagnostico, respuestas, idioma_interfaz, idioma_prompt))
        if self.fallos:
            raise self.fallos.pop(0)
        if self._error:
            raise self._error
        return self._mejoras.pop(0) if len(self._mejoras) > 1 else self._mejoras[0]
