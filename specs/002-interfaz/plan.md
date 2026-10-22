# Plan: Interfaz atractiva e intuitiva

**Especificación:** `specs/002-interfaz/spec.md` v1.0 · **Guía visual:** `specs/002-interfaz/guia-visual.md` · **Estado:** propuesta (las decisiones del ADR-0004 están aprobadas)

## Resumen técnico

Mejora progresiva sobre la interfaz actual (ADR-0004):
- **El servidor** sigue generando todas las pantallas. Añade el reintento automático (RF-018), los pasos del recorrido (RF-022), los ejemplos (RF-021) y la guía visual (RF-024).
- **Un archivo JavaScript propio y pequeño** (`static/sharpener.js`) añade el progreso inmediato (RF-017), el bloqueo del doble envío (RF-019), la copia (RF-020), la sustitución sin recarga con desplazamiento al contenido nuevo (RF-023) y el interruptor de tema (RF-025).
- **Sin scripts**, la app funciona como en el incremento 001, con el modo oscuro automático del sistema.

## Contexto técnico

| Aspecto | Decisión |
|---|---|
| Plantillas | Jinja2 con autoescape, como hasta ahora. La plantilla se divide en partes reutilizables (barra, pasos, diagnóstico, mejora) |
| Estilos | `static/sharpener.css`, con los tokens de la guía visual (claro y oscuro) y sin colores literales en los componentes |
| JavaScript | `static/sharpener.js`, sin dependencias. `fetch` del mismo formulario y sustitución del `<main>` |
| Tipografías | Bricolage Grotesque y Figtree en `static/fuentes/` (woff2) con sus licencias OFL. Sin Google Fonts |
| Archivos estáticos | `StaticFiles` de FastAPI (Starlette), sin dependencias nuevas |
| Reintento | En `Diagnosticar` y `Mejorar`: un reintento solo ante `RESPUESTA_INVALIDA` |
| Contraste | Prueba automática que lee los tokens de `sharpener.css` y calcula el contraste de cada par (RNF-014) |

## Comprobación de la constitución

| Principio | ¿Se cumple? | Cómo |
|---|---|---|
| 1 La especificación manda | ✅ | Cada tarea apunta a un RF o RNF de la spec 002 |
| 4 Comprensible para no expertos | ✅ | Lo miden RNF-012 y RNF-016 en la T060 |
| 7 Independencia del proveedor | ✅ | La interfaz no toca la IA; el reintento está en los casos de uso |
| 8 Simplicidad | ✅ | Sin frameworks ni dependencias nuevas (ADR-0004) |
| 9 Pruebas antes que implementación | ✅ / ⚠️ | Servidor con pruebas automáticas primero; el JavaScript con lista de comprobación manual (excepción justificada en el ADR-0004) |
| 10 Ni secretos ni datos de usuario donde no deben | ✅ | Tipografías locales, sin datos en la URL (cambio de idioma por POST), sin almacenamiento salvo la preferencia de tema en el navegador |

## Estructura

```
src/evaluador/adaptadores/web/
  app.py                     # + rutas /idioma (POST) y /static
  ejemplos.py                # los 4 ejemplos por idioma (RF-021)
  plantillas/
    base.html                # barra, pasos, pie
    pagina.html              # recorrido completo
    partes/                  # diagnóstico, mejora, ejemplos
  static/
    sharpener.css · sharpener.js · logo.svg
    fuentes/                 # woff2 y OFL.txt
  i18n/{es,ca,en,de}.json    # + textos nuevos
```

## Decisiones

- [ADR-0002](../../docs/adr/0002-tipo-de-aplicacion.md) · Web con FastAPI (se mantiene).
- [ADR-0004](../../docs/adr/0004-interfaz-con-mejora-progresiva.md) · Interfaz con mejora progresiva.

## Trazabilidad

| Requisito | Componente | Prueba |
|---|---|---|
| RF-017 indicador de progreso | `sharpener.js`, plantilla (región `aria-live`) | aceptación (marcado presente) + comprobación manual |
| RF-018 reintento ante respuesta inválida | `casos_uso/diagnosticar.py`, `casos_uso/mejorar.py` | aceptación con un modelo falso que falla una vez |
| RF-019 sin doble envío | `sharpener.js` | comprobación manual |
| RF-020 copiar | `sharpener.js`, plantilla | aceptación (botón y texto exacto en `data-`) + manual |
| RF-021 cuatro ejemplos por idioma | `ejemplos.py`, plantilla | aceptación (4 por idioma, rellenan los campos) |
| RF-022 pasos del recorrido | plantilla | aceptación (paso actual marcado en cada pantalla) |
| RF-023 sin saltos y desplazamiento al contenido nuevo | `sharpener.js` | comprobación manual |
| RF-024 guía visual | `sharpener.css`, logotipo, tipografías | revisión con la guía + prueba de que no se carga nada de Google |
| RF-025 modo oscuro e interruptor | `sharpener.css`, `sharpener.js` | aceptación (tokens oscuros e interruptor) + manual |
| RNF-012 intuitiva | toda la interfaz | T060 |
| RNF-013 progreso en < 200 ms | `sharpener.js` (síncrono al enviar) | comprobación manual |
| RNF-014 accesible AA | tokens, foco, etiquetas | **prueba de contraste automática** + revisión con teclado |
| RNF-015 desde 360 px | CSS | comprobación manual a 360 px |
| RNF-016 atractiva | guía visual | T060 |

## Pendiente de la decisión sobre RF-002

La pantalla de inicio (campo «Qué resultado esperas», ejemplos) depende de si el resultado esperado pasa a ser opcional (spec 001, RF-002, medición en curso). Por eso las tareas de la pantalla de inicio van al final.

## Quickstart de la spec 002

1. Abrir la app: barra con el logotipo, pasos con «1 Escribir» marcado y cuatro ejemplos.
2. Elegir un ejemplo: se rellenan los campos.
3. Pulsar «Revisar»: el progreso «Afilando tu prompt…» aparece al instante; los fragmentos se marcan con el fosforito.
4. Pulsar «Mejorar» y luego «Copiar»: aparece «Copiado» y el portapapeles contiene el prompt mejorado.
5. Cambiar a modo oscuro con el interruptor y volver a recorrerlo.
6. Repetirlo con los scripts desactivados: todo funciona, salvo copiar con un clic.
