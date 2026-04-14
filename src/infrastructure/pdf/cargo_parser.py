"""
Parser de cargos con reglas estructuradas.

Reemplaza el enfoque split(',') por reglas explícitas que modelan
los cargos reales del BOE:
- juez / jueza
- magistrado / magistrada
- juez de adscripción territorial
- magistrado especialista
- servicios especiales
"""

import re


# Cargos base reconocidos
CARGO_PATTERNS = [
    (
        "juez de adscripción territorial",
        re.compile(
            r'(juez[oa]?)\s+de\s+adscripci[oó]n\s+territorial',
            re.IGNORECASE
        ),
    ),
    (
        "magistrado especialista",
        re.compile(
            r'(magistrad[oa])\s*,\s*especialista\s+(?:en|del)',
            re.IGNORECASE
        ),
    ),
    (
        "magistrado (servicios especiales)",
        re.compile(
            r'(magistrad[oa]|juez[oa]?)\s*,\s*en\s+situaci[oó]n\s+administrativa.*?'
            r'servicios\s+especiales',
            re.IGNORECASE
        ),
    ),
    (
        "fiscal",
        re.compile(
            r'\b(fiscal)\b(?:\s+del\s|\s+de\s+\w+\s|\s+que\s+sirve|\s*$|\s*,)',
            re.IGNORECASE
        ),
    ),
    (
        "letrado",
        re.compile(
            r'\b(letrad[oa])\b(?:\s+del\s|\s+de\s+la\s+)',
            re.IGNORECASE
        ),
    ),
    (
        "juez",
        re.compile(
            r'\b(juez[oa]?)\b(?:\s+que\s+sirve|\s+,|\s+del|\s+de\s)',
            re.IGNORECASE
        ),
    ),
    (
        "magistrado",
        re.compile(
            r'\b(magistrad[oa])\b(?:\s*,|\s+del|\s+de\s|\s+que\s)',
            re.IGNORECASE
        ),
    ),
]


def extract_cargo(parrafo: str) -> str:
    """
    Extrae el cargo del participante del párrafo.

    Estrategia de dos pasos:
    1. Extraer la base del cargo (juez, magistrado, etc.)
    2. Normalizar con calificativos si aplica

    Soporta:
    - "jueza del Juzgado..." → "jueza"
    - "magistrada de la Audiencia..." → "magistrada"
    - "jueza de adscripción territorial del TSJ..." → "jueza de adscripción territorial"
    - "magistrado, especialista en menores" → "magistrado especialista"
    - "juez que sirve en la AP..." → "juez"
    """
    if not parrafo:
        return ""

    # Obtener la porción después de la numeración
    texto = _get_content_after_numbering(parrafo)

    # Intentar patrones especiales primero (más específicos)
    for cargo_name, pattern in CARGO_PATTERNS:
        match = pattern.search(texto)
        if match:
            cargo_base = match.group(1).strip().capitalize()
            return _build_cargo(cargo_base, cargo_name)

    # Fallback: buscar cualquier juez/magistrado
    m = re.search(r'\b(juez[a]?|magistrad[a]?)\b', texto, re.IGNORECASE)
    if m:
        return m.group(1).strip().capitalize()

    return ""


def _get_content_after_numbering(parrafo: str) -> str:
    """Obtiene el contenido después de la numeración inicial."""
    # Quitar "Uno. " o "Veintitres. " etc.
    m = re.match(r'^[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ\s]+\.\s+', parrafo)
    if m:
        return parrafo[m.end():]
    return parrafo


def _build_cargo(cargo_base: str, cargo_name: str) -> str:
    """Construye el cargo final con calificativos."""
    if "adscripción" in cargo_name:
        return f"{cargo_base} de adscripción territorial"
    if "especialista" in cargo_name:
        return f"{cargo_base} especialista"
    if "servicios especiales" in cargo_name:
        return f"{cargo_base} (servicios especiales)"
    return cargo_base


def extract_cargo_from_context(context: str) -> str:
    """
    Extrae cargo de un bloque de texto arbitrario (origen o destino).
    Útil cuando el cargo aparece en contexto diferente al párrafo principal.
    """
    m = re.search(
        r'\b(juez[oa]?|magistrad[oa])\s+'
        r'(?:de\s+adscripci[oó]n\s+territorial\s+)?'
        r'(?:del\s+|de\s+la\s+|de\s+)?',
        context, re.IGNORECASE
    )
    if m:
        base = m.group(1).strip().capitalize()
        if "adscripción" in context[m.start():m.start()+80]:
            return f"{base} de adscripción territorial"
        return base
    return ""
