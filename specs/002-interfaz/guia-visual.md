# Guía visual de Sharpener

**Estado:** aprobada · **Versión:** 1.0 · **Aprobada:** 2026-10-22 por Àlex Marco · **Spec:** 002 (RF-024, RF-025)

Dirección **B · Grafito**, elegida entre tres propuestas generadas con UI UX Pro Max y filtradas con los criterios de Taste Skill. Las propuestas están en el artefacto «Sharpener: tres direcciones».

## Idea

Un lápiz recién afilado. Grises de grafito y **un único amarillo de lápiz**, que funciona como un rotulador fosforito sobre el texto del usuario: marca lo que falla en su prompt. Es el elemento que solo tiene Sharpener, y se entiende sin explicación: «esto es lo importante».

**La claridad manda sobre la estética** (spec 002). Si un adorno compite con entender la pantalla, se quita.

## Logotipo

Un lápiz en diagonal: cuerpo amarillo y punta de grafito, seguido de «Sharpener» en la tipografía de títulos (800).

```svg
<svg viewBox="0 0 32 32" aria-hidden="true">
  <path d="M3 22 L22 3 L29 10 L10 29 Z" fill="var(--amarillo)"/>
  <path d="M3 22 L10 29 L3 29 Z" fill="currentColor"/>
</svg>
```

Siempre a la izquierda de la barra superior, a 26 px. Nunca sin el nombre al lado.

## Paleta

Tokens de color. Ningún componente usa un color literal.

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `--fondo` | `#EFEFEC` | `#121212` | Fondo de la ventana |
| `--hoja` | `#FAFAF8` | `#1C1C1C` | Superficie de trabajo |
| `--tinta` | `#1B1B1D` | `#EDEDEA` | Texto principal |
| `--tinta-suave` | `#57575C` | `#A9A9A4` | Texto secundario, etiquetas |
| `--velo` | `#E4E4E0` | `#262626` | Bloques (problemas, pasos inactivos) |
| `--amarillo` | `#F5C518` | `#F5C518` | Fosforito y acento. Siempre con texto `--grafito` encima |
| `--grafito` | `#1B1B1D` | `#121212` | Texto sobre amarillo |
| `--accion` | `#1B1B1D` | `#F5C518` | Fondo del botón principal |
| `--sobre-accion` | `#F5C518` | `#121212` | Texto del botón principal |
| `--error` | `#B42318` | `#FF8A80` | Solo para errores (RF-014); no es acento |
| `--foco` | `#1D4ED8` | `#8AB4FF` | Anillo de foco del teclado |

**Contraste medido (WCAG 2.2 AA pide ≥ 4,5:1, RNF-014; calculado el 2026-10-22):**

| Par | Claro | Oscuro |
|---|---|---|
| Grafito sobre amarillo (fosforito, botón) | 10,5:1 | 10,5:1 |
| Tinta sobre hoja | 16,5:1 | 14,5:1 |
| Tinta suave sobre hoja | 6,9:1 | 7,2:1 |
| Tinta suave sobre velo | 5,6:1 | 6,4:1 |
| Error sobre hoja | 6,3:1 | 7,5:1 |

**Reglas:**
- El amarillo **solo** marca: fragmentos con problemas, el paso actual, el botón principal y el logotipo. Nunca como fondo de un bloque grande.
- Sin degradados, sin efecto cristal, sin sombras en elementos en reposo (sombra solo en lo que flota: menús, avisos).
- Las superficies se separan por un cambio de tono (`--fondo` → `--hoja` → `--velo`), no por líneas.

## Tipografía

| Rol | Familia | Uso |
|---|---|---|
| Títulos y prompt del usuario | **Bricolage Grotesque** (500, 700, 800) | Marca, títulos, el prompt mostrado en grande |
| Texto | **Figtree** (400, 500, 600) | Todo lo demás |

Escala (rem): 0,85 · 1 · 1,25 · 1,7 · 2,6. Cinco tamaños como máximo. Texto a 16 px como mínimo, interlineado 1,5 y unos 65 caracteres por línea. Títulos con `text-wrap: balance` y en dos líneas como máximo.

Las tipografías se sirven desde la propia app, no desde Google (privacidad, RNF-006/A6). Ambas tienen licencia SIL Open Font License.

## Componentes

- **Barra superior:** logotipo, selector de idioma (ES · CA · EN · DE) e interruptor de modo claro u oscuro (RF-025). Sin menú lateral: la app tiene una sola pantalla.
- **Pasos** (RF-022): «1 Escribir · 2 Revisar · 3 Mejorar» como pastillas. La actual va en amarillo con texto grafito; las hechas, en tinta; las pendientes, en tinta suave.
- **Fosforito** (la firma): fondo amarillo y texto grafito sobre el fragmento con problemas, con `box-decoration-break: clone` para que se vea bien en varias líneas.
- **Problema:** bloque en `--velo` con la gravedad (Alta / Media / Baja) en una pastilla, el nombre de la categoría en la tipografía de títulos y la explicación en tinta suave.
- **Botón principal:** fondo `--accion`, texto `--sobre-accion`, radio de 4 px, al menos 44 × 44 px. Un solo botón principal por paso.
- **Copiar** (RF-020): botón con icono y texto. Al pulsarlo, «Copiado» durante 2 s. Si hay `[COMPLETAR: …]`, el aviso lo recuerda.
- **Progreso** (RF-017): barra fina indeterminada con el texto del paso. La voz de la marca: «Afilando tu prompt…» al revisar y «Puliendo la versión mejorada…» al mejorar.
- **Ejemplos** (RF-021): cuatro opciones en la pantalla inicial, con el comienzo del prompt en la tipografía de títulos.
- **Foco:** anillo de 3 px en `--foco` con 2 px de separación, visible siempre con el teclado.

## Movimiento

Discreto (nivel 3 de 10): 150–250 ms con salida suave, solo `transform` y `opacity`. Entrada del resultado nuevo y desplazamiento hasta él (RF-023). Con `prefers-reduced-motion`, nada se desplaza ni se anima; el contenido aparece directamente.

## Voz

Hablar de tú, en frases cortas y sin jerga. El verbo de la marca es **afilar**: «Afilando tu prompt…». Los errores dicen qué ha pasado y qué hacer, sin disculpas (RF-014).
