"""Pruebas de scripts/coherencia.py (T003).

Los identificadores de requisito se construyen con f-strings (p. ej. f"RF-{1:03d}") para que este
archivo no contenga referencias literales: la propia comprobación de coherencia analiza tests/
y las tomaría por pruebas de requisitos reales.
"""

from pathlib import Path

import coherencia

RF1, RF2, RNF1 = f"RF-{1:03d}", f"RF-{2:03d}", f"RNF-{1:03d}"


def crear_proyecto(raiz: Path, tareas: str, pruebas: str = "") -> Path:
    spec = raiz / "specs" / "001-demo"
    spec.mkdir(parents=True)
    (spec / "spec.md").write_text(
        f"- **{RF1}:** El sistema debe A.\n"
        f"- **{RF2}:** El sistema debe B.\n"
        f"- **{RNF1} · Tiempo:** p95 < 1 s.\n",
        encoding="utf-8",
    )
    (spec / "tasks.md").write_text(tareas, encoding="utf-8")
    (raiz / "tests").mkdir()
    (raiz / "tests" / "test_demo.py").write_text(pruebas, encoding="utf-8")
    return raiz


def test_proyecto_coherente_no_da_errores(tmp_path: Path) -> None:
    tareas = f"## Historia\n- [x] **T010** Hacer A ({RF1})\n- [ ] **T011** Hacer B ({RF2}, {RNF1})\n"
    raiz = crear_proyecto(tmp_path, tareas, pruebas=f"# Verifica {RF1}\n")
    errores, pendientes = coherencia.analizar(raiz)
    assert errores == []
    assert pendientes == [RF2, RNF1]


def test_tarea_sin_requisito_es_error(tmp_path: Path) -> None:
    raiz = crear_proyecto(tmp_path, "## Historia\n- [ ] **T010** Hacer algo sin requisito\n")
    errores, _ = coherencia.analizar(raiz)
    assert any("T010" in e and "no referencia" in e for e in errores)


def test_tareas_de_harness_no_necesitan_requisito(tmp_path: Path) -> None:
    raiz = crear_proyecto(tmp_path, "## Base: harness (Fase 7)\n- [ ] **T001** Configurar el linter\n")
    errores, _ = coherencia.analizar(raiz)
    assert errores == []


def test_la_referencia_a_un_adr_cuenta_como_requisito(tmp_path: Path) -> None:
    raiz = crear_proyecto(tmp_path, f"## Historia\n- [ ] **T010** Elegir estrategia (ADR-{3:04d})\n")
    errores, _ = coherencia.analizar(raiz)
    assert errores == []


def test_identificador_inexistente_en_pruebas_es_error(tmp_path: Path) -> None:
    raiz = crear_proyecto(
        tmp_path, f"## Historia\n- [ ] **T010** A ({RF1})\n", pruebas=f"# {'RF'}-{99:03d}\n"
    )
    errores, _ = coherencia.analizar(raiz)
    assert any(f"RF-{99:03d}" in e and "no existe" in e for e in errores)


def test_identificador_inexistente_en_tareas_es_error(tmp_path: Path) -> None:
    raiz = crear_proyecto(tmp_path, f"## Historia\n- [ ] **T010** A (RF-{77:03d})\n")
    errores, _ = coherencia.analizar(raiz)
    assert any(f"RF-{77:03d}" in e and "no existe" in e for e in errores)


def test_requisito_con_tareas_terminadas_y_sin_prueba_es_error(tmp_path: Path) -> None:
    raiz = crear_proyecto(tmp_path, f"## Historia\n- [x] **T010** Hacer A ({RF1})\n")
    errores, _ = coherencia.analizar(raiz)
    assert any(RF1 in e and "sin prueba" in e for e in errores)


def test_requisito_con_alguna_tarea_pendiente_no_es_error(tmp_path: Path) -> None:
    tareas = f"## Historia\n- [x] **T010** Parte 1 ({RF1})\n- [ ] **T011** Parte 2 ({RF1})\n"
    errores, pendientes = coherencia.analizar(crear_proyecto(tmp_path, tareas))
    assert errores == []
    assert RF1 in pendientes


def test_las_lineas_de_continuacion_pertenecen_a_la_tarea(tmp_path: Path) -> None:
    tareas = f"## Historia\n- [ ] **T010** Reglas en el dominio:\n  - longitud máxima\n\n  ({RF1})\n"
    errores, _ = coherencia.analizar(crear_proyecto(tmp_path, tareas))
    assert errores == []
