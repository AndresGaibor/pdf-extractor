"""
Selector de órganos por scoring dentro de un bloque de texto.

Usa posiciones absolutas (TextBlock) para filtrar órganos
y scoring para elegir el más representativo de origen/destino.
"""

import re
from typing import Optional

from src.infrastructure.pdf.parse_models import OrganMatch, TextBlock

# Puntuaciones por tipo de órgano
TYPE_SCORES = {
    "Audiencia Provincial": 10,
    "Tribunal Superior de Justicia": 10,
    "Tribunal de Instancia": 9,
    "Tribunal Supremo": 8,
    "Audiencia Nacional": 8,
    "Juzgado Central": 7,
    "Oficina de Justicia": 5,
    "Juzgado": 4,
    "Tribunal Constitucional": 3,
}

# Cláusulas accesorias que penalizan la relevancia del órgano
ACCESSORY_CLAUSES = [
    r'mientras\s+su\s+titular',
    r'se\s+encuentre\s+en\s+situaci[oó]n',
    r'servicios\s+especiales',
    r'continuando\s+en\s+la\s+misma',
    r'con\s+sede\s+en',
]


def select_organs_by_block(
    organ_matches: list[OrganMatch],
    block: TextBlock,
) -> list[OrganMatch]:
    """
    Filtra órganos por posición absoluta dentro del bloque.

    Un órgano pertenece al bloque si su posición (start, end)
    cae dentro del rango [block.start, block.end).
    """
    if not organ_matches or not block:
        return []

    return [
        m for m in organ_matches
        if block.start <= m.start < block.end
    ]


def pick_best_organo(
    organ_matches: list[OrganMatch],
    block: TextBlock,
) -> Optional[OrganMatch]:
    """
    Selecciona el mejor órgano de un bloque usando scoring.

    Reglas de scoring:
    +10: Audiencia Provincial o TSJ
    +9: Tribunal de Instancia
    +8: Tribunal Supremo o Audiencia Nacional
    +5: Tiene sección definida
    +3: Tiene localidad definida
    +2: Tiene número de plaza
    +2: Está cerca del inicio útil del bloque
    -5: Tiene alias histórico "(antes ...)"
    -3: Está dentro de cláusula accesoria
    -8: Parece alias corto (JPI 14)
    """
    candidates = select_organs_by_block(organ_matches, block)

    if not candidates:
        return None

    scored = [(score_organo(m, block), m) for m in candidates]
    scored.sort(key=lambda x: x[0], reverse=True)

    return scored[0][1]


def score_organo(match: OrganMatch, block: TextBlock) -> int:
    """
    Calcula la puntuación de un órgano para un bloque dado.
    """
    score = 0

    # Puntuación base por tipo
    score += TYPE_SCORES.get(match.organ_type, 2)

    # Bonificación por sección (indica órgano específico)
    if match.seccion:
        score += 5

    # Bonificación por localidad definida
    if match.locality:
        score += 3

    # Bonificación por plaza definida
    if match.numero_plaza:
        score += 2

    # Bonificación por cercanía al inicio del bloque
    pos_in_block = match.start - block.start
    if pos_in_block < 150:
        score += 2
    elif pos_in_block < 300:
        score += 1

    # Penalización por alias histórico
    if match.alias_historico:
        score -= 5

    # Penalización si está dentro de cláusula accesoria
    if _is_in_accessory_clause(match, block):
        score -= 3

    # Penalización si parece alias corto
    if _looks_like_alias(match.raw):
        score -= 8

    return score


def _is_in_accessory_clause(match: OrganMatch, block: TextBlock) -> bool:
    """
    Verifica si el órgano está dentro de una cláusula accesoria.

    Busca patrones como "mientras su titular", "servicios especiales",
    etc. en el contexto inmediato del órgano dentro del bloque.
    """
    # Posición relativa del órgano dentro del bloque
    rel_start = match.start - block.start
    rel_end = match.end - block.start

    # Ventana de contexto: 300 chars antes del órgano
    window_start = max(0, rel_start - 300)
    context = block.text[window_start:rel_end]

    for pattern in ACCESSORY_CLAUSES:
        if re.search(pattern, context, re.IGNORECASE):
            return True

    return False


def _looks_like_alias(raw: str) -> bool:
    """Detecta si un órgano parece ser un alias histórico tipo 'JPI 14'."""
    if re.match(r'^(antes\s+)?[A-Z]+(?:\s*\d+)?$', raw.strip(), re.IGNORECASE):
        return True
    if len(raw.split()) <= 2 and re.search(r'\d', raw):
        return True
    return False
