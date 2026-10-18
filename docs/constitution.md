# Constitución del Evaluador de prompts

**Estado:** aprobada · **Versión:** 1.0 · **Perfil:** B (sube a C al abrirse a otras personas)

## Principios

1. **La especificación manda.** Todo cambio parte de una especificación aprobada en `/specs`. Si el código y la especificación divergen, se corrige primero la especificación. *Por qué:* evita construir lo que nadie ha decidido.
2. **Explicar, no solo reescribir.** Cada cambio que la app propone en un prompt está ligado a un problema detectado y explica por qué mejora el resultado. *Por qué:* es la diferenciación (a) del producto.
3. **Preguntar antes que suponer.** Si a la app le falta información sobre lo que quiere el usuario, se la pregunta; no la inventa. *Por qué:* es la diferenciación (c), y una intención inventada produce prompts que parecen mejores sin serlo.
4. **Comprensible para no expertos.** Todo texto visible para el usuario se entiende sin conocimientos técnicos de IA. Un término técnico solo aparece con su explicación. *Por qué:* es el público objetivo.
5. **La calidad se mide, no se supone.** El diagnóstico tiene evals versionadas (prompts de prueba con los problemas que se espera detectar). Ningún cambio de modelo o de prompt interno se acepta sin pasarlas. *Por qué:* la incertidumbre principal del proyecto es la calidad del diagnóstico.
6. **Coste cero por defecto.** Todo funciona con modelos de nivel gratuito y se mide el consumo de tokens. *Por qué:* el presupuesto es 0 €.
7. **Independencia del proveedor.** El acceso a modelos de IA queda detrás de una interfaz propia, así que cambiar de proveedor no toca la lógica del producto. *Por qué:* el proveedor está abierto y los niveles gratuitos cambian.
8. **Simplicidad primero.** Una pieza, dependencia o abstracción solo entra si un requisito la pide (KISS, YAGNI). *Por qué:* hay una sola persona para mantenerla.
9. **Pruebas antes que implementación.** La prueba de cada tarea se escribe primero y debe fallar antes de implementar.
10. **Ningún secreto ni dato del usuario donde no debe.** Claves de API fuera del repositorio. Los prompts de los usuarios no aparecen en logs.

## Arquitectura y diseño por defecto

- Arquitectura limpia. El **dominio** contiene prompt, problema detectado, sugerencia, versión y caso de prueba, sin depender de frameworks ni de proveedores. Los **casos de uso** son revisar, preguntar, mejorar, comprobar y consultar historial. Los **puertos** son el modelo de IA, el almacenamiento y la interfaz. Los **adaptadores** quedan en el borde.
- Las dependencias apuntan hacia el dominio y las implementaciones se conectan en un único punto.
- Separación de responsabilidades, composición antes que herencia, SOLID, DRY. Sirven como criterio de revisión, no como dogma.
- **Lenguaje principal: Python.** Tiene SDKs de todos los proveedores de modelos, el ecosistema de evaluación y métricas de texto, pruebas sencillas y es el estándar en ingeniería de IA. Si la interfaz necesita otro lenguaje (por ejemplo, HTML y JavaScript en el frontend), se decide con un ADR en la Fase 5.
- **Paradigma:** orientado a objetos para las entidades del dominio y funciones puras para las reglas y transformaciones sin estado. Tipado estático con anotaciones de tipo comprobadas en la CI.

## Invariantes del dominio

- El prompt original del usuario nunca se modifica ni se pierde. Cada mejora genera una versión nueva.
- Cada problema detectado señala el fragmento concreto del prompt al que se refiere.
- Cada sugerencia de mejora referencia el problema o los problemas que resuelve.
- El usuario siempre sabe a qué proveedor de IA se envía su prompt.

## Definición de hecho

- Cumple los criterios de aceptación de la especificación.
- Hay pruebas automáticas que referencian el requisito (`RF-xxx`) y están en verde.
- Si el cambio afecta al diagnóstico o a un prompt interno, las evals no empeoran.
- El linter y el formateador pasan, y la CI está en verde.
- Pasa la revisión (ver más abajo).
- La documentación (spec, plan, README, AGENTS.md) está actualizada en el mismo cambio.
- No hay secretos ni datos de usuario en código, logs ni commits.

## Reglas de revisión

- **Excepción justificada al «revisa otra persona»:** el equipo es de una sola persona. Por eso, cada cambio pasa por:
  - (1) una revisión asistida por IA contra la spec y esta constitución;
  - (2) una autorrevisión con la checklist de la DoD, en otro momento distinto al de escribirlo.
- Cambios pequeños: un PR por tarea o grupo de tareas de una misma historia.
- Al abrirse a otras personas (perfil C) se revisa esta regla.

## Confidencialidad y seguridad

| Clasificación | Qué incluye | Dónde puede estar |
|---|---|---|
| Pública | Código, documentación, specs, evals con prompts sintéticos | Repositorio, herramientas de IA |
| Confidencial | Claves de API | Solo variables de entorno o gestor de secretos; nunca en repositorio, chats ni capturas |
| Datos de usuario | Prompts introducidos por otras personas (perfil C) | Solo en el proveedor elegido por el usuario y en su propio almacenamiento; nunca en logs ni en herramientas de desarrollo |

- Herramientas de IA permitidas para desarrollar: cualquiera, porque el código es público.
- Si una clave se filtra, se rota de inmediato.
- Los datos de prueba y de evals son siempre sintéticos.

## Repositorio y convenciones

- Un único repositorio. Las specs viven en `/specs/NNN-funcionalidad/` junto al código.
- Rama principal `main` y ramas cortas por tarea (trunk-based).
- Conventional Commits. SemVer a partir de la primera versión publicada.
- Formateador y linter desde el primer commit de código. Dependencias con versión fijada.
- `README.md` ejecutable: con ese archivo basta para instalar, ejecutar y probar.

## Gobierno

Solo Àlex Marco puede enmendar esta constitución. Cada enmienda sube la versión y queda registrada abajo con fecha y motivo. Se enmienda con motivo explícito; no se esquiva.

### Registro de enmiendas

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| 0.1 | 2026-10-18 | Borrador inicial | Fase 2 |
| 1.0 | 2026-10-18 | Lenguaje fijado (Python) y aprobación | Cierre de la Fase 2 |

**Versión:** 1.0 · **Aprobada:** 2026-10-18 por Àlex Marco
