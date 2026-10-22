# Guía visual de Sharpener

**Estado:** aprobada · **Versión:** 1.1 · **Aprobada:** 2026-10-22 por Àlex Marco (v1.0 Grafito, sustituida) · **Spec:** 002 (RF-024, RF-025)

Dirección **Amarillo lápiz** (v1.1). Sustituye a la dirección Grafito (v1.0), que a tamaño real resultaba plana y sin color. Se eligió entre tres direcciones de color (artefacto «Sharpener en color»).

**Cambios de la v1.1:** el amarillo pasa de detalle a color de marca (portada amarilla), el fondo es crema cálido, las hojas son blancas y los problemas son tarjetas con barra de tinta. Estructura, tipografía, movimiento y voz no cambian.

## Idea

Un lápiz recién afilado. **El amarillo del lápiz es el color de la marca**: la portada es un gran campo amarillo con el título en grafito. Dentro, hojas blancas y el mismo amarillo como rotulador fosforito sobre el texto del usuario: marca lo que falla en su prompt. Es el elemento que solo tiene Sharpener, y se entiende sin explicación: «esto es lo importante».

**La claridad manda sobre la estética** (spec 002). Si un adorno compite con entender la pantalla, se quita.

## Logotipo

Un lápiz en diagonal: cuerpo amarillo y punta de grafito, seguido de «Sharpener» en la tipografía de títulos (800).

```svg
<svg viewBox="0 0 32 32" aria-hidden="true">
  <path d="M3 22 L22 3 L29 10 L10 29 Z" fill="var(--amarillo)" stroke="var(--tinta)"/>
  <path d="M3 22 L10 29 L3 29 Z" fill="currentColor"/>
</svg>
```

Siempre a la izquierda de la barra superior, a 26 px. Nunca sin el nombre al lado.

## Paleta

Tokens de color. Ningún componente usa un color literal.

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `--fondo` | `#FFF6D6` | `#161510` | Fondo de la ventana (crema cálido) |
| `--hoja` | `#FFFFFF` | `#1F1D16` | Superficie de trabajo |
| `--tinta` | `#1B1B1D` | `#F4F1E6` | Texto principal; barra de las tarjetas de problema |
| `--tinta-suave` | `#4A4A4F` | `#C4BFAE` | Texto secundario, etiquetas |
| `--velo` | `#FFF1B8` | `#3A3214` | Pastillas, borde de tarjetas, pasos inactivos |
| `--amarillo` | `#F5C518` | `#F5C518` | Fosforito y acento. Siempre con texto `--grafito` encima |
| `--grafito` | `#1B1B1D` | `#161510` | Texto sobre amarillo |
| `--accion` | `#1B1B1D` | `#F5C518` | Fondo del botón principal |
| `--sobre-accion` | `#F5C518` | `#161510` | Texto del botón principal |
| `--portada` | `#F5C518` | `#2A2410` | Fondo de la hoja de portada (en oscuro, amarillo tostado para no deslumbrar) |
| `--sobre-portada` | `#1B1B1D` | `#F4F1E6` | Texto sobre la portada |
| `--error` | `#B42318` | `#FF8A80` | Solo para errores (RF-014); no es acento |
| `--foco` | `#1D4ED8` | `#8AB4FF` | Anillo de foco del teclado |

**Contraste medido (WCAG 2.2 AA pide ≥ 4,5:1, RNF-014; calculado el 2026-10-22):**

| Par | Claro | Oscuro |
|---|---|---|
| Grafito sobre amarillo (fosforito) | 10,5:1 | 11,2:1 |
| Texto del botón principal | 10,5:1 | 11,2:1 |
| Texto sobre portada | 10,5:1 | 13,7:1 |
| Tinta sobre hoja | 17,2:1 | 14,9:1 |
| Tinta sobre fondo | 15,9:1 | 16,2:1 |
| Tinta sobre velo | 15,2:1 | 11,3:1 |
| Tinta suave sobre hoja | 8,8:1 | 9,2:1 |
| Tinta suave sobre velo | 7,8:1 | 6,9:1 |
| Error sobre hoja | 6,6:1 | 7,4:1 |

El test `tests/unit/test_contraste.py` recalcula estos pares en cada ejecución.

**Reglas:**
- El amarillo es la marca: fondo de la portada, fosforito sobre los fragmentos con problemas, texto del botón principal y logotipo. Fuera de la portada, ningún bloque grande es amarillo: el diagnóstico y la mejora van sobre hojas blancas para que el fosforito destaque.
- Sin degradados, sin efecto cristal, sin sombras en elementos en reposo (sombra solo en lo que flota: menús, avisos).
- Las superficies se separan por un cambio de tono (`--fondo` → `--hoja`); las tarjetas llevan un borde de 2 px en `--velo` y una barra de 6 px a la izquierda.

## Tipografía

| Rol | Familia | Uso |
|---|---|---|
| Títulos y prompt del usuario | **Bricolage Grotesque** (500, 700, 800) | Marca, títulos, el prompt mostrado en grande |
| Texto | **Figtree** (400, 500, 600) | Todo lo demás |

Escala (rem): 0,85 · 1 · 1,25 · 1,7 · 2,6. Cinco tamaños como máximo. Texto a 16 px como mínimo, interlineado 1,5 y unos 65 caracteres por línea. Títulos con `text-wrap: balance` y en dos líneas como máximo.

Las tipografías se sirven desde la propia app, no desde Google (privacidad, RNF-006/A6). Ambas tienen licencia SIL Open Font License.

## Componentes

- **Barra superior:** logotipo, selector de idioma (ES · CA · EN · DE) e interruptor de modo claro u oscuro (RF-025). Sin menú lateral: la app tiene una sola pantalla.
- **Pasos** (RF-022): «1 Escribir · 2 Revisar · 3 Mejorar» como pastillas. La actual va en `--accion` con texto `--sobre-accion`; las hechas, en tinta; las pendientes, en tinta suave.
- **Fosforito** (la firma): fondo amarillo y texto grafito sobre el fragmento con problemas, con `box-decoration-break: clone` para que se vea bien en varias líneas.
- **Portada:** hoja en `--portada` con el título muy grande (hasta 4,2 rem) en `--sobre-portada`; los campos, blancos con borde de 2 px en `--sobre-portada`.
- **Problema:** tarjeta en `--hoja` con barra de tinta a la izquierda, la gravedad (Alta / Media / Baja) en una pastilla, el nombre de la categoría en la tipografía de títulos y la explicación en tinta suave.
- **Cambio** (versión mejorada): tarjeta en `--hoja` con barra amarilla a la izquierda.
- **Botón principal:** fondo `--accion`, texto `--sobre-accion`, radio de 4 px, al menos 44 × 44 px. Un solo botón principal por paso.
- **Copiar** (RF-020): botón con icono y texto. Al pulsarlo, «Copiado» durante 2 s. Si hay `[COMPLETAR: …]`, el aviso lo recuerda.
- **Progreso** (RF-017): barra fina indeterminada con el texto del paso. La voz de la marca: «Afilando tu prompt…» al revisar y «Puliendo la versión mejorada…» al mejorar.
- **Ejemplos** (RF-021): cuatro opciones en la pantalla inicial, con el comienzo del prompt en la tipografía de títulos.
- **Foco:** anillo de 3 px en `--foco` con 2 px de separación, visible siempre con el teclado.

## Movimiento

Discreto (nivel 3 de 10): 150–250 ms con salida suave, solo `transform` y `opacity`. Entrada del resultado nuevo y desplazamiento hasta él (RF-023). Con `prefers-reduced-motion`, nada se desplaza ni se anima; el contenido aparece directamente.

## Voz

Hablar de tú, en frases cortas y sin jerga. El verbo de la marca es **afilar**: «Afilando tu prompt…». Los errores dicen qué ha pasado y qué hacer, sin disculpas (RF-014).
