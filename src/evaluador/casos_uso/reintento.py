"""Reintento automático ante una respuesta inválida de la IA (RF-018, spec 002, ADR-0004).

Un fallo puntual del modelo (JSON mal formado) no debe llegar al usuario: se reintenta una vez.
Los demás errores (servicio no disponible, tiempo agotado, límite de uso) no se reintentan, porque
solo alargarían la espera; llegan a la interfaz con su tipo (RF-014).
"""

import logging
from collections.abc import Callable

from evaluador.puertos.modelo_ia import ErrorProveedor, TipoError

registro = logging.getLogger("evaluador.reintento")


def con_reintento[T](llamada: Callable[[], T]) -> T:
    try:
        return llamada()
    except ErrorProveedor as error:
        if error.tipo is not TipoError.RESPUESTA_INVALIDA:
            raise
        registro.info("reintento motivo=respuesta_invalida")
        return llamada()
