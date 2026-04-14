"""
Patrones pequeños para detectar órganos judiciales en texto de BOE.

Cada patrón es independiente y se puede depurar de forma aislada.
Los patrones devuelven grupos nombrados cuando es posible para facilitar
la extracción de tipo y localidad.
"""

import re
from dataclasses import dataclass


# Fragmento reusable para nombres de lugar (ciudades, provincias)
# Non-greedy para no capturar más de la cuenta
LUGAR = r"[A-ZÁÉÍÓÚÜÑL'][\wáéíóúüñÁÉÍÓÚÜÑ\s\-']*?"

# Palabras que indican fin de un órgano judicial
FIN_ORGANO = (
    r'(?=\s*[,.:;()]'
    r'|\s+(?:pasará|había|tramit|resolv|remit|interpon|admit|dictad|también|previamente|finalmente'
    r'|\by\s+(?:al|el|la|los|las|del|de|[A-ZÁÉÍÓÚÜÑ])|que\s+sirve|de\s+(?:familia|adscripción))'
    r'|\s*$)'
)


@dataclass
class OrganPattern:
    """Patrón individual para detectar un tipo de órgano judicial."""
    name: str           # identificador legible
    pattern: str        # expresión regular
    type_name: str      # nombre canónico del tipo de órgano
    has_locality: bool  # si el patrón incluye captura de localidad


# Secciones comunes de Tribunales de Instancia
SECCIONES_TI = (
    r"Sección\s+de\s+(?:"
    r"Instrucción"
    r"|lo\s+Penal"
    r"|lo\s+Civil"
    r"|lo\s+Social"
    r"|lo\s+Contencioso[\-\s]Administrativo"
    r"|Violencia\s+sobre\s+la\s+Mujer"
    r"|Familia,\s*Infancia\s+y\s+Capacidad"
    r"|Menores"
    r"|Vigilancia\s+Penitenciaria"
    r"|[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]+?"
    r")"
)

# Lista de patrones ordenados de más específico a más genérico
ORGAN_PATTERNS: list[OrganPattern] = [
    OrganPattern(
        name="tribunal_supremo",
        pattern=r"Tribunal\s+Supremo(?:\s+\([^)]+\))?",
        type_name="Tribunal Supremo",
        has_locality=False,
    ),
    OrganPattern(
        name="tribunal_constitucional",
        pattern=r"Tribunal\s+Constitucional",
        type_name="Tribunal Constitucional",
        has_locality=False,
    ),
    OrganPattern(
        name="audiencia_nacional",
        pattern=r"Audiencia\s+Nacional(?:\s+de\s+[\w\s]+)?",
        type_name="Audiencia Nacional",
        has_locality=False,
    ),
    OrganPattern(
        name="tsj",
        pattern=rf"Tribunal\s+Superior\s+de\s+Justicia\s+de\s+({LUGAR}{FIN_ORGANO})",
        type_name="Tribunal Superior de Justicia",
        has_locality=True,
    ),
    OrganPattern(
        name="audiencia_provincial",
        pattern=rf"Audiencia\s+Provincial\s+de\s+({LUGAR}{FIN_ORGANO})",
        type_name="Audiencia Provincial",
        has_locality=True,
    ),
    # Patrón nuevo: Sección del Tribunal de Instancia (prioridad alta)
    OrganPattern(
        name="seccion_ti",
        pattern=rf"{SECCIONES_TI}\s+del\s+Tribunal\s+(?:Central\s+)?de\s+Instancia\s+de\s+({LUGAR}{FIN_ORGANO})",
        type_name="Tribunal de Instancia",
        has_locality=True,
    ),
    OrganPattern(
        name="tribunal_instancia",
        pattern=rf"Tribunal\s+(?:Central\s+)?de\s+Instancia(?:\s+(?:de\s+)?{LUGAR})?{FIN_ORGANO}",
        type_name="Tribunal de Instancia",
        has_locality=True,
    ),
    OrganPattern(
        name="sala_tsj",
        pattern=rf"Sala\s+de\s+[\w\s]+?\s+del\s+Tribunal\s+Superior\s+de\s+Justicia\s+de\s+({LUGAR}{FIN_ORGANO})",
        type_name="Tribunal Superior de Justicia",
        has_locality=True,
    ),
    OrganPattern(
        name="juzgado_central",
        pattern=r"Juzgado(?:s)?\s+Central(?:es)?\s+de\s+(?:Instrucción|lo\s+Penal|Menores|Vigilancia\s+Penitenciaria|lo\s+Contencioso-Administrativo)(?:\s+nº?\s*\d+)?",
        type_name="Juzgado Central",
        has_locality=False,
    ),
    OrganPattern(
        name="oficina_justicia",
        pattern=rf"Oficina\s+de\s+Justicia\s+de\s+({LUGAR}{FIN_ORGANO})",
        type_name="Oficina de Justicia",
        has_locality=True,
    ),
    # Juzgados especializados con número y localidad opcional
    OrganPattern(
        name="juzgado_especializado",
        pattern=(
            r"Juzgado\s+de\s+(?:"
            r"Primera\s+Instancia(?:\s+e\s+Instrucción)?"
            r"|Instrucción"
            r"|lo\s+Mercantil"
            r"|lo\s+Penal"
            r"|lo\s+Social"
            r"|lo\s+Contencioso[\-\s]Administrativo"
            r"|Violencia\s+(?:sobre\s+la\s+Mujer|de\s+Género)"
            r"|Menores"
            r"|Vigilancia\s+Penitenciaria"
            r"|Paz"
            rf")(?:\s+(?:nº|n°|n\.|número|num\.?|Nº|N\.|No\.?)\s*\d+)?"
            rf"(?:\s+de\s+{LUGAR})?{FIN_ORGANO}"
        ),
        type_name="Juzgado",
        has_locality=True,
    ),
    # Patrón genérico fallback: "Juzgado de <algo> de <lugar>"
    OrganPattern(
        name="juzgado_generico",
        pattern=rf"Juzgado\s+de\s+[\w\s]+?\s+de\s+({LUGAR}{FIN_ORGANO})",
        type_name="Juzgado",
        has_locality=True,
    ),
]


# Catálogos de tipos y conectores para uso en parsing
TRIBUNAL_TYPES = [
    "Tribunal Supremo",
    "Tribunal Constitucional",
    "Audiencia Nacional",
    "Tribunal Superior de Justicia",
    "Audiencia Provincial",
    "Tribunal de Instancia",
    "Tribunal Central de Instancia",
    "Oficina de Justicia",
]

JUZGADO_SPECIALIZATIONS = [
    "Primera Instancia",
    "Primera Instancia e Instrucción",
    "Instrucción",
    "lo Mercantil",
    "lo Penal",
    "lo Social",
    "lo Contencioso-Administrativo",
    "lo Contencioso Administrativo",
    "Violencia sobre la Mujer",
    "Violencia de Género",
    "Menores",
    "Vigilancia Penitenciaria",
    "Paz",
]

SECCIONES_LIST = [
    "Instrucción",
    "lo Penal",
    "lo Civil",
    "lo Social",
    "lo Contencioso-Administrativo",
    "lo Contencioso Administrativo",
    "Violencia sobre la Mujer",
    "Familia, Infancia y Capacidad",
    "Menores",
    "Vigilancia Penitenciaria",
]

CARGO_SEPARATORS = [" del ", " de ", " que sirve "]

ORGAN_STOP_WORDS = [
    "pasará", "había", "tramit", "resolv", "remit", "interpon",
    "admit", "dictad", "también", "previamente", "finalmente",
]

# Bloques de texto que indican fin de resoluciones útiles
# Deben ser suficientemente específicos para no coincidir con encabezados
CUTOFF_MARKERS = [
    "Excluir las siguientes solicitudes",
    "La incidencia que en la resolución",
    "Contra la presente disposición",
    "Los Magistrados/as nombrados/as",
    "Los/as jueces/zas nombrados/as",
    "Excluir las siguientes",
]


def compile_organ_pattern() -> re.Pattern:
    """Compila todos los patrones en un solo regex alternativo."""
    subpatterns = [p.pattern for p in ORGAN_PATTERNS]
    combined = "(?:" + "|".join(subpatterns) + ")"
    return re.compile(combined, re.VERBOSE | re.IGNORECASE)
