"""
División y recomposición de párrafos numerados de BOE.

Detecta párrafos que inician con numeración (Uno, Dos, etc.)
y agrupa las continuaciones que no inician con numeración
con el párrafo anterior.
"""

from src.domain.constants import NUMERACION


def build_candidate_paragraphs(clean_text: str) -> list[str]:
    """
    Construye una lista de párrafos candidatos a partir del texto limpio.

    1. Divide por doble salto de línea
    2. Filtra bloques vacíos
    3. Detecta párrafos que inician con numeración
    4. Agrupa las continuaciones con el párrafo anterior

    Devuelve solo los párrafos que inician con numeración
    (incluyendo sus continuaciones concatenadas).
    """
    parrafos = [p.strip() for p in clean_text.split('\n\n') if p.strip()]

    result: list[str] = []
    for parrafo in parrafos:
        if parrafo.startswith(tuple(NUMERACION)):
            result.append(parrafo)
        elif result:
            # Es una continuación del párrafo anterior
            result[-1] += ' ' + parrafo

    return result


def is_numbered_paragraph(text: str) -> bool:
    """Verifica si un texto inicia con numeración de BOE."""
    return text.startswith(tuple(NUMERACION))


def split_paragraphs_only(text: str) -> list[str]:
    """
    Divide texto por doble salto de línea sin agrupar continuaciones.
    Útil para depuración y logging.
    """
    return [p.strip() for p in text.split('\n\n') if p.strip()]
