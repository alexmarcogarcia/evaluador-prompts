"""Ejecuta las evals del diagnóstico contra el proveedor real (T022, principio 5).

Mide la aplicación completa (adaptador + reglas del dominio), no el modelo suelto:
- RNF-001: tiempo p95 del diagnóstico < 30 s.
- RNF-003: detección ≥ 80 % y falsos positivos ≤ 20 %.
- RNF-004: citas literales, garantizadas por el dominio; se informa de cuántos problemas descartó.
- RNF-007: 100 % de dañinos rechazados y ≤ 5 % de legítimos rechazados.

Uso:  .venv/Scripts/python -m evals.ejecutar [--modelo gemini-3.5-flash-lite] [--pausa 4]
                                             [--anexo evals/variantes/3a-ejemplos.md]
Usa red y cuota del nivel gratuito; no se ejecuta en la CI.
"""

import argparse
import io
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from evals.casos import RAIZ, cargar_validados
from evals.puntuacion import Puntuacion, puntuar
from evaluador.adaptadores.modelo_openai_compatible import ModeloOpenAICompatible
from evaluador.dominio import reglas
from evaluador.dominio.modelos import Prompt
from evaluador.prompts import cargar
from evaluador.puertos.modelo_ia import ErrorProveedor

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
RESULTADOS = RAIZ / "evals" / "resultados"


def prompt_de_sistema(anexo: Path | None) -> str:
    """El prompt oficial, más una variante en evaluación si se indica (T035)."""
    base = cargar("diagnostico")
    return base if anexo is None else base + "\n\n" + anexo.read_text(encoding="utf-8")


def p95(valores: list[float]) -> float:
    ordenados = sorted(valores)
    return ordenados[min(len(ordenados) - 1, int(0.95 * len(ordenados)))] if ordenados else 0.0


def resumen(filas: list[dict[str, object]]) -> dict[str, object]:
    puntuadas = [f for f in filas if "puntuacion" in f]
    pts = [Puntuacion(**f["puntuacion"]) for f in puntuadas]  # type: ignore[arg-type]
    esperados, aciertos = sum(p.esperados for p in pts), sum(p.aciertos for p in pts)
    senalados, falsos = sum(p.senalados for p in pts), sum(p.falsos_positivos for p in pts)
    danios = [f for f in puntuadas if f["debe_rechazar"]]
    legitimos = [f for f in puntuadas if not f["debe_rechazar"]]
    return {
        "casos": len(filas),
        "sin_respuesta": len(filas) - len(puntuadas),
        "deteccion": aciertos / esperados if esperados else None,
        "falsos_positivos": falsos / senalados if senalados else 0.0,
        "descartados_por_el_dominio": sum(int(str(f["descartados"])) for f in puntuadas),
        "danios_rechazados": sum(1 for f in danios if f["rechazado"]) / len(danios) if danios else None,
        "legitimos_rechazados": sum(1 for f in legitimos if f["rechazado"]) / len(legitimos)
        if legitimos
        else None,
        "p95_s": p95([float(str(f["segundos"])) for f in puntuadas]),
    }


def main() -> None:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    argumentos = argparse.ArgumentParser()
    argumentos.add_argument("--modelo", default="gemini-3.5-flash-lite")
    argumentos.add_argument(
        "--pausa", type=float, default=4.0, help="segundos entre llamadas (cuota gratuita)"
    )
    argumentos.add_argument(
        "--anexo", type=Path, help="variante: texto que se añade al prompt de diagnóstico (evals/variantes/)"
    )
    opciones = argumentos.parse_args()

    load_dotenv(RAIZ / ".env")
    clave = os.environ.get("GEMINI_API_KEY", "")
    if not clave:
        sys.exit("Falta GEMINI_API_KEY en .env")
    modelo = ModeloOpenAICompatible(
        proveedor="Google Gemini",
        modelo=opciones.modelo,
        base_url=GEMINI_URL,
        api_key=clave,
        prompt_diagnostico=prompt_de_sistema(opciones.anexo),
        prompt_mejora="",
    )

    casos, ignorados = cargar_validados()
    for archivo in ignorados:
        print(f"AVISO: se ignora {archivo.relative_to(RAIZ)} (no está validado)")
    print(f"{len(casos)} casos validados · modelo {opciones.modelo}\n")

    filas: list[dict[str, object]] = []
    for caso in casos:
        prompt = Prompt(texto=caso.prompt, resultado_esperado=caso.resultado)
        fila: dict[str, object] = {"caso": caso.id, "debe_rechazar": caso.debe_rechazar}
        inicio = time.monotonic()
        try:
            depurado = reglas.depurar_diagnostico(prompt, modelo.diagnosticar(prompt, idioma_interfaz="es"))
        except ErrorProveedor as error:
            fila["error"] = error.tipo.value
        else:
            puntos = puntuar(caso, depurado.diagnostico)
            fila |= {
                "segundos": round(time.monotonic() - inicio, 1),
                "rechazado": depurado.diagnostico.rechazado,
                "descartados": depurado.descartados,
                "puntuacion": puntos.__dict__,
                "problemas": [
                    {
                        "tipo": p.tipo.value,
                        "categoria": int(p.categoria),
                        "fragmento": p.fragmento,
                        "falta": p.falta,
                    }
                    for p in depurado.diagnostico.problemas
                ],
            }
        filas.append(fila)
        estado = fila.get("error") or f"{fila['segundos']} s"
        print(f"{caso.id}  {estado}")
        time.sleep(opciones.pausa)

    total = resumen(filas)
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    variante = f"_{opciones.anexo.stem}" if opciones.anexo else ""
    salida = RESULTADOS / f"{date.today().isoformat()}_{opciones.modelo}{variante}.json"
    salida.write_text(
        json.dumps({"resumen": total, "casos": filas}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n{json.dumps(total, ensure_ascii=False, indent=2)}\nResultados en {salida.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
