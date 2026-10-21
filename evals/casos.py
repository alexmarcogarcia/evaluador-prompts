"""Lectura de los casos de evals desde sus archivos Markdown validados (T022).

Un archivo solo cuenta si su cabecera dice «**Estado:** validado»: los casos sin validar no son
una «respuesta correcta» contra la que medir. Los casos con «[PENDIENTE]» se saltan.
"""

import re
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
IDIOMAS = {"Español": "es", "Catalán": "ca", "Inglés": "en", "Alemán": "de"}
ARCHIVOS = (
    RAIZ / "specs" / "001-diagnostico-prompt" / "casos-prueba.md",
    RAIZ / "evals" / "casos" / "ampliacion-v1.md",
)


@dataclass(frozen=True)
class Esperado:
    tipo: str
    categoria: int
    fragmento: str | None


@dataclass(frozen=True)
class Caso:
    id: str
    prompt: str
    resultado: str
    esperados: tuple[Esperado, ...]
    debe_rechazar: bool
    idioma: str | None = None
    """Idioma del prompt (es, ca, en, de), leído de la cabecera del caso."""


def esta_validado(md: str) -> bool:
    return bool(re.search(r"^\*\*Estado:\*\* validado", md, flags=re.M))


def leer_casos(md: str) -> list[Caso]:
    casos = []
    for bloque in re.split(r"^### ", md, flags=re.M)[1:]:
        cabecera = bloque.splitlines()[0]
        if not re.match(r"C\d\d", cabecera) or "[PENDIENTE]" in bloque:
            continue
        lineas_prompt: list[str] = []
        esperados: list[Esperado] = []
        en_prompt = False
        for linea in bloque.splitlines():
            if linea.startswith("**Prompt:**"):
                en_prompt = True
            elif en_prompt and linea.startswith("> "):
                lineas_prompt.append(linea[2:])
            elif en_prompt and lineas_prompt:
                en_prompt = False
            fila = re.match(r"\| (T|A) \| (\d) \| (.+) \|$", linea)
            if fila:
                cita = re.search(r"«(.+?)»", fila.group(3)) if fila.group(1) == "T" else None
                esperados.append(Esperado(fila.group(1), int(fila.group(2)), cita.group(1) if cita else None))
        resultado = re.search(r"\*\*Resultado esperado:\*\* (.+)", bloque)
        casos.append(
            Caso(
                id=cabecera[:3],
                prompt="\n".join(lineas_prompt),
                resultado=resultado.group(1).strip() if resultado else "",
                esperados=tuple(esperados),
                debe_rechazar="**rechazo**" in bloque,
                idioma=next((c for n, c in IDIOMAS.items() if f"· {n}" in cabecera), None),
            )
        )
    return casos


def cargar_validados(archivos: tuple[Path, ...] = ARCHIVOS) -> tuple[list[Caso], list[Path]]:
    """Devuelve (casos de archivos validados, archivos ignorados por no estar validados)."""
    casos: list[Caso] = []
    ignorados: list[Path] = []
    for archivo in archivos:
        md = archivo.read_text(encoding="utf-8")
        if esta_validado(md):
            casos.extend(leer_casos(md))
        else:
            ignorados.append(archivo)
    return casos, ignorados
