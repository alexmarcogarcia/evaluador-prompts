"""Entidades del dominio (spec 001, «Entidades y glosario»).

Dos familias:
- Las entidades validadas (Problema, Diagnostico, VersionMejorada…) cumplen los invariantes de la
  constitución al construirse: si existen, son correctas.
- Las propuestas (…Propuesto/…Propuesta) son lo que devuelve el modelo, sin validar. Solo
  `reglas` las convierte en entidades validadas.
"""

from dataclasses import dataclass
from enum import IntEnum, StrEnum


class Categoria(IntEnum):
    """Catálogo cerrado de la spec (sección «Catálogo de categorías y fronteras»)."""

    OBJETIVO_AMBIGUO = 1
    FALTA_DE_CONTEXTO = 2
    DESTINATARIO_O_TONO = 3
    FORMATO_DE_SALIDA = 4
    INSTRUCCIONES_CONTRADICTORIAS = 5
    RESTRICCIONES_AUSENTES = 6
    TAREA_COMPUESTA = 7
    FALTAN_EJEMPLOS = 8
    VAGUEDAD_LEXICA = 9


class TipoProblema(StrEnum):
    EN_TEXTO = "texto"
    POR_AUSENCIA = "ausencia"


class Gravedad(StrEnum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


@dataclass(frozen=True)
class Prompt:
    """Lo que escribe el usuario. Inmutable: el original nunca se modifica."""

    texto: str


@dataclass(frozen=True)
class Problema:
    id: str
    tipo: TipoProblema
    categoria: Categoria
    explicacion: str
    gravedad: Gravedad
    fragmento: str | None
    falta: str | None

    def __post_init__(self) -> None:
        if not self.explicacion.strip():
            raise ValueError("Un problema necesita una explicación.")
        if self.tipo is TipoProblema.EN_TEXTO and not (self.fragmento and self.fragmento.strip()):
            raise ValueError("Un problema en el texto debe citar su fragmento.")
        if self.tipo is TipoProblema.POR_AUSENCIA:
            if self.fragmento is not None:
                raise ValueError("Un problema por ausencia no cita fragmento.")
            if not (self.falta and self.falta.strip()):
                raise ValueError("Un problema por ausencia debe indicar qué falta.")


@dataclass(frozen=True)
class Pregunta:
    id: str
    texto: str
    problema_id: str


@dataclass(frozen=True)
class Diagnostico:
    prompt: Prompt
    problemas: tuple[Problema, ...]
    preguntas: tuple[Pregunta, ...]
    rechazado: bool = False

    def __post_init__(self) -> None:
        if self.rechazado and (self.problemas or self.preguntas):
            raise ValueError("Un diagnóstico rechazado no tiene problemas ni preguntas.")

    @property
    def sin_problemas(self) -> bool:
        return not self.rechazado and not self.problemas


@dataclass(frozen=True)
class Cambio:
    explicacion: str
    problema_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.problema_ids:
            raise ValueError("Cada cambio debe referenciar al menos un problema.")


@dataclass(frozen=True)
class VersionMejorada:
    original: Prompt
    texto: str
    cambios: tuple[Cambio, ...]


@dataclass(frozen=True)
class ProblemaPropuesto:
    """Problema tal como lo devuelve el modelo, sin validar."""

    tipo: str
    categoria: int
    fragmento: str | None
    falta: str | None
    explicacion: str
    gravedad: str


@dataclass(frozen=True)
class PreguntaPropuesta:
    texto: str
    problema: int
    """Posición (desde 1) del problema que la motiva dentro de la propuesta del modelo."""


@dataclass(frozen=True)
class DiagnosticoPropuesto:
    problemas: tuple[ProblemaPropuesto, ...]
    preguntas: tuple[PreguntaPropuesta, ...]
    rechazado: bool


@dataclass(frozen=True)
class MejoraPropuesta:
    texto: str
    cambios: tuple[tuple[str, tuple[str, ...]], ...]
    """(explicación, identificadores de los problemas que resuelve) por cada cambio."""
