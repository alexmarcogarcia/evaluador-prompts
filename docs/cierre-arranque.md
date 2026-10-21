# Cierre del arranque · Fase 9

**Proyecto:** Evaluador de prompts · **Perfil:** B · **Fecha:** 2026-10-21 · **Estado:** pendiente de la retrospectiva con Àlex Marco

El arranque termina cuando el primer incremento ha recorrido el ciclo completo (spec aprobada, plan, tareas, implementación y verificación) y funciona de extremo a extremo con el pipeline real. El incremento 001 (diagnóstico, preguntas y versión mejorada) cumple esa condición.

## Checklist de arranque completado

| Punto de la guía | Estado | Evidencia |
|---|---|---|
| One-pager con problema, objetivo, criterios de éxito y decisión go/no-go | ✅ | `docs/one-pager.md` v1.0 (GO el 2026-10-18) |
| Perfil del proyecto asignado y peso de los artefactos acordado | ✅ | Perfil B, con seguridad de C al abrirse (`docs/one-pager.md`, Fase 1) |
| Constitución aprobada, con DoD, reglas de revisión y de confidencialidad | ✅ | `docs/constitution.md` v1.2 |
| Repositorio estructurado con `/specs`, `README.md` ejecutable y `CONTRIBUTING.md` | ✅ | Verificado el 2026-10-21 con un clon limpio: con solo el README se instala, se prueba (131 pruebas) y se arranca |
| Especificación del primer incremento aprobada, sin dudas abiertas | ✅ | `specs/001-diagnostico-prompt/spec.md` v1.5, 0 marcas `[CLARIFICAR]` |
| Plan técnico con ADRs, contratos y matriz de trazabilidad | ✅ | `plan.md`, ADR-0001 a ADR-0003, `contracts/` |
| `tasks.md` con tareas trazables a requisitos | ✅ | 26 tareas; la comprobación de coherencia lo verifica en cada PR |
| CI en verde con linter, formato, pruebas y comprobación de coherencia | ✅ | GitHub Actions: también tipos, pip-audit y gitleaks |
| Entorno reproducible con un solo comando | ✅ | `python scripts/setup.py` |
| Secretos gestionados y herramientas permitidas definidas | ✅ | `.env` fuera de git, gitleaks sobre todo el historial, constitución y `docs/seguridad.md` |
| `AGENTS.md` y verificación autónoma, si se usan agentes | ✅ | `AGENTS.md` y `python scripts/check.py` |
| Registro de riesgos y acuerdo de roles | ✅ | `docs/riesgos.md` (R-01 ocurrido y gestionado; R-02 y R-03 mitigados) |
| Primer incremento desplegado y verificado contra sus criterios de aceptación | ✅ | Quickstart pasos 1–5 con Gemini real; pruebas de aceptación P1–P3; evals de diagnóstico (55 casos) y de mejora (37 casos) |

## Requisitos de la spec 001

| Requisito | Verificación | Resultado |
|---|---|---|
| RF-001 a RF-016 | Pruebas automáticas (unit, contrato, integración, aceptación) | ✅ Todos con prueba |
| RNF-001 · tiempo p95 < 30 s | Evals | ✅ 1,6–3,7 s (diagnóstico), 2,0 s (mejora) |
| RNF-002 · coste 0 € | Configuración: solo niveles gratuitos | ✅ en la práctica; sin prueba automática (la comprobación de coherencia lo marca como pendiente) |
| RNF-003 · detección ≥ 80 %, falsos positivos ≤ 20 % | Evals (55 casos) | ✅ 87,9 % y 18–20 % |
| RNF-004 · citas literales | Garantizado por el dominio | ✅ |
| RNF-005 · comprensibilidad | Prueba con 5 personas | ⏳ **T060** |
| RNF-006 · logs solo con métricas | Pruebas | ✅ |
| RNF-007 · rechazos | Evals | ✅ 6/6 dañinos, 0 % legítimos |
| RNF-008 a RNF-010 · seguridad | Pruebas | ✅ |
| RNF-011 · no inventar en la mejora | Evals con juez calibrado | ✅ 0 % datos inventados, 2,7 % requisitos añadidos |

## Después del arranque (guía)

1. **Retrospectiva corta** con Àlex Marco: qué decisiones del arranque se mantienen y cuáles cambian. Preguntas propuestas al final de este documento.
2. **Enmiendas a la constitución**, si salen de la retrospectiva.
3. **Revisión de los criterios de éxito de la Fase 0:**
   - Criterio 1 (de 3 reescrituras a 1 como máximo): se mide con prompts reales de Àlex Marco.
   - Criterio 2 (4 de 5 personas no expertas obtienen mejor resultado): **T060**.
   - Criterio 3 (comprobar y repetir comparaciones): parcialmente cubierto por las evals; la verificación con casos dentro de la app (diferenciación b) es una spec futura.
   - Fecha de evaluación acordada: 3 meses tras el primer incremento, **2027-01-21**.
4. **Siguientes incrementos**, que empiezan por la Fase 3:
   - verificación con casos (b);
   - historial (d);
   - extensión de navegador, la idea de Àlex Marco del 2026-10-20, aplazada hasta tener la app.

## Lecciones aprendidas (propuesta para la retrospectiva)

- **Los proveedores gratuitos cambian sin avisar** (R-01, tres veces): modelos retirados (Kimi, Mistral, Nemotron 3 Super) y saturaciones (Flash-Lite, 2026-10-20). La independencia del proveedor (principio 7) y las evals permitieron adaptarse en minutos.
- **Medir antes de decidir funcionó:** la estrategia 3a subió la detección del 67,7 % al 87,9 %, y la medición evitó adoptar Gemini 3.5 Flash, que no tiene cuota gratuita suficiente.
- **Las garantías en código tienen límites:** RF-010 se intentó imponer en código y empeoró la experiencia. Solo puede juzgarlo quien entiende el texto, y se resolvió cambiando la spec (1.5).
- **Las etiquetas humanas hechas deprisa invalidan la calibración:** la primera tanda dio 2/12 y hubo que revisarla con calma.
- **La comprobación de coherencia cuenta menciones, no pruebas reales:** un comentario con un identificador basta para darlo por probado. Mejora pendiente.
