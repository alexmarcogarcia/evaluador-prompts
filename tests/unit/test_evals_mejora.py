"""Herramientas de las evals de la mejora (T054).

Verifican RF-013 (detección del idioma de la versión mejorada) y RNF-011 (veredicto del juez y
calibración con las etiquetas de Àlex Marco).
"""

from evals.calibracion import coincidencias, leer_etiquetas
from evals.casos import ARCHIVOS, leer_casos
from evals.ejecutar_mejora import casos_mejorables
from evals.idioma import detectar
from evals.juez import interpretar_veredicto


def test_detecta_los_4_idiomas_de_la_interfaz() -> None:
    assert detectar("Escribe un artículo para el blog de mi instituto, dirigido a los alumnos.") == "es"
    assert detectar("Escriu un article per al blog de l'institut, adreçat als alumnes.") == "ca"
    assert detectar("Write an article for the school blog, aimed at the students.") == "en"
    assert detectar("Schreib einen Artikel für den Blog der Schule, der sich an die Schüler richtet.") == "de"


def test_los_casos_saben_su_idioma() -> None:
    casos = [c for a in ARCHIVOS for c in leer_casos(a.read_text(encoding="utf-8"))]
    assert {c.idioma for c in casos} >= {"es", "ca", "en", "de"}


def test_solo_se_mejoran_casos_con_problemas_esperados_y_no_danios() -> None:
    casos = [c for a in ARCHIVOS for c in leer_casos(a.read_text(encoding="utf-8"))]
    mejorables = casos_mejorables(casos)
    assert mejorables and all(c.esperados and not c.debe_rechazar for c in mejorables)


def test_interpreta_el_veredicto_del_juez() -> None:
    texto = 'Veredicto: {"datos_inventados": ["el pedido 4521"], "requisitos_anadidos": []}'
    veredicto = interpretar_veredicto(texto)
    assert veredicto.datos_inventados == ("el pedido 4521",) and veredicto.requisitos_anadidos == ()
    assert veredicto.inventa_datos and not veredicto.anade_requisitos


def test_lee_las_etiquetas_y_cuenta_coincidencias_con_el_juez() -> None:
    md = """### M01 · C15
**¿Dato inventado?** no
**¿Requisito añadido?** sí · tono divulgativo

### M02 · C16
**¿Dato inventado?** sí · una fecha
**¿Requisito añadido?** no
"""
    etiquetas = leer_etiquetas(md)
    assert etiquetas == {"C15": (False, True), "C16": (True, False)}
    juez = {"C15": (False, True), "C16": (False, False)}
    assert coincidencias(etiquetas, juez) == (1, 2)


def test_acepta_la_respuesta_escrita_despues_de_la_plantilla() -> None:
    md = "### M01 · C17\n**¿Dato inventado?** [sí/no] · no\n**¿Requisito añadido?** [sí/no] · sí\n"
    assert leer_etiquetas(md) == {"C17": (False, True)}
