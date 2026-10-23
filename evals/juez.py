"""Juez automático del contenido inventado en la mejora (RNF-011, T054).

Es de un proveedor distinto del que mejora (NVIDIA frente a Gemini) para no juzgar con el mismo
sesgo. Se calibra con las etiquetas de Àlex Marco (evals/calibracion.py) antes de fiarse de él.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import openai

PROMPT_JUEZ = (Path(__file__).parent / "juez_mejora.md").read_text(encoding="utf-8")
NVIDIA_URL = "https://integrate.api.nvidia.com/v1"


@dataclass(frozen=True)
class Veredicto:
    datos_inventados: tuple[str, ...]
    requisitos_anadidos: tuple[str, ...]

    @property
    def inventa_datos(self) -> bool:
        return bool(self.datos_inventados)

    @property
    def anade_requisitos(self) -> bool:
        return bool(self.requisitos_anadidos)


def interpretar_veredicto(texto: str) -> Veredicto:
    inicio, fin = texto.find("{"), texto.rfind("}")
    datos = json.loads(texto[inicio : fin + 1])
    return Veredicto(
        tuple(str(x) for x in datos.get("datos_inventados", [])),
        tuple(str(x) for x in datos.get("requisitos_anadidos", [])),
    )


class Juez:
    # Calibrado 11/12 (2026-10-20). Reserva, también 11/12: nvidia/nemotron-3-ultra-550b-a55b.
    def __init__(self, api_key: str, modelo: str = "nvidia/nemotron-3.5-lightning-30b-a3b") -> None:
        self.modelo = modelo
        self._cliente = openai.OpenAI(api_key=api_key, base_url=NVIDIA_URL, timeout=150, max_retries=2)

    def juzgar(self, prompt: str, respuestas: str, mejorado: str) -> Veredicto:
        usuario = "\n\n".join(
            f"{etiqueta}:\n<<<\n{texto}\n>>>"
            for etiqueta, texto in (
                ("PROMPT ORIGINAL", prompt),
                ("RESPUESTAS DEL USUARIO", respuestas or "(ninguna: todas las preguntas se omitieron)"),
                ("VERSIÓN MEJORADA", mejorado),
            )
        )
        respuesta = self._cliente.chat.completions.create(
            model=self.modelo,
            messages=[{"role": "system", "content": PROMPT_JUEZ}, {"role": "user", "content": usuario}],
            temperature=0,
        )
        return interpretar_veredicto(respuesta.choices[0].message.content or "")
