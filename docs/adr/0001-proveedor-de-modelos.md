# ADR-0001: Proveedor de modelos de IA

**Estado:** aceptada · **Fecha:** 2026-10-19 · **Decide:** Àlex Marco

**Contexto:** el diagnóstico (spec 001, RF-003 a RF-016) necesita un modelo de lenguaje. Los requisitos que más pesan son:
- RNF-002: coste 0 €;
- RNF-001: p95 < 30 s;
- RNF-003: detección ≥ 80 % y falsos positivos ≤ 20 %;
- RNF-004: citas literales;
- RF-015: rechazos;
- RF-013: explicaciones en el idioma de la interfaz.

El principio 7 de la constitución exige independencia del proveedor. La evidencia completa está en `specs/001-diagnostico-prompt/research.md`.

**Opciones consideradas:**
- **A · NVIDIA, Nemotron 3 Super (gratuito).**
  - A favor: citas y rechazos correctos, y buena resistencia a la inyección.
  - En contra: p95 de 75 s, 30 % de falsos positivos, a veces explica en el idioma del prompt, y muchos modelos del catálogo no están disponibles o no responden.
- **B · NVIDIA, gpt-oss-20b (gratuito).**
  - En contra: p95 de 67 s, tiempos agotados frecuentes y detección inestable (83 % → 52 % según el prompt).
- **C · Gemini 3.5 Flash-Lite (gratuito, Google AI Studio).**
  - A favor: p95 de 7 s, 19 % de falsos positivos, citas y rechazos correctos, y explicaciones en español llano dirigidas al usuario.
  - En contra: detección del 66 %; el nivel gratuito tiene límites de uso y condiciones que Google puede cambiar.
- **D · Gemini 3.8 Flash (gratuito).** Sin cuota en el nivel gratuito de la cuenta: 429 persistente.
- **E · Claude Haiku 5.5 (de pago, unos 0,001 $ por diagnóstico).** Descartada por decisión del responsable (presupuesto 0 €).

**Decisión:** **C, Gemini 3.5 Flash-Lite**, a través de su API compatible con OpenAI y detrás de un puerto propio (`ModeloIA`). **A** queda como alternativa configurable: el mismo adaptador sirve para los dos, porque NVIDIA también es compatible con OpenAI.

**Consecuencias:**
- ✅ Se cumplen RNF-001, RNF-002, RNF-004 y RF-015, y los falsos positivos de RNF-003.
- ❌ La detección (66 %) no cumple todavía RNF-003. Se trabaja en el diseño del diagnóstico (ADR-0003) y se verifica con evals. Si no se alcanza, se reabre esta decisión.
- ⚠️ Dependencia de un nivel gratuito externo. El cambio de proveedor queda en un solo adaptador y en la configuración, sin tocar el dominio. Los errores 429/503 se tratan según RF-014.
- ⚠️ Lo que el usuario escribe se envía a Google. RF-006 obliga a mostrarlo antes de enviar. Al abrir la app a otras personas, se revisa en la Fase 8 (condiciones de uso de datos del nivel gratuito).
