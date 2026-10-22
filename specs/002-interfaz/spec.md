# Especificación: Interfaz atractiva e intuitiva

**Estado:** aprobada · **Versión:** 1.0 · **Aprobada:** 2026-10-22 por Àlex Marco · **Constitución:** 1.2 · **Depende de:** spec 001 v1.5

> Los identificadores continúan los de la spec 001 (RF-017 en adelante, RNF-012 en adelante) para que sean únicos en todo el proyecto.

## Contexto y objetivo

El incremento 001 funciona de extremo a extremo, pero la interfaz es básica. Al usarla, Àlex Marco detectó cuatro problemas:
- no se sabe si la app está trabajando mientras responde la IA;
- hay que copiar el resultado a mano;
- un fallo puntual del modelo («respuesta que no hemos podido entender») obliga al usuario a reintentar;
- el aspecto no invita a usarla.

El público objetivo son personas con poco dominio de la IA (principio 4), y la prueba con 5 de ellas (T060) depende de que la interfaz se entienda sin ayuda.

**Objetivo:** que cualquier persona complete el recorrido (escribir, revisar, responder y mejorar) **sin ayuda y con ganas de volver**. La app tiene que ser visualmente atractiva, pero **la claridad manda sobre la estética** cuando entren en conflicto.

## Historias de usuario (priorizadas)

### P1 · Saber en todo momento qué está pasando
Como persona que usa la app, quiero ver que está trabajando y no tener que lidiar con fallos puntuales de la IA, para confiar en ella y no abandonar.

**Prueba independiente:** con un modelo lento o que falla una vez, se comprueba que aparece un indicador de progreso y que el fallo puntual no llega al usuario.

**Criterios de aceptación:**
- Dado que pulso «Revisar» o «Mejorar», cuando la IA tarda, entonces veo enseguida un indicador de que se está trabajando, con un texto que dice qué paso se está haciendo.
- Dado que la IA devuelve una respuesta ilegible una vez, cuando la app lo detecta, entonces lo reintenta sola y yo solo veo el resultado.
- Dado que la IA falla también en el reintento, cuando termina, entonces veo el mensaje de error en lenguaje llano y mi texto sigue escrito (RF-014).
- Dado que hay una petición en curso, cuando vuelvo a pulsar el botón, entonces no se envía una segunda petición.

### P1 · Usar el resultado sin esfuerzo
Como persona que ha mejorado su prompt, quiero copiarlo con un clic, para pegarlo en mi herramienta de IA.

**Prueba independiente:** con una mejora ya mostrada, se pulsa «Copiar» y se comprueba el contenido del portapapeles.

**Criterios de aceptación:**
- Dado un prompt mejorado, cuando pulso «Copiar», entonces el texto exacto del prompt mejorado queda en el portapapeles y veo una confirmación breve.
- Dado un prompt mejorado con marcadores `[COMPLETAR: …]`, cuando lo copio, entonces la confirmación me recuerda que tengo que completarlos.

### P2 · Empezar sin saber qué escribir
Como persona sin experiencia, quiero ver ejemplos de prompts, para entender qué hace la app y probarla en segundos.

**Prueba independiente:** sin escribir nada, se elige un ejemplo y se comprueba que rellena los campos y se puede revisar directamente.

**Criterios de aceptación:**
- Dado que entro por primera vez, cuando miro la pantalla inicial, entonces veo ejemplos de prompts típicos en el idioma de la interfaz.
- Dado un ejemplo, cuando lo elijo, entonces se rellenan el prompt y el resultado esperado, y puedo pulsar «Revisar».

### P2 · Un recorrido fluido y guiado
Como persona que usa la app, quiero ver en qué paso estoy y pasar de uno a otro sin saltos, para no perderme.

**Prueba independiente:** se recorre todo el flujo y se comprueba que el paso actual se ve en todo momento y que lo ya hecho sigue visible.

**Criterios de aceptación:**
- Dado cualquier momento del recorrido, cuando miro la pantalla, entonces veo los pasos (1 Escribir, 2 Revisar, 3 Mejorar) y cuál es el actual.
- Dado que paso de un paso al siguiente, cuando aparece el resultado, entonces la pantalla no se queda en blanco ni pierde lo que ya había, y me lleva a la parte nueva.

### P2 · Una interfaz atractiva y coherente
Como persona que usa la app, quiero que sea agradable a la vista, para que me apetezca usarla y confiar en ella.

**Prueba independiente:** se revisa la interfaz con la guía visual aprobada y en los dos modos (claro y oscuro).

**Criterios de aceptación:**
- Dada la guía visual aprobada (colores, tipografía, nombre y logotipo), cuando abro cualquier pantalla, entonces la aplicación la respeta.
- Dado que mi sistema está en modo oscuro, cuando abro la app, entonces se muestra en modo oscuro, con el mismo contraste mínimo.

## Requisitos funcionales

- **RF-017:** Al iniciar una petición a la IA, el sistema debe mostrar un indicador de progreso con el nombre del paso en curso. (P1)
- **RF-018:** Si la IA devuelve una respuesta inválida, el sistema debe reintentarla automáticamente una vez antes de mostrar el error. Solo las respuestas inválidas: si el servicio no está disponible o tarda demasiado, reintentar solo alarga la espera. (P1)
- **RF-019:** Mientras haya una petición en curso, el sistema no debe enviar otra igual al pulsar de nuevo el botón. (P1)
- **RF-020:** El sistema debe ofrecer un botón «Copiar» que copie el texto exacto del prompt mejorado y confirme la acción, recordando los `[COMPLETAR: …]` si los hay. (P1)
- **RF-021:** La pantalla inicial debe ofrecer 4 ejemplos de prompts en el idioma de la interfaz que, al elegirlos, rellenen el prompt y el resultado esperado. (P2)
- **RF-022:** El sistema debe mostrar los pasos del recorrido y destacar el actual. (P2)
- **RF-023:** Al pasar de un paso al siguiente, el sistema debe conservar visible lo anterior y llevar la vista al contenido nuevo, sin dejar la pantalla en blanco. (P2)
- **RF-024:** La interfaz debe seguir una guía visual aprobada para la app **Sharpener**: logotipo, paleta, tipografía y componentes. (P2)
- **RF-025:** La interfaz debe adaptarse al modo claro u oscuro del sistema y ofrecer además un interruptor manual. (P2)

## Casos límite

- La IA tarda más de 30 s: el indicador sigue visible y, al final, aparece el error de tiempo agotado (RF-014) sin perder el texto.
- El navegador no permite copiar al portapapeles: se selecciona el texto y se indica cómo copiarlo a mano.
- El usuario cambia de idioma con un resultado en pantalla: se vuelve al inicio conservando el texto escrito (prompt y resultado esperado), porque las explicaciones ya generadas están en el idioma anterior.
- Pantalla pequeña (móvil de 360 px): el recorrido completo sigue siendo usable y la comparación original/mejorado se apila.
- El navegador bloquea los scripts: la app sigue funcionando como en el incremento 001, sin las mejoras que dependen de ellos.

## Requisitos no funcionales (con cifras)

- **RNF-012 · Intuitiva:** en la prueba con 5 personas (T060), al menos 4 completan el recorrido (revisar y mejorar un prompt propio) sin ayuda, en menos de 5 minutos desde que abren la app.
- **RNF-013 · Respuesta inmediata:** el indicador de progreso aparece en menos de 200 ms tras pulsar el botón.
- **RNF-014 · Accesible:** contraste mínimo WCAG 2.2 nivel AA (4,5:1 en texto normal) en los dos modos; todo el recorrido se puede hacer solo con teclado; cada control tiene una etiqueta legible por lectores de pantalla.
- **RNF-015 · Adaptable:** todo el recorrido se puede usar desde 360 px de ancho.
- **RNF-016 · Atractiva:** en la prueba T060, al menos 4 de 5 personas puntúan el aspecto con un 4 o más sobre 5.
- Siguen vigentes todos los RNF de la spec 001, en especial RNF-009 (sin persistencia) y RNF-010 (todo texto escapado).

## Entidades y glosario

- **Recorrido:** los pasos 1 Escribir → 2 Revisar (diagnóstico y preguntas) → 3 Mejorar (comparación y copia).
- **Sharpener:** nombre de la app («afilador»: afila los prompts). Decidido por Àlex Marco el 2026-10-22.
- **Guía visual:** documento con logotipo, paleta (claro y oscuro), tipografía y componentes de Sharpener, aprobado por Àlex Marco.
- **Ejemplo:** prompt típico, con su resultado esperado, pensado para enseñar qué hace la app. Sintético.

## Fuera de alcance

- Cuentas de usuario, historial y guardado (historial: spec futura).
- Publicar la app para otras personas (perfil C).
- Extensión de navegador (aplazada por decisión de Àlex Marco).
- Cambios en el diagnóstico o en la mejora: esta spec solo toca la interfaz.

## Supuestos y dudas abiertas

No quedan dudas abiertas.

### Registro de clarificaciones

| Fecha | Autor | Duda | Respuesta |
|---|---|---|---|
| 2026-10-22 | Àlex Marco | Nombre de la app | **Sharpener** |
| 2026-10-22 | Àlex Marco | ¿Modo oscuro? | Automático según el sistema, más un interruptor manual (RF-025) |
| 2026-10-22 | Àlex Marco | Reintento automático | Solo en respuestas inválidas (RF-018) |
| 2026-10-22 | Àlex Marco | Número de ejemplos | 4 (RF-021) |
| 2026-10-22 | Àlex Marco | Cambio de idioma con un resultado en pantalla | Volver al inicio conservando el texto escrito |
| 2026-10-22 | Àlex Marco | Scripts bloqueados | La app sigue funcionando sin las mejoras |
| 2026-10-22 | Àlex Marco | Tiempo del recorrido en T060 | Menos de 5 minutos (RNF-012) |
| 2026-10-22 | Àlex Marco | Medida de «atractiva» | 4 o más sobre 5 en al menos 4 de 5 personas (RNF-016) |

## Criterios de éxito

Contribuye al criterio de éxito 2 del one-pager (4 de 5 personas no expertas obtienen mejor resultado sin ayuda), que se medirá en la T060 junto con RNF-012 y RNF-016.
