"""Evals de la mejora (T054): RF-009, RF-010, RF-013 y RNF-011.

Para cada caso con problemas esperados: diagnostica y mejora con Gemini, con TODAS las preguntas
omitidas (peor caso para inventar), y un juez de otro proveedor (NVIDIA) busca datos inventados y
requisitos añadidos. También comprueba el idioma de la mejora y los marcadores [COMPLETAR: …].

Uso:  .venv/Scripts/python -m evals.ejecutar_mejora [--calibracion 12] [--pausa 4]
Con --calibracion N solo procesa N casos repartidos y prepara el archivo que etiqueta Àlex Marco
(evals/calibracion/mejora-v1.md), sin mostrarle lo que dijo el juez para no influirle.
"""

import argparse
import io
import json
import os
import sys
import time
from datetime import date

from dotenv import load_dotenv

from evals.calibracion import ETIQUETAS, VEREDICTOS
from evals.casos import RAIZ, Caso, cargar_validados
from evals.ejecutar import GEMINI_URL, p95
from evals.idioma import detectar
from evals.juez import Juez
from evaluador.adaptadores.modelo_openai_compatible import ModeloOpenAICompatible
from evaluador.casos_uso.diagnosticar import Diagnosticar
from evaluador.casos_uso.mejorar import MARCADOR, Mejorar
from evaluador.prompts import cargar
from evaluador.puertos.modelo_ia import ErrorProveedor

RESULTADOS = RAIZ / "evals" / "resultados"


def casos_mejorables(casos: list[Caso]) -> list[Caso]:
    """Casos con problemas que mejorar: ni dañinos ni prompts sin problemas esperados."""
    return [c for c in casos if c.esperados and not c.debe_rechazar]


def repartir(casos: list[Caso], n: int) -> list[Caso]:
    paso = max(1, len(casos) // n)
    return casos[::paso][:n]


def archivo_de_etiquetado(filas: list[dict[str, object]]) -> str:
    partes = [
        "# Calibración del juez de la mejora (T054, RNF-011)",
        "",
        "**Estado:** pendiente de etiquetar por Àlex Marco · **Versión:** 1.0",
        "",
        "Para cada mejora, sustituye `[sí/no]` por **sí** o **no** y, si es sí, "
        "escribe después de `·` qué has visto.",
        "",
        "- **Dato inventado:** hechos, cifras, nombres, fechas o características que no están en el "
        "prompt ni en las respuestas (aquí no hay respuestas: todas las "
        "preguntas se omitieron).",
        "- **Requisito añadido:** condiciones de estilo, tono, formato, extensión o contenido "
        "que nadie pidió.",
        "- No cuentan: reformular, hacer explícito lo que ya dice el prompt, ni los `[COMPLETAR: …]`.",
        "",
        "Lo que opinó el juez está en otro archivo, para no influirte.",
        "",
    ]
    for i, fila in enumerate(f for f in filas if "mejorado" in f):
        partes += [
            "---",
            "",
            f"### M{i + 1:02d} · {fila['caso']}",
            "",
            "**Prompt original:**",
            "",
            *[f"> {linea}" for linea in str(fila["prompt"]).splitlines()],
            "",
            "**Versión mejorada:**",
            "",
            *[f"> {linea}" for linea in str(fila["mejorado"]).splitlines()],
            "",
            "**¿Dato inventado?** [sí/no] · ",
            "**¿Requisito añadido?** [sí/no] · ",
            "",
        ]
    return "\n".join(partes)


def main() -> None:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    argumentos = argparse.ArgumentParser()
    argumentos.add_argument("--calibracion", type=int, default=0)
    argumentos.add_argument("--modelo", default="gemini-3.5-flash-lite")
    argumentos.add_argument("--pausa", type=float, default=4.0)
    opciones = argumentos.parse_args()

    load_dotenv(RAIZ / ".env")
    gemini = ModeloOpenAICompatible(
        proveedor="Google Gemini",
        modelo=opciones.modelo,
        base_url=GEMINI_URL,
        api_key=os.environ.get("GEMINI_API_KEY", ""),
        prompt_diagnostico=cargar("diagnostico"),
        prompt_mejora=cargar("mejora"),
    )
    juez = Juez(os.environ.get("NVIDIA_API_KEY", ""))
    casos = casos_mejorables(cargar_validados()[0])
    if opciones.calibracion:
        casos = repartir(casos, opciones.calibracion)
    print(f"{len(casos)} casos · mejora con {opciones.modelo} · juez {juez.modelo}\n")

    filas: list[dict[str, object]] = []
    for caso in casos:
        fila: dict[str, object] = {
            "caso": caso.id,
            "idioma": caso.idioma,
            "prompt": caso.prompt,
        }
        try:
            diagnostico = Diagnosticar(gemini).ejecutar(caso.prompt, idioma_interfaz="es")
            if diagnostico.rechazado or diagnostico.sin_problemas:
                fila["omitido"] = "rechazado" if diagnostico.rechazado else "sin problemas"
            else:
                inicio = time.monotonic()
                version = Mejorar(gemini).ejecutar(
                    diagnostico, {q.id: None for q in diagnostico.preguntas}, "es"
                )
                fila |= {
                    "segundos": round(time.monotonic() - inicio, 1),
                    "mejorado": version.texto,
                    "cambios": len(version.cambios),
                    "preguntas_omitidas": len(diagnostico.preguntas),
                    "marcadores": version.texto.count(MARCADOR),
                    "idioma_mejora": detectar(version.texto),
                }
                veredicto = juez.juzgar(caso.prompt, "", version.texto)
                fila |= {
                    "datos_inventados": veredicto.datos_inventados,
                    "requisitos_anadidos": veredicto.requisitos_anadidos,
                }
        except (ErrorProveedor, ValueError) as error:
            fila["error"] = str(error)
        except Exception as error:  # noqa: BLE001  # Fallos del juez (red, cuota): se registran y se sigue.
            fila["error"] = f"juez: {type(error).__name__}"
        filas.append(fila)
        print(f"{caso.id}  {fila.get('error') or fila.get('omitido') or str(fila['segundos']) + ' s'}")
        time.sleep(opciones.pausa)

    juzgadas = [f for f in filas if "datos_inventados" in f]
    con_omitidas = [f for f in juzgadas if f["preguntas_omitidas"]]
    total = {
        "casos": len(filas),
        "juzgados": len(juzgadas),
        "con_datos_inventados": sum(bool(f["datos_inventados"]) for f in juzgadas) / len(juzgadas)
        if juzgadas
        else None,
        "con_requisitos_anadidos": sum(bool(f["requisitos_anadidos"]) for f in juzgadas) / len(juzgadas)
        if juzgadas
        else None,
        "idioma_correcto": sum(f["idioma_mejora"] == f["idioma"] for f in juzgadas) / len(juzgadas)
        if juzgadas
        else None,
        "marcadores_presentes": sum(int(str(f["marcadores"])) > 0 for f in con_omitidas) / len(con_omitidas)
        if con_omitidas
        else None,
        "p95_mejora_s": p95([float(str(f["segundos"])) for f in juzgadas]),
    }
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    nombre = "calibracion" if opciones.calibracion else "completa"
    salida = RESULTADOS / f"{date.today().isoformat()}_mejora_{nombre}_{opciones.modelo}.json"
    salida.write_text(
        json.dumps({"resumen": total, "casos": filas}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if opciones.calibracion:
        ETIQUETAS.parent.mkdir(parents=True, exist_ok=True)
        ETIQUETAS.write_text(archivo_de_etiquetado(filas), encoding="utf-8")
        veredictos = {
            f["caso"]: [bool(f["datos_inventados"]), bool(f["requisitos_anadidos"])] for f in juzgadas
        }
        VEREDICTOS.write_text(json.dumps(veredictos, indent=2), encoding="utf-8")
        print(f"\nArchivo para etiquetar: {ETIQUETAS.relative_to(RAIZ)}")
    print(f"\n{json.dumps(total, ensure_ascii=False, indent=2)}\nResultados en {salida.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
