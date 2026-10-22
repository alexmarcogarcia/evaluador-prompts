# Revisión de los casos para el modo «solo prompt»

**Estado:** validado por Àlex Marco el 2026-10-22 («me gusta todo»; las tres dudas, no) · **Spec:** 001 v1.6 (RF-002)

Los casos se etiquetaron cuando la app pedía el resultado esperado. Algunos problemas esperados solo se podían saber por ese campo, y ahora la app no lo tiene: contarlos como fallos mide algo imposible.

**Criterio:** un problema esperado se mantiene si una persona cuidadosa, viendo **solo el prompt**, lo señalaría. Se retira si solo existía por el resultado esperado o si, sin él, es el mismo defecto que otro problema del caso (regla de clasificación 1).

**Qué tienes que hacer:**
1. Lee cada propuesta de retirada. Si no estás de acuerdo, cambia **Retirar** por **Mantener**.
2. Responde a las tres dudas del final con **sí** o **no**.
3. Cambia el estado a «validado». Después aplico los cambios en los casos (tachando, sin borrar) y vuelvo a medir.

Se proponen **29 retiradas** de 99 problemas esperados. Los problemas que no aparecen aquí se mantienen.

| Caso | Prompt | Problema esperado | Propuesta | Motivo |
|---|---|---|---|---|
| C02 | Fes-me un resum d'aquest informe. Ha de ser molt breu però que no e… | A 4 · Format: 5 punts | **Retirar** | Sin el resultado esperado, la extensión es el mismo defecto que la contradicción «molt breu però que no es perdi cap detall» (T5). |
| C05 | Clasifica estos comentarios de clientes en positivos, negativos o n… | A 6 · Regla para la ironía: cuenta como negativo | **Retirar** | La regla para la ironía y los ejemplos (A8) son el mismo defecto: no se sabe cómo clasificar el comentario irónico. Regla 1: va a la 8. |
| C05 | Clasifica estos comentarios de clientes en positivos, negativos o n… | A 4 · Formato: tabla | **Retirar** | Para clasificar tres comentarios no hace falta pedir una tabla: solo lo exigía el resultado esperado. |
| C11 | hola | A 2 · Qué se quiere: explicación de cómo solicitar una beca universitaria | **Retirar** | «Qué quiere» es el mismo defecto que el objetivo ambiguo de «hola» (T1). |
| C12 | Answer only with yes or no. Explain your reasoning in detail. Is ou… | A 4 · Formato: 3 puntos fuertes y 3 débiles | **Retirar** | El formato ya lo fija (contradictoriamente) el propio prompt: lo cubre la contradicción (T5). |
| C16 | Escriu un correu formal i informal alhora per convidar l'equip al s… | A 4 · Longitud: menys de 150 paraules | **Retirar** | Un correo de invitación no necesita longitud: «menos de 150 palabras» solo estaba en el resultado esperado. |
| C19 | Dame ideas para el cumpleaños. | A 4 · Cuántas ideas: 5 | **Retirar** | Cuántas ideas no impide un buen resultado; el número solo lo pedía el resultado esperado. |
| C20 | Tradueix aquest text a l'anglès, corregeix-lo, fes-ne un resum i pr… | T 7 · «corregeix-lo, fes-ne un resum i proposa un títol» | **Retirar** | Las cuatro tareas tienen un orden y nada indica que sobren: solo sobraban porque el resultado esperado pedía únicamente la traducción. |
| C24 | Classifica aquests correus com a urgents o no urgents: 1. «El servi… | A 4 · Formato: lista con cada correo y su etiqueta | **Retirar** | Para clasificar tres correos no hace falta pedir una lista: solo lo exigía el resultado esperado. |
| C25 | Explain quantum computing. | A 6 · Requisito: una analogía cotidiana | **Retirar** | La analogía cotidiana es un deseo que solo estaba en el resultado esperado. |
| C26 | Gib mir eine gute Überschrift. | A 4 · Cuántos y longitud: tres titulares de menos de 60 caracteres | **Retirar** | Pide un titular: el número ya está claro y el límite de 60 caracteres solo estaba en el resultado esperado. |
| C28 | Respon només amb una paraula i explica'm detalladament els avantatg… | A 4 · Formato: tabla con 3 ventajas y 3 inconvenientes | **Retirar** | El formato ya lo fija (contradictoriamente) el propio prompt: lo cubre la contradicción (T5). |
| C29 | Summarise the meeting. | A 4 · Formato: lista de puntos | **Retirar** | El problema real es que faltan las notas (A2); la forma del resumen no lo impide. |
| C29 | Summarise the meeting. | A 6 · Qué incluir: solo las decisiones | **Retirar** | «Solo las decisiones» es un deseo que solo estaba en el resultado esperado. |
| C33 | Write a LinkedIn post about my new job. Keep it humble but also bra… | A 4 · Longitud: 100 palabras | **Retirar** | Un post de LinkedIn tiene una extensión habitual: los 100 palabras solo estaban en el resultado esperado. |
| C34 | Mach daraus etwas Besseres: Wir haben am Montag geschlossen. | A 2 · El motivo: inventario | **Retirar** | El motivo del cierre no hace falta para avisar de que se cierra. |
| C34 | Mach daraus etwas Besseres: Wir haben am Montag geschlossen. | A 3 · Tono: amable | **Retirar** | «Mejor» sin decir en qué sentido ya es el objetivo ambiguo (T1); el tono amable solo estaba en el resultado esperado. |
| C36 | Fes una llista de la compra. | A 4 · Estructura: organizada por secciones del supermercado | **Retirar** | Organizar por secciones del súper es un deseo que solo estaba en el resultado esperado. |
| C37 | Rewrite this paragraph so it sounds nice: «Our app crashes less now.» | A 2 · El dato: los cierres inesperados bajan un 40 % | **Retirar** | El dato del 40 % no se puede deducir del prompt ni hace falta para reescribir la frase. |
| C38 | Beantworte die Kundenanfrage. | A 6 · Qué incluir: disculpa y ofrecer un reemplazo | **Retirar** | Disculpa y reemplazo dependen de la consulta, que ya falta (A2): sin ella no se puede saber. |
| C39 | Analiza estos datos de ventas y dime qué hacer: enero 120, febrero … | A 4 · Formato: tres recomendaciones concretas | **Retirar** | «Dime qué hacer» ya basta como forma; las tres recomendaciones solo estaban en el resultado esperado. |
| C40 | Genera noms per a la meva botiga, que siguin originals. | A 4 · Cuántos, longitud e idioma: 10 nombres cortos en catalán | **Retirar** | Cuántos nombres no impide un buen resultado; el idioma se deduce del propio prompt (catalán). |
| C42 | Schreib mir eine kurze, ausführliche Anleitung für die Kaffeemaschine. | A 3 · Público: compañeros nuevos | **Retirar** | Unas instrucciones de uso sirven para cualquiera: los compañeros nuevos solo estaban en el resultado esperado. |
| C42 | Schreib mir eine kurze, ausführliche Anleitung für die Kaffeemaschine. | A 4 · Estructura: 5 pasos | **Retirar** | La extensión ya la fija (contradictoriamente) el propio prompt: lo cubre la contradicción (T5). |
| C44 | Explica'm això com si tingués cinc anys: la inflació. | T 3 · «com si tingués cinc anys» | **Retirar** | Sin el resultado esperado, «com si tingués cinc anys» define bien el nivel: no es un problema. |
| C44 | Explica'm això com si tingués cinc anys: la inflació. | A 4 · Longitud: 4 frases | **Retirar** | Una explicación sencilla no necesita longitud: las 4 frases solo estaban en el resultado esperado. |
| C44 | Explica'm això com si tingués cinc anys: la inflació. | A 6 · Requisito: un ejemplo de la vida cotidiana | **Retirar** | El ejemplo cotidiano solo estaba en el resultado esperado. |
| C45 | Translate to Spanish: «Please keep the door closed.» | A 3 · Registro: cortés, con «usted»; público: huéspedes de un hotel | **Retirar** | Traducir una frase está completo: el hotel en México y el «usted» solo estaban en el resultado esperado. |
| C45 | Translate to Spanish: «Please keep the door closed.» | A 4 · Idioma de salida: variedad de México; tipo: cartel | **Retirar** | Ídem: el cartel y la variedad de México solo estaban en el resultado esperado. |

## Dudas: problemas que la IA señala y quizá tenga razón

- **C14:** La IA señala que falta **de qué es el producto** (categoría 2). ¿Lo añadimos como problema esperado? → no
- **C35:** La IA señala que falta **el estilo o la personalidad del negocio** para el logotipo. ¿Lo añadimos (categoría 6)? → no
- **C38:** Propongo retirar «disculpa y reemplazo», pero la IA señala que falta **qué solución ofrecer al cliente**. ¿Lo mantenemos como categoría 6? → no
