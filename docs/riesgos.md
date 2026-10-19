# Registro de riesgos

**Revisión:** al cerrar cada historia · **Última revisión:** 2026-10-19 · **Aprobado por:** Àlex Marco

| ID | Riesgo | Probabilidad | Impacto | Respuesta | Responsable | Estado |
|---|---|---|---|---|---|---|
| R-01 | Google cambia o recorta el nivel gratuito de Gemini (cuota, condiciones, retirada del modelo) | Media | Alto | **Mitigar:** adaptador compatible con OpenAI y NVIDIA Nemotron configurado como alternativa (ADR-0001); las evals permiten validar un modelo nuevo en minutos | Àlex Marco | Abierto |
| R-02 | La detección no llega al 80 % (RNF-003) con ninguna estrategia gratuita | Media | Alto | **Mitigar:** estrategias 3a/3b/3c (T035). Si fallan todas, volver a la spec con dos opciones: revisar el umbral o reabrir el ADR-0001 con un modelo de pago | Àlex Marco | Mitigado (T035: 87,9 % con 3a) |
| R-03 | Medidas ruidosas: con 14 casos, cada problema vale unos 3,4 puntos | Alta | Medio | **Mitigar:** ampliar las evals a ≥ 50 casos validados (T022) | Àlex Marco | Mitigado (55 casos validados) |
| R-04 | Los límites de uso (429/503) interrumpen las evals o la app | Media | Medio | **Mitigar:** reintentos con espera y mensajes en lenguaje llano (RF-014); evals con pausas | Àlex Marco | Abierto |
| R-05 | Se envían a Google los prompts de otras personas, con posibles datos personales, al publicar | Baja (ahora) | Alto | **Evitar:** hoy no se publica. Antes de publicar, Fase 8 completa (perfil C): condiciones de uso de datos, aviso al usuario y RF-006 | Àlex Marco | Abierto |
| R-06 | Inyección de instrucciones en los prompts analizados | Media | Medio | **Mitigar:** regla en el prompt de sistema, validación en código (ADR-0003) y casos de inyección en las evals | Àlex Marco | Abierto |
| R-07 | Proyecto en solitario: sin revisión independiente | Alta | Medio | **Mitigar:** revisión asistida por IA y autorrevisión con la DoD en otro momento (constitución) | Àlex Marco | Abierto |
| R-08 | El alcance crece con la verificación (b) y el historial (d) antes de cerrar el incremento | Media | Medio | **Evitar:** b y d tienen spec propia y entran después de la Fase 9 | Àlex Marco | Abierto |

## Roles y comunicación

| Rol | Persona |
|---|---|
| Producto y prioridades | Àlex Marco |
| Decisiones técnicas | Àlex Marco, con propuestas del asistente de IA |
| Operación y mantenimiento | Àlex Marco |
| Asistente de IA (Claude Code) | Propone, implementa y verifica dentro de los límites de `AGENTS.md`. **No decide el alcance** |

**Cadencia:** flujo continuo, con revisión al cerrar cada historia (spec, código y riesgos coherentes).
**Comunicación:** proyecto individual; las decisiones quedan registradas en el repositorio (specs, ADRs, este registro).
