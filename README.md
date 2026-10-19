# Evaluador de prompts

Aplicación que revisa un prompt, señala dónde falla, explica cómo precisarlo para obtener el resultado esperado y comprueba que la versión mejorada funciona mejor. Pensada para personas con poco dominio de la IA.

> Estado: primer incremento en curso. Ya funciona el diagnóstico de prompts (historia P1); faltan las preguntas aclaratorias (P2) y la versión mejorada (P3).

## Requisitos

- Python 3.13 (versión fijada en `.python-version`)
- Git

## Instalar

```
git clone https://github.com/alexmarcogarcia/evaluador-prompts.git
cd evaluador-prompts
python scripts/setup.py
```

`setup.py` crea el entorno virtual `.venv`, instala las dependencias con sus versiones fijadas y crea un `.env` a partir de `.env.example`. Añade tus claves de API en `.env`, que nunca se sube al repositorio:

- `GEMINI_API_KEY`: proveedor principal (ADR-0001), gratuito en https://aistudio.google.com
- `NVIDIA_API_KEY`: alternativa, gratuita en https://build.nvidia.com

## Probar

```
python scripts/check.py
```

Ejecuta lo mismo que la CI: linter y formato (ruff), tipos (mypy), pruebas (pytest) y la comprobación de coherencia entre spec, tareas y pruebas. Las pruebas que llaman a un proveedor real no se ejecutan por defecto; para lanzarlas: `.venv/Scripts/python -m pytest -m red` (en Linux/macOS, `.venv/bin/python`).

## Ejecutar

```
.venv/Scripts/python -m evaluador      # Windows
.venv/bin/python -m evaluador          # Linux/macOS
```

Y abre http://127.0.0.1:8000 en el navegador. La app solo acepta conexiones desde tu propio equipo y no guarda nada en disco. Por defecto usa Gemini; para usar NVIDIA, añade `PROVEEDOR=nvidia` en `.env`.

## Documentación

- [One-pager y clasificación](docs/one-pager.md)
- [Constitución](docs/constitution.md)
- [Especificaciones](specs/)
- [Decisiones de arquitectura (ADR)](docs/adr/)
- [Registro de riesgos](docs/riesgos.md)
- [Cómo contribuir](CONTRIBUTING.md)

## Licencia

[MIT](LICENSE) © 2026 Àlex Marco
