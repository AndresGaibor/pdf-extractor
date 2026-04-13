"""
Extractor de órganos judiciales basado en patrones declarativos.

Aplica los patrones de organ_patterns.py sobre texto normalizado
y devuelve una lista de OrganMatch con posición, tipo y localidad.
"""

import re

from src.infrastructure.pdf.organ_patterns import (
    ORGAN_PATTERNS,
    compile_organ_pattern,
)
from src.infrastructure.pdf.parse_models import OrganMatch


def extract_organs(text: str) -> list[OrganMatch]:
    """
    Extrae todos los órganos judiciales encontrados en el texto.

    Normaliza el texto, aplica patrones compilados y devuelve
    una lista de OrganMatch deduplicada y ordenada por posición.
    """
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\u2018', "'").replace('\u2019', "'")

    compiled = compile_organ_pattern()
    matches: list[OrganMatch] = []
    vistos: set[str] = set()

    for match in compiled.finditer(text):
        organo_raw = match.group(0).strip()
        organo_raw = re.sub(r'[;:,.\s]+$', '', organo_raw)
        organo_raw = re.sub(r'\s+', ' ', organo_raw)

        if organo_raw in vistos:
            continue
        vistos.add(organo_raw)

        organ_type, locality = _classify_match(organo_raw, text, match.start(), match.end())
        matches.append(OrganMatch(
            raw=organo_raw,
            organ_type=organ_type,
            locality=locality,
            start=match.start(),
            end=match.end(),
        ))

    # Ordenar por posición de aparición
    matches.sort(key=lambda m: m.start)
    return matches


def _classify_match(
    raw: str,
    text: str,
    start: int,
    end: int,
) -> tuple[str, str]:
    """
    Determina el tipo canónico y localidad de un órgano detectado.

    Revisa cada patrón específico para clasificar el match encontrado.
    """
    for pattern in ORGAN_PATTERNS:
        m = re.match(pattern.pattern, raw, re.VERBOSE | re.IGNORECASE)
        if not m:
            continue

        if not pattern.has_locality:
            return (pattern.type_name, "")

        # Intentar extraer localidad de grupos de captura
        groups = m.groups()
        if groups and groups[-1]:
            locality = groups[-1].strip()
            locality = re.sub(r'[.,;:\s]+$', '', locality)
            return (pattern.type_name, locality)

        # Si el patrón tiene localidad pero no capturó grupo, intentar regex posterior
        type_name, locality = _separate_tipo_localidad(raw, pattern.type_name)
        return (type_name, locality)

    # Fallback: no se pudo clasificar
    return (raw, "")


def _separate_tipo_localidad(raw: str, default_type: str) -> tuple[str, str]:
    """
    Separa tipo y localidad de un órgano cuando el patrón no capturó grupo.
    Usa la misma lógica que el método _separar_tipo_y_localidad original.
    """
    if not raw:
        return ("", "")

    # Tribunales sin localidad
    for prefix in [
        r'Tribunal\s+Supremo',
        r'Tribunal\s+Constitucional',
        r'Audiencia\s+Nacional',
        r'Juzgado(?:s)?\s+Central',
    ]:
        if re.match(prefix, raw, re.IGNORECASE):
            return (raw, "")

    # TSJ de <lugar>
    m = re.match(r'(Tribunal\s+Superior\s+de\s+Justicia)\s+de\s+(.+)', raw, re.IGNORECASE)
    if m:
        return (m.group(1).strip(), m.group(2).strip())

    # Audiencia Provincial de <lugar>
    m = re.match(r'(Audiencia\s+Provincial)\s+de\s+(.+)', raw, re.IGNORECASE)
    if m:
        return (m.group(1).strip(), m.group(2).strip())

    # Tribunal de Instancia
    m = re.match(r'(Tribunal\s+(?:Central\s+)?de\s+Instancia)\s+(?:de\s+)?(.+)', raw, re.IGNORECASE)
    if m:
        return (m.group(1).strip(), m.group(2).strip())
    m = re.match(r'(Tribunal\s+(?:Central\s+)?de\s+Instancia)$', raw, re.IGNORECASE)
    if m:
        return (m.group(1).strip(), "")

    # Oficina de Justicia de <lugar>
    m = re.match(r'(Oficina\s+de\s+Justicia)\s+de\s+(.+)', raw, re.IGNORECASE)
    if m:
        return (m.group(1).strip(), m.group(2).strip())

    # Juzgados especializados
    especializaciones = (
        r'Primera\s+Instancia(?:\s+e\s+Instrucción)?'
        r'|Instrucción'
        r'|lo\s+Mercantil'
        r'|lo\s+Penal'
        r'|lo\s+Social'
        r'|lo\s+Contencioso[\-\s]Administrativo'
        r'|Violencia\s+(?:sobre\s+la\s+Mujer|de\s+Género)'
        r'|Menores'
        r'|Vigilancia\s+Penitenciaria'
        r'|Paz'
    )

    m = re.match(
        rf'(Juzgado\s+de\s+(?:{especializaciones})'
        rf'(?:\s+(?:nº|n°|n\.|número|num\.?|Nº|N\.|No\.?)\s*\d+)?)'
        rf'\s+de\s+(.+)',
        raw, re.IGNORECASE
    )
    if m:
        return (m.group(1).strip(), m.group(2).strip())

    # Fallback genérico
    m = re.match(r'(Juzgado\s+.+?)\s+de\s+([A-ZÁÉÍÓÚÜÑL\'][^\n]+)$', raw, re.IGNORECASE)
    if m:
        posible_lugar = m.group(2).strip()
        if posible_lugar and posible_lugar[0].isupper():
            return (m.group(1).strip(), posible_lugar)

    return (raw, "")
