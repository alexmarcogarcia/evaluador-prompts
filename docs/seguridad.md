# Seguridad y confidencialidad

**Fase:** 8 · **Perfil:** B, con el rigor de seguridad de C al abrirse a otras personas · **Alcance:** spec 001, ejecución local · **Fecha:** 2026-10-19 · **Estado:** aprobada por Àlex Marco (requisitos en la spec 1.3)

Revisión rápida de amenazas (perfil B): qué datos entran, dónde se guardan y quién accede. Las reglas permanentes están en la constitución (sección «Confidencialidad y seguridad»). Aquí se aplican al primer incremento.

## Datos

| Dato | Clasificación | Dónde está | Quién accede |
|---|---|---|---|
| Claves de API (Gemini, NVIDIA) | Confidencial | `.env` en el equipo, excluido de git | El propietario del equipo |
| Prompt y resultado esperado del usuario | Datos de usuario: pueden contener datos personales | Memoria del proceso mientras dura la petición; se envía a Google por HTTPS | El usuario y **Google, según las condiciones del nivel gratuito** |
| Diagnóstico y versión mejorada | Datos de usuario | Memoria del proceso y página del navegador | El usuario |
| Registros (logs) | Interna | Consola del proceso | El propietario del equipo |
| Evals y casos de prueba | Pública (sintéticos) | Repositorio | Cualquiera |

**Flujo:** navegador → app en `127.0.0.1` → API de Gemini (HTTPS) → app → navegador. No hay base de datos ni archivos con datos de usuario.

> ⚠️ **Condiciones del nivel gratuito.** En los servicios gratuitos de la API de Gemini, Google puede usar el contenido enviado para mejorar sus productos, e incluso que lo revisen personas. Hay que verificarlo en las condiciones vigentes de Google AI Studio. **Consecuencia:** no se deben introducir datos personales ni confidenciales en los prompts. La app lo avisa antes de enviar (RF-006).

## Amenazas y respuesta

| ID | Amenaza | Probabilidad / impacto | Respuesta | Dónde se verifica |
|---|---|---|---|---|
| A1 | Filtración de una clave de API (repositorio, logs, capturas, chats) | Media / Medio | `.env` ignorado; gitleaks sobre todo el historial en la CI; regla en `AGENTS.md`; las claves nunca se registran | CI (secretos) |
| A2 | Otro equipo de la red local usa la app y la cuota de la clave | Baja / Medio | La app solo escucha en `127.0.0.1` (RNF-008) | Prueba de configuración del servidor |
| A3 | **XSS:** el prompt del usuario o la respuesta del modelo contienen HTML o JavaScript que se ejecuta al mostrarlos | Media / Medio | Autoescape de Jinja2 siempre activo; prohibido `\|safe` o `innerHTML` con contenido del usuario o del modelo (RNF-010) | Prueba de aceptación con un prompt que contiene `<script>` |
| A4 | Inyección de instrucciones en el prompt analizado | Media / Medio | Regla en el prompt de sistema, validación en código (ADR-0003) y casos de inyección en las evals | Evals (C08 y ampliación en T022) |
| A5 | Datos del usuario en logs | Media / Medio | Solo se registran métricas: duración, tokens, proveedor, modelo y código de error. Nunca texto (RNF-006, ampliado) | Prueba unitaria del logging |
| A6 | Datos personales enviados a un tercero sin saberlo | Media / Medio | Aviso antes de enviar, con el proveedor y la recomendación de no incluir datos personales (RF-006, ampliado) | Prueba de aceptación |
| A7 | Peticiones dañinas a través de la app | Baja / Medio | Rechazo (RF-015) | Evals (RNF-007) |
| A8 | Dependencia con vulnerabilidad conocida | Media / Medio | Versiones fijadas y `pip-audit` en `check.py` y en la CI | CI (comprobaciones) |
| A9 | Persistencia accidental de datos del usuario | Baja / Medio | Sin almacenamiento en este incremento (RNF-009) | Revisión: no hay escrituras a disco en `src/` |

**Aceptado sin respuesta en perfil B:**
- CSRF y autenticación. La app es de un solo usuario, local y sin acciones peligrosas: lo peor que se puede provocar es un diagnóstico.
- Límites de uso por persona.

Se revisa todo al publicar (perfil C, riesgo R-05).

## Preguntas de control (guía)

- **¿Qué dato sería más grave que se filtrara?** Hoy, las claves de API, porque permitirían usar la cuota a tu nombre. Son gratuitas, así que no hay cargos. Al publicar, lo más grave serían los prompts de otras personas.
- **¿Quién puede verlo hoy?** Las claves, solo quien tiene acceso a tu equipo. Los prompts, tú y Google.
- **¿Qué pasa si se pierde una credencial a las 3 de la mañana?**
  1. Revocar la clave en https://aistudio.google.com (o en https://build.nvidia.com).
  2. Crear una nueva y pegarla en `.env`.

  No hay facturación asociada, así que el impacto es bajo y la respuesta puede esperar a la mañana.

## Licencias

| Dependencia | Licencia | Dependencia | Licencia |
|---|---|---|---|
| fastapi | MIT | pydantic | MIT |
| uvicorn | BSD-3-Clause | python-dotenv | BSD-3-Clause |
| jinja2 | BSD-3-Clause | pytest (dev) | MIT |
| python-multipart | Apache-2.0 | httpx (dev) | BSD-3-Clause |
| openai | Apache-2.0 | ruff, mypy (dev) | MIT |
| pip-audit (dev) | Apache-2.0 | | |

Todas son permisivas y compatibles con un proyecto público. **Licencia del propio proyecto: MIT** (`LICENSE`), elegida por Àlex Marco el 2026-10-19.

## Escaneo automático activo

- Secretos: gitleaks en la CI, sobre todo el historial.
- Dependencias vulnerables: pip-audit en `scripts/check.py` y en la CI.
- Licencias: tabla de este documento, revisada cuando cambia una dependencia.
