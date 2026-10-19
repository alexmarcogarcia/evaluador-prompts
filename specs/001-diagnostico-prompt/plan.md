# Plan: Diagnóstico y mejora de un prompt

**Especificación:** `specs/001-diagnostico-prompt/spec.md` v1.4 · **Estado:** aprobado · **Aprobado:** 2026-10-19 por Àlex Marco

## Resumen técnico

Aplicación web local en Python (ADR-0002) con arquitectura limpia. Un caso de uso **Diagnosticar** hace una llamada al modelo, que devuelve:
- los problemas detectados,
- las preguntas aclaratorias,
- o un rechazo.

Un caso de uso **Mejorar** hace una segunda llamada con el diagnóstico y las respuestas del usuario y devuelve la versión mejorada, cuyos cambios van ligados a los problemas.

El dominio valida en código todo lo que la spec exige con carácter absoluto: citas literales, tipos, catálogo, límites y vínculo entre cambios y problemas. Así no depende del modelo (ADR-0003). El modelo es Gemini 3.5 Flash-Lite, detrás del puerto `ModeloIA` (ADR-0001).

## Contexto técnico

| Aspecto | Decisión |
|---|---|
| Lenguaje | Python 3.13 (constitución) |
| Web | FastAPI + plantillas Jinja2 + JavaScript mínimo (ADR-0002) |
| Cliente del modelo | SDK `openai`, apuntando al endpoint compatible de Gemini. El mismo adaptador sirve para NVIDIA (ADR-0001) |
| Validación de datos | Pydantic, que ya viene con FastAPI, para el contrato del diagnóstico |
| Diferencias original/mejorado (RF-011) | `difflib`, de la biblioteca estándar |
| Traducción de la interfaz (RF-013) | Un archivo JSON de textos por idioma (`es`, `ca`, `en`, `de`) |
| Almacenamiento | Ninguno en este incremento: el historial queda fuera de alcance |
| Pruebas | pytest. Evals con un script propio sobre `evals/` |
| Calidad | ruff (linter y formato) y mypy (tipos), en la CI |
| Configuración | Variables de entorno desde `.env` (claves, proveedor, modelo) |
| Plataforma | Local, en `localhost`. La publicación se trata en el perfil C |

Las versiones exactas se fijan en la Fase 7 (harness).

## Comprobación de la constitución

| Principio | ¿Se cumple? | Cómo / excepción |
|---|---|---|
| 1 La especificación manda | ✅ | Cada componente se traza a un RF (tabla de trazabilidad) |
| 2 Explicar, no solo reescribir | ✅ | Cada cambio de la versión mejorada referencia problemas; el dominio lo valida |
| 3 Preguntar antes que suponer | ✅ | Preguntas en el diagnóstico; marcadores `[COMPLETAR: …]` si se omiten (RF-010) |
| 4 Comprensible para no expertos | ✅ | El prompt de sistema pide lenguaje llano; se mide en la prueba con usuarios (RNF-005) |
| 5 La calidad se mide | ✅ | Evals versionadas; el prompt de sistema es un archivo versionado (ADR-0003) |
| 6 Coste cero | ✅ | Nivel gratuito de Gemini; se registran los tokens por llamada |
| 7 Independencia del proveedor | ✅ | Puerto `ModeloIA` y un adaptador compatible con OpenAI |
| 8 Simplicidad | ✅ | Sin base de datos ni frameworks de agentes; la estrategia de detección más simple que cumpla |
| 9 Pruebas antes que implementación | ✅ | Ver `tasks.md` (Fase 6) |
| 10 Ni secretos ni datos de usuario donde no deben | ✅ | Claves en `.env`; los logs registran métricas, nunca el texto de los prompts (RNF-006) |

## Estructura del código

```
src/evaluador/
  dominio/            # sin dependencias externas
    modelos.py        # Prompt, Problema, Categoria, TipoProblema, Gravedad, Diagnostico,
                      # Pregunta, VersionMejorada, Cambio
    reglas.py         # validación: citas literales, tipos, catálogo, límites, vínculos
  casos_uso/
    diagnosticar.py   # RF-001..008, 015, 016
    mejorar.py        # RF-009..012
  puertos/
    modelo_ia.py      # interfaz ModeloIA (Protocol)
  adaptadores/
    modelo_openai_compatible.py   # Gemini / NVIDIA
    web/              # FastAPI: rutas, plantillas, estáticos, i18n/{es,ca,en,de}.json
  prompts/            # prompts de sistema versionados (diagnostico.md, mejora.md)
  composicion.py      # único punto donde se conectan las implementaciones
tests/
  unit/ contract/ integration/ acceptance/
evals/
  casos/              # parte de specs/001-diagnostico-prompt/casos-prueba.md y lo amplía
  ejecutar.py         # mide RNF-003, 004 y 007
```

## Contratos

- `contracts/diagnostico.schema.json`: respuesta del modelo al diagnosticar. Pendiente de escribir en la tarea base.
- `contracts/mejora.schema.json`: respuesta del modelo al mejorar, con una lista de cambios y los identificadores de los problemas que resuelve cada uno.

Las pruebas de contrato comprueban que el adaptador transforma cualquier respuesta válida en entidades del dominio y que rechaza las inválidas.

## Decisiones

- [ADR-0001](../../docs/adr/0001-proveedor-de-modelos.md) · Proveedor de modelos: Gemini 3.5 Flash-Lite (aceptada).
- [ADR-0002](../../docs/adr/0002-tipo-de-aplicacion.md) · Tipo de aplicación: web con FastAPI (aceptada).
- [ADR-0003](../../docs/adr/0003-diseno-del-diagnostico.md) · Diseño del diagnóstico: validación en código y estrategia de detección por evals (aceptada).

## Trazabilidad

| Requisito | Componente | Prueba |
|---|---|---|
| RF-001 longitud ≤ 8.000 | `dominio/reglas.py` | unit |
| RF-002 resultado esperado obligatorio | `casos_uso/diagnosticar.py` | unit + aceptación P1 |
| RF-003 problemas con tipo, categoría, explicación, gravedad | `dominio/modelos.py`, contrato | contract + unit |
| RF-004 catálogo y fronteras | `prompts/diagnostico.md`, `dominio/reglas.py` | unit (catálogo) + evals |
| RF-005 sin problemas → decirlo | `casos_uso/diagnosticar.py`, web | aceptación (C07) |
| RF-006 mostrar proveedor y modelo antes de enviar | `adaptadores/web` | aceptación |
| RF-007 ≤ 5 preguntas | `dominio/reglas.py` | unit |
| RF-008 responder u omitir | `adaptadores/web`, `casos_uso/mejorar.py` | aceptación P2 |
| RF-009 cambios ligados a problemas | `dominio/reglas.py`, `casos_uso/mejorar.py` | unit + contract |
| RF-010 marcador si se omite una pregunta | `casos_uso/mejorar.py` | unit + aceptación P2 |
| RF-011 original y mejorado con diferencias | `adaptadores/web` (difflib) | unit + aceptación P3 |
| RF-012 original intacto | `dominio/modelos.py` (inmutable) | unit |
| RF-013 4 idiomas de interfaz; mejora en el idioma del prompt | `adaptadores/web/i18n`, prompts | unit (claves i18n completas) + evals |
| RF-014 errores del proveedor | adaptador del modelo, web | integration |
| RF-015 rechazo | `casos_uso/diagnosticar.py`, prompt | evals (RNF-007) + aceptación (C09) |
| RF-016 solo lo relevante, un defecto una vez | prompt, `dominio/reglas.py` | evals |
| RNF-001 p95 < 30 s | adaptador (timeout) | evals (latencia) |
| RNF-003 / 004 / 007 | todo el diagnóstico | evals |
| RNF-006 logs solo con métricas | logging del adaptador | unit |
| RNF-008 solo 127.0.0.1 | `composicion.py` (arranque del servidor) | unit (configuración) |
| RNF-009 sin persistencia | todo `src/` (sin escrituras a disco) | revisión + unit |
| RNF-010 contenido escapado | `adaptadores/web` (autoescape de Jinja2) | aceptación con `<script>` |
| RNF-011 no inventar en la mejora | `prompts/mejora.md` | evals de la mejora con juez calibrado |

## Quickstart (validación de extremo a extremo)

1. Arrancar la app y abrir `http://localhost:8000` en español.
2. Pegar el prompt de C01 y su resultado esperado. Ver el proveedor y el modelo antes de enviar.
3. Recibir en menos de 30 s el diagnóstico con «que esté bien» marcado y las carencias de destinatario y formato.
4. Responder una pregunta y omitir otra.
5. Recibir la versión mejorada: cada cambio con su problema, el original intacto al lado, las diferencias marcadas y un `[COMPLETAR: …]` para la pregunta omitida.
