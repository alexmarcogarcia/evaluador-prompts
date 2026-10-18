# Evaluador de prompts

## Qué es
Aplicación que revisa prompts, explica sus problemas y propone cómo precisarlos, pensada para personas con poco dominio de la IA.

## Comandos
Pendiente. Se definen en las fases 5 y 7.

## Dónde está cada cosa
- Constitución: `docs/constitution.md`. Gobierna todo lo demás.
- One-pager y perfil: `docs/one-pager.md`
- Especificaciones: `specs/NNN-funcionalidad/` (`spec.md`, `plan.md`, `tasks.md`)
- ADRs: `docs/adr/`
- Código: `src/` · Pruebas: `tests/`

## Flujo de trabajo
Especificación → plan → tareas → implementación → verificación.
No decidas el alcance: si falta información, anótala como `[CLARIFICAR]` y pregunta.

## Reglas
- No implementes nada que no esté en una spec aprobada.
- No escribas claves de API ni datos de usuario en código, logs, mensajes ni commits.
- Cada cambio referencia un requisito (`RF-xxx`) y pasa la CI.
- No modifiques `docs/constitution.md` sin una enmienda aprobada por Àlex Marco.

## Verificación
Definición de hecho de la constitución. Los comandos concretos están pendientes de la Fase 7.
