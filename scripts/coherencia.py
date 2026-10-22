"""Comprobación de coherencia entre especificación, tareas y pruebas (T003, guía 7.3).

Falla (código 1) si:
- una tarea no referencia ningún requisito (RF/RNF) ni ADR, salvo las de las secciones de harness;
- tareas, plan, código, pruebas o evals citan un RF/RNF que no existe en ninguna spec;
- un requisito tiene todas sus tareas terminadas y ninguna prueba ni eval lo referencia
  («un requisito sin prueba no está terminado»).

Los requisitos cuyas tareas siguen abiertas se listan como pendientes, sin fallar.
Los identificadores son únicos en todo el proyecto: cada spec nueva continúa la numeración.
"""

import io
import re
import sys
from pathlib import Path

from _entorno import RAIZ

ID_REQUISITO = re.compile(r"\b(?:RF|RNF)-\d{3}\b")
DEFINICION = re.compile(r"\*\*((?:RF|RNF)-\d{3})")
TAREA = re.compile(r"^- \[( |x)\] \*\*(T\d{3})\*\*(.*)$")
ADR = re.compile(r"\bADR-\d{4}\b")
CARPETAS_CON_REFERENCIAS = ("tests", "evals", "src")
CARPETAS_DE_PRUEBA = ("tests", "evals")


def leer_tareas(tasks_md: str) -> list[tuple[str, bool, str, bool]]:
    """Devuelve (id, terminada, texto, exenta) por tarea; el texto incluye sus líneas de continuación."""
    tareas: list[tuple[str, bool, str, bool]] = []
    seccion = ""
    for linea in tasks_md.splitlines():
        if linea.startswith("#"):
            seccion = linea.lower()
            continue
        m = TAREA.match(linea)
        if m:
            tareas.append((m.group(2), m.group(1) == "x", m.group(3), "harness" in seccion))
        elif tareas and (linea.startswith("  ") or not linea.strip()):
            ident, hecha, texto, exenta = tareas[-1]
            tareas[-1] = (ident, hecha, texto + "\n" + linea, exenta)
    return tareas


def referencias_en(raiz: Path, carpetas: tuple[str, ...]) -> dict[str, set[str]]:
    """Identificador -> archivos que lo citan, dentro de las carpetas dadas."""
    refs: dict[str, set[str]] = {}
    for carpeta in carpetas:
        for archivo in (raiz / carpeta).rglob("*") if (raiz / carpeta).exists() else []:
            if archivo.is_file() and archivo.suffix in {".py", ".md", ".json", ".yaml", ".yml", ".txt"}:
                for ident in ID_REQUISITO.findall(archivo.read_text(encoding="utf-8", errors="ignore")):
                    refs.setdefault(ident, set()).add(str(archivo.relative_to(raiz)))
    return refs


def analizar(raiz: Path) -> tuple[list[str], list[str]]:
    """Devuelve (errores, requisitos pendientes de prueba)."""
    errores: list[str] = []
    pendientes: list[str] = []
    specs = sorted((raiz / "specs").glob("*/spec.md"))

    # Los identificadores son únicos en todo el proyecto (la spec 002 sigue la numeración de la 001):
    # citar uno de otra spec es correcto; solo es error si no está definido en ninguna.
    todos_definidos: set[str] = set()
    citados: dict[str, set[str]] = referencias_en(raiz, CARPETAS_CON_REFERENCIAS)
    for spec in specs:
        todos_definidos |= set(DEFINICION.findall(spec.read_text(encoding="utf-8")))
        for nombre in ("tasks.md", "plan.md"):
            doc = spec.parent / nombre
            if doc.exists():
                for ident in ID_REQUISITO.findall(doc.read_text(encoding="utf-8")):
                    citados.setdefault(ident, set()).add(str(doc.relative_to(raiz)))
    for ident in sorted(set(citados) - todos_definidos):
        donde = ", ".join(sorted(citados[ident]))
        errores.append(f"{ident} no existe en ninguna spec (citado en {donde})")

    probados = referencias_en(raiz, CARPETAS_DE_PRUEBA)
    for spec in specs:
        definidos = set(DEFINICION.findall(spec.read_text(encoding="utf-8")))
        tasks_md = spec.parent / "tasks.md"
        tareas = leer_tareas(tasks_md.read_text(encoding="utf-8")) if tasks_md.exists() else []

        tareas_por_requisito: dict[str, list[bool]] = {}
        for ident, hecha, texto, exenta in tareas:
            requisitos = set(ID_REQUISITO.findall(texto))
            if not requisitos and not ADR.search(texto) and not exenta:
                errores.append(f"{ident} no referencia ningún requisito (RF/RNF) ni ADR")
            for req in requisitos:
                tareas_por_requisito.setdefault(req, []).append(hecha)

        for req in sorted(definidos):
            if req in probados:
                continue
            estados = tareas_por_requisito.get(req, [])
            if estados and all(estados):
                errores.append(f"{req} tiene todas sus tareas terminadas y está sin prueba que lo referencie")
            else:
                pendientes.append(req)
    return errores, pendientes


def main() -> None:
    if isinstance(sys.stdout, io.TextIOWrapper):  # La consola de Windows usa cp1252 por defecto.
        sys.stdout.reconfigure(encoding="utf-8")
    errores, pendientes = analizar(RAIZ)
    if pendientes:
        print(f"Requisitos pendientes de prueba ({len(pendientes)}): {', '.join(pendientes)}")
    for error in errores:
        print(f"ERROR: {error}")
    print("Coherencia: OK" if not errores else f"Coherencia: {len(errores)} error(es)")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
