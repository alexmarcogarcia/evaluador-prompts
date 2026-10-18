# Cómo contribuir

Este proyecto sigue Spec Driven Development. Antes de cambiar nada, lee la [constitución](docs/constitution.md).

## Flujo

1. **Especificar:** crea o modifica `specs/NNN-funcionalidad/spec.md`. Lo que no se sepa se marca como `[CLARIFICAR: pregunta]`.
2. **Clarificar:** sin marcas `[CLARIFICAR]` abiertas y con la checklist de calidad pasada, la spec se aprueba.
3. **Planificar:** escribe `plan.md` y, para cada decisión cara de revertir, un ADR en `docs/adr/`.
4. **Tareas:** escribe `tasks.md`. Cada tarea referencia un `RF-xxx`.
5. **Implementar:** escribe primero la prueba y comprueba que falla; después, el código.
6. **Verificar:** antes de fusionar, pasa la definición de hecho de la constitución.

Si durante la implementación aparece un hueco, se vuelve a la especificación. No se parchea el código.

## Convenciones

- Ramas cortas desde `main`, una por tarea o grupo pequeño de tareas.
- Mensajes con [Conventional Commits](https://www.conventionalcommits.org/es/): `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
- Cada commit o PR referencia el requisito (`RF-xxx`) o la tarea (`Txxx`).
- Nunca se suben claves de API ni archivos `.env`.
