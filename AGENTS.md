# Evaluador de prompts

## Qué es
Aplicación web en Python que revisa prompts, explica sus problemas y propone cómo precisarlos, pensada para personas con poco dominio de la IA.

## Comandos
- Instalar: `python scripts/setup.py`
- Verificar todo (lo mismo que la CI): `python scripts/check.py`
- Solo pruebas: `.venv/Scripts/python -m pytest` (Windows) · `.venv/bin/python -m pytest` (Linux/macOS)
- Pruebas contra un proveedor real (red y claves): `... -m pytest -m red`
- Coherencia spec ↔ tareas ↔ pruebas: `.venv/Scripts/python scripts/coherencia.py`
- Ejecutar la app: `.venv/Scripts/python -m evaluador` → http://127.0.0.1:8000

## Dónde está cada cosa
- Constitución: `docs/constitution.md`. Gobierna todo lo demás.
- One-pager y perfil: `docs/one-pager.md` · Riesgos y roles: `docs/riesgos.md`
- Especificaciones: `specs/NNN-funcionalidad/` (`spec.md`, `plan.md`, `tasks.md`, `research.md`)
- ADRs: `docs/adr/`
- Código: `src/evaluador/` (dominio, casos_uso, puertos, adaptadores) · Pruebas: `tests/` · Scripts: `scripts/`
- `spikes/`: código desechable; no se reutiliza ni se mantiene

## Flujo de trabajo
Especificación → plan → tareas → implementación → verificación.
No decidas el alcance: si falta información, anótala como `[CLARIFICAR]` y pregunta.
La prueba de cada tarea se escribe primero y debe fallar antes de implementar.

## Reglas
- No implementes nada que no esté en una spec aprobada.
- No escribas claves de API ni datos de usuario en código, logs, mensajes ni commits. No leas ni muestres `.env`.
- Cada prueba referencia el requisito que verifica (`RF-xxx` / `RNF-xxx`) en su docstring o en un comentario.
- Cada cambio referencia un requisito o tarea y pasa la CI.
- No modifiques `docs/constitution.md` sin una enmienda aprobada por Àlex Marco.
- Trabaja en una rama corta; nada se fusiona en `main` con la CI en rojo.

## Verificación
`python scripts/check.py` en verde, más la definición de hecho de la constitución.
