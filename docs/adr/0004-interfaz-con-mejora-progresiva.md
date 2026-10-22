# ADR-0004: Interfaz con mejora progresiva

**Estado:** aceptada · **Fecha:** 2026-10-22 · **Decide:** Àlex Marco · **Spec:** 002

**Contexto:** la spec 002 pide varias cosas:
- un indicador de progreso inmediato (RF-017, RNF-013);
- no enviar dos veces (RF-019);
- copiar con un clic (RF-020);
- pasar de un paso a otro sin saltos (RF-023);
- modo oscuro con interruptor (RF-025);
- una guía visual con tipografías propias (RF-024).

Además, la app **tiene que seguir funcionando aunque el navegador bloquee los scripts** (caso límite de la spec). El ADR-0002 eligió páginas HTML generadas en el servidor con FastAPI y Jinja2, y ya hay 138 pruebas sobre ese recorrido.

**Opciones consideradas:**
- **A · Mejora progresiva.** Se mantienen las páginas del servidor y se añade un archivo pequeño de JavaScript propio, sin frameworks, que mejora lo que ya funciona: intercepta el envío del formulario, muestra el progreso, sustituye el contenido sin recargar y copia al portapapeles. Sin scripts, todo sigue funcionando como en el incremento 001.
  - A favor: cumple el caso límite por construcción; reutiliza el servidor y sus pruebas; muy poco código (principio 8).
  - En contra: algo de lógica en el navegador que hay que probar a mano o con un navegador real.
- **B · Aplicación de una sola página (React o similar) que consume una API JSON.**
  - A favor: más control sobre las transiciones.
  - En contra: duplica la lógica de presentación; añade dependencias, compilación y otro lenguaje; **no funciona sin scripts**, lo que incumple la spec; obliga a rehacer las pruebas de la interfaz.
- **C · htmx o una librería parecida.**
  - A favor: poco código propio.
  - En contra: una dependencia externa para algo que se hace con unas decenas de líneas propias.

**Decisión:** **A**, con tres reglas:
1. **El servidor manda.** Toda pantalla se genera en el servidor. El JavaScript solo pide la misma página por detrás y sustituye el contenido; nunca construye HTML con datos del usuario, así que el autoescape de Jinja2 sigue cubriendo el RNF-010.
2. **Tipografías servidas por la propia app.** Bricolage Grotesque y Figtree, con licencia SIL OFL, se sirven como archivos propios con su licencia incluida, y no desde Google Fonts, que conocería la IP de cada usuario (RNF-006, amenaza A6).
3. **El reintento automático (RF-018) va en el servidor**, dentro de los casos de uso: funciona también sin scripts y lo cubren las pruebas de aceptación.

Además, **nada del usuario viaja en la dirección (URL)**. El cambio de idioma que conserva el texto escrito se hace con un envío POST, no con un enlace con parámetros. Una URL con el prompt acabaría en el historial del navegador y en los registros del servidor (RNF-006).

**Consecuencias:**
- ✅ La app funciona sin scripts. Con scripts, gana el progreso, la copia, las transiciones y el interruptor de tema.
- ✅ Las pruebas existentes siguen valiendo; la parte nueva del servidor se prueba igual.
- ⚠️ El JavaScript (copiar, progreso, sustitución) no lo cubren las pruebas automáticas actuales. Se verifica con una lista de comprobación manual en navegador, y se reconsiderará añadir pruebas con un navegador real si el JavaScript crece.
- ⚠️ Las tipografías añaden unos 100–200 KB a la primera carga, con caché después.
