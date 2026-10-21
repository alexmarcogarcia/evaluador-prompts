"""Composición: el único punto donde se conectan las implementaciones (T034, ADR-0001, ADR-0002).

Lee la configuración del entorno (.env) y arranca el servidor solo en el propio equipo (RNF-008).
No hay almacenamiento: nada de lo que escribe el usuario se guarda en disco (RNF-009).
"""

import logging
import os
import sys
from dataclasses import dataclass

import uvicorn
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI

from evaluador.adaptadores.modelo_openai_compatible import ModeloOpenAICompatible
from evaluador.adaptadores.web.app import crear_app
from evaluador.casos_uso.diagnosticar import Diagnosticar
from evaluador.casos_uso.mejorar import Mejorar
from evaluador.prompts import cargar

HOST = "127.0.0.1"  # RNF-008: nunca 0.0.0.0 en este incremento.
PUERTO = 8000


@dataclass(frozen=True)
class Proveedor:
    nombre: str
    base_url: str
    modelo: str
    variable_clave: str


PROVEEDORES = {
    "gemini": Proveedor(
        "Google Gemini",
        "https://generativelanguage.googleapis.com/v1beta/openai",
        "gemini-3.5-flash-lite",
        "GEMINI_API_KEY",
    ),
    "nvidia": Proveedor(
        "NVIDIA", "https://integrate.api.nvidia.com/v1", "nvidia/nemotron-3-super-120b-a12b", "NVIDIA_API_KEY"
    ),
}


def construir_app() -> FastAPI:
    load_dotenv(find_dotenv(usecwd=True))
    proveedor = PROVEEDORES[os.environ.get("PROVEEDOR", "gemini")]
    clave = os.environ.get(proveedor.variable_clave, "")
    if not clave:
        sys.exit(f"Falta {proveedor.variable_clave} en .env (ver README).")
    modelo = ModeloOpenAICompatible(
        proveedor=proveedor.nombre,
        modelo=os.environ.get("MODELO", proveedor.modelo),
        base_url=proveedor.base_url,
        api_key=clave,
        prompt_diagnostico=cargar("diagnostico"),
        prompt_mejora=cargar("mejora"),
    )
    return crear_app(Diagnosticar(modelo), Mejorar(modelo), proveedor=modelo.proveedor, modelo=modelo.modelo)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    app = construir_app()  # Primero la configuración: si falta la clave, se avisa y no se anuncia nada.
    print(f"Evaluador de prompts en http://{HOST}:{PUERTO}  (Ctrl+C para salir)")
    uvicorn.run(app, host=HOST, port=PUERTO)
