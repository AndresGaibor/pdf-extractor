"""
División y recomposición de párrafos numerados de BOE.

Detecta párrafos que inician con numeración (Uno, Dos, etc.)
y agrupa las continuaciones que no inician con numeración
con el párrafo anterior.

También detecta bloques de corte que indican fin de resoluciones útiles.
"""

import re

from src.domain.constants import NUMERACION
from src.infrastructure.pdf.organ_patterns import CUTOFF_MARKERS


def build_candidate_paragraphs(clean_text: str) -> list[str]:
    """
    Construye una lista de párrafos candidatos a partir del texto limpio.

    1. Divide por doble salto de línea
    2. Filtra bloques vacíos
    3. Detecta párrafos que inician con numeración
    4. Agrupa las continuaciones con el párrafo anterior
    5. Detiene el procesamiento al encontrar un bloque de corte

    Devuelve solo los párrafos que inician con numeración
    (incluyendo sus continuaciones concatenadas).
    """
    parrafos = [p.strip() for p in clean_text.split('\n\n') if p.strip()]

    result: list[str] = []
    for parrafo in parrafos:
        # Detectar bloques de corte: fin de resoluciones útiles
        if _is_cutoff_block(parrafo):
            break

        if parrafo.startswith(tuple(NUMERACION)):
            result.append(parrafo)
        elif result:
            # Es una continuación del párrafo anterior
            result[-1] += ' ' + parrafo

    return result


def _is_cutoff_block(text: str) -> bool:
    """Verifica si un texto es un bloque de fin de resoluciones.

    Detecta:
    1. Marcadores al inicio del párrafo
    2. Bloques de "Incidencias" que no están en encabezados
    """
    texto_normalizado = text.strip()

    for marker in CUTOFF_MARKERS:
        if texto_normalizado.lower().startswith(marker.lower()):
            return True

    # Detectar "X. Incidencias." donde X es numeración
    # Esto evita "situaciones e incidencias" en encabezados
    # Usamos \w* después de prefijos como Dieci/Veinti para capturar
    # Dieciséis, Veintiuno, etc.
    if re.search(
        r'^(?:Uno|Dos|Tres|Cuatro|Cinco|Seis|Siete|Ocho|Nueve|Diez|'
        r'Once|Doce|Trece|Catorce|Quince|Dieci\w*|Veinte|Veinti\w*|'
        r'Treinta|Cuarenta|Cincuenta|Sesenta|Setenta|Ochenta|'
        r'Noventa|Ciento|Doscientos|Trescientos|Cuatrocientos|'
        r'Quinientos|Seiscientos|Setecientos|Ochocientos|'
        r'Novecientos|Mil)\.?\s+Incidencias',
        texto_normalizado, re.IGNORECASE
    ):
        return True

    # También detectar "Incidencias:" al inicio (sin numeración)
    if texto_normalizado.lower().startswith("incidencias:"):
        return True

    return False


def is_numbered_paragraph(text: str) -> bool:
    """Verifica si un texto inicia con numeración de BOE."""
    return text.startswith(tuple(NUMERACION))


def split_paragraphs_only(text: str) -> list[str]:
    """
    Divide texto por doble salto de línea sin agrupar continuaciones.
    Útil para depuración y logging.
    """
    return [p.strip() for p in text.split('\n\n') if p.strip()]
