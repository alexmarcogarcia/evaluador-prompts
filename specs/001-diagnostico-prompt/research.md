# Investigación: Spec 001 · Diagnóstico de prompts

**Fase:** 5 · Plan técnico · **Fecha:** 2026-10-19

## Spike 001 · ¿Qué modelo gratuito diagnostica bien?

**Pregunta:** ¿hay un modelo gratuito que cumpla RNF-001 (p95 < 30 s), RNF-003 (≥ 80 % de detección, ≤ 20 % de falsos positivos), RNF-004 (citas literales al 100 %) y RF-015 (rechazos)?

**Método:**
- 14 casos validados (`casos-prueba.md` v1.0), con el mismo prompt de sistema para todos los modelos y temperatura 0.
- Puntuación automática por categoría con `spikes/001-modelos/spike.py`, revisada a mano después.
- Las respuestas completas están en `spikes/001-modelos/resultados/`.

### Disponibilidad (prueba de conexión, 2026-10-18)

| Modelo (NVIDIA, nivel gratuito) | Estado |
|---|---|
| `nvidia/nemotron-3-super-120b-a12b` | Disponible |
| `openai/gpt-oss-20b` | Disponible |
| `google/gemma-4-31b-it` | Disponible, pero 77 s para responder «OK» |
| `deepseek-ai/deepseek-v4.1-flash`, `z-ai/glm-5.3`, `z-ai/glm-5.3-flash`, `meta/llama-guard-4-12b` | Sin respuesta en 90 s |
| `moonshotai/kimi-k2.6`, `mistralai/mistral-large-2-instruct` | 404: no disponibles para la cuenta |

### Resultados

| Métrica | Objetivo | Nemotron 3 Super | gpt-oss-20b |
|---|---|---|---|
| Respuestas válidas | — | 14/14 | 12/14 (2 tiempos agotados a los 120 s) |
| Detección (RNF-003) | ≥ 80 % | 70 % ❌ | 83 % ✅ |
| Falsos positivos (RNF-003) | ≤ 20 % | 52 % ❌ | 44 % ❌ |
| Citas literales (RNF-004) | 100 % | 16/16 ✅ | 24/24 ✅ |
| Rechazos correctos (RF-015) | 100 % | 14/14 ✅ | 12/12 ✅ |
| Prompt bueno sin problemas (C07, RF-005) | 0 problemas | ✅ | ✅ |
| Inyección no obedecida (C08) | No declarar el prompt perfecto | ✅ | Sin dato (tiempo agotado) |
| Tiempo p95 (RNF-001) | < 30 s | 70,6 s ❌ | 61,1 s ❌ |

### Hallazgos de la revisión manual

1. **El catálogo de categorías se solapa.** Es la causa principal de los «falsos positivos»; muchos son problemas reales clasificados en una categoría vecina:
   - La longitud se clasifica tanto en 4 (formato) como en 6 (restricciones): C01, C02, C12.
   - Varias tareas mezcladas se clasifican en 7 (compuesta), 5 (contradicción) o 1 (ambiguo): C03, C13.
   - Faltar ejemplos de los nombres existentes se clasifica en 2 (contexto) o en 8 (ejemplos): C14.
   - Algo vago se clasifica en 1 (ambiguo) o en 9 (vaguedad): C01, C11.

   **Consecuencia:** la spec necesita definiciones de categoría con fronteras explícitas. Es un hueco de la especificación y se corrige allí (Fase 4), no en el código.
2. **Los modelos señalan de más.** Enumeran cualquier cosa que podría faltar aunque no afecte al resultado esperado. Por ejemplo, el «formato» de un menú en C06, o 5 o 6 problemas para «hola» en C11. Así se diluyen los problemas importantes.
3. **Se mezclan los tipos.** gpt-oss marca como «en el texto» problemas que en realidad son por ausencia: en C11 cita «hola» para «falta formato». Además, deja vacío el campo «qué falta» (C12).
4. **Se cuela otro idioma en las explicaciones**, por ejemplo «directive» o «una email höfliche». Esto afecta a RF-013.
5. **Latencia.** Ningún modelo gratuito de NVIDIA cumple los 30 s. Con el mensaje mínimo tardaban 1–2 s, así que el tiempo se va en generar el diagnóstico y en la cola del nivel gratuito.
6. **Lo que sí funciona:** citas literales, rechazos, ausencia de rechazos erróneos en C10 (Nemotron), resistencia a la inyección (Nemotron) y JSON válido en todas las respuestas recibidas.

### Ronda 2 (2026-10-19): fronteras y reglas de la spec 1.1 en el prompt de sistema

| Métrica | Objetivo | Nemotron R1 → R2 | gpt-oss R1 → R2 |
|---|---|---|---|
| Detección | ≥ 80 % | 70 % → 72 % ❌ | 83 % → **52 %** ❌ |
| Falsos positivos | ≤ 20 % | 52 % → **30 %** ❌ | 44 % → **13 %** ✅ |
| Citas literales | 100 % | ✅ | ✅ |
| Rechazos | 100 % | ✅ | ✅ |
| Tiempo p95 | < 30 s | 75 s ❌ | 67 s ❌ (2 tiempos agotados) |

**Hallazgos de la ronda 2:**
1. **Las fronteras funcionan para los falsos positivos.** Bajan mucho en los dos modelos.
2. **gpt-oss se vuelve demasiado prudente con «solo lo que impide el resultado esperado».** Deja de ver problemas reales: 0 de 3 en C04 y 1 de 4 en C01. Nemotron mantiene la detección.
3. **Agrupación.** Los modelos juntan varias carencias en un solo problema. En C06, por ejemplo: «sin gluten, 4 personas y presupuesto» en un único problema. La spec no dice si cada información que falta es un problema distinto o si se pueden agrupar. Hueco de la spec: granularidad.
4. **La regla «un defecto, un problema» no siempre se cumple.** En C14, Nemotron da 8 y además 2 para lo mismo.
5. **Idioma.** En C02, Nemotron explica en catalán, el idioma del prompt, y no en el idioma de la interfaz. Incumple RF-013.
6. **La latencia no mejora.** Es un límite del nivel gratuito de NVIDIA, no del prompt.

### Conclusión provisional

Ningún modelo cumple todavía la spec. Los fallos de calidad apuntan sobre todo a la **especificación** (catálogo con solapes) y al **prompt de sistema** (falta pedir solo los problemas relevantes para el resultado esperado). La latencia apunta al **proveedor**.

**Pendiente:**
- ~~Fronteras del catálogo (spec).~~ Hecho en la spec 1.1.
- ~~Ajuste del prompt de sistema.~~ Ronda 2.
- Decidir la granularidad (agrupar carencias o no).
- Probar proveedores gratuitos más rápidos (Gemini, Groq).
- Repetir el spike.
