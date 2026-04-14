"""
Selector de órganos por scoring dentro de un bloque de texto.

Reemplaza "primer órgano encontrado" por un sistema de puntuación
que elige el órgano más representativo para origen o destino.
"""

import re
from typing import Optional

from src.infrastructure.pdf.parse_models import OrganMatch

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


def select_organs_by_block(
    organ_matches: list[OrganMatch],
    block_text: str,
) -> list[OrganMatch]:
    """
    Filtra órganos que aparecen dentro de un bloque de texto dado.

    Usa las posiciones (start/end) de cada órgano para verificar
    si está contenido en el bloque.
    """
    if not block_text or not organ_matches:
        return []

    # Encontrar la posición del bloque dentro del párrafo original
    # Como block_text es un substring del párrafo, buscamos cada órgano
    # por su raw text en el bloque
    result: list[OrganMatch] = []
    for organ in organ_matches:
        if organ.raw in block_text:
            result.append(organ)
    return result


def pick_best_organo(
    organ_matches: list[OrganMatch],
    block_text: str,
) -> Optional[OrganMatch]:
    """
    Selecciona el mejor órgano de un bloque usando scoring.

    Reglas de scoring:
    +10: Audiencia Provincial o TSJ
    +9: Tribunal de Instancia
    +8: Tribunal Supremo o Audiencia Nacional
    +5: Tiene sección
    +3: Tiene localidad
    +2: Está cerca del inicio del bloque (primer órgano suele ser el relevante)
    -5: Parece alias corto
    -3: Está dentro de cláusula "mientras su titular"
    -2: Está dentro de "(antes ...)"
    """
    if not organ_matches:
        return None

    # Filtrar por bloque primero
    candidates = select_organs_by_block(organ_matches, block_text)
    if not candidates:
        # Si no encontró por posición, buscar por contenido
        for organ in organ_matches:
            if organ.raw in block_text:
                candidates.append(organ)

    if not candidates:
        return None

    scored = [(score_organo(m, block_text), m) for m in candidates]
    scored.sort(key=lambda x: x[0], reverse=True)

    return scored[0][1]


def score_organo(match: OrganMatch, block_text: str) -> int:
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
    pos_in_block = _position_in_block(match, block_text)
    if pos_in_block is not None and pos_in_block < 200:
        score += 2

    # Penalización por alias histórico
    if match.alias_historico:
        score -= 5

    # Penalización si está dentro de cláusula "mientras su titular"
    if _is_in_while_clause(match, block_text):
        score -= 3

    # Penalización si parece alias corto
    if _looks_like_alias(match.raw):
        score -= 8

    return score


def _position_in_block(match: OrganMatch, block_text: str) -> Optional[int]:
    """Devuelve la posición del órgano dentro del bloque."""
    idx = block_text.find(match.raw)
    if idx >= 0:
        return idx
    return None


def _is_in_while_clause(match: OrganMatch, block_text: str) -> bool:
    """Verifica si el órgano está dentro de una cláusula 'mientras su titular'."""
    idx = block_text.find(match.raw)
    if idx < 0:
        return False

    # Buscar "mientras" en los 300 chars anteriores al órgano
    window_start = max(0, idx - 300)
    context = block_text[window_start:idx]
    return bool(re.search(r'mientras\s+(su\s+titular|se\s+encuentre)', context, re.IGNORECASE))


def _looks_like_alias(raw: str) -> bool:
    """Detecta si un órgano parece ser un alias histórico tipo 'JPI 14'."""
    if re.match(r'^(antes\s+)?[A-Z]+(?:\s*\d+)?$', raw.strip(), re.IGNORECASE):
        return True
    if len(raw.split()) <= 2 and re.search(r'\d', raw):
        return True
    return False
