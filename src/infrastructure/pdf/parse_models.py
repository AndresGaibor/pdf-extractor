"""
Modelos intermedios para el parsing de párrafos de BOE.

Estos modelos permiten inspeccionar cada etapa del proceso de extracción
sin saltar directamente de texto crudo a ExtractedRow.
"""

from dataclasses import dataclass, field


@dataclass
class TextBlock:
    """
    Representa un bloque de texto con su posición absoluta en el párrafo.

    Permite filtrar órganos por rango real en vez de substring matching.
    """
    text: str
    start: int  # posición inicial en el párrafo original
    end: int    # posición final (exclusiva) en el párrafo original


@dataclass
class OrganMatch:
    """Representa un órgano judicial detectado en el texto."""
    raw: str
    organ_type: str       # e.g. "Audiencia Provincial", "Juzgado de lo Penal"
    locality: str         # e.g. "Sevilla", ""
    start: int            # posición inicial en el texto
    end: int              # posición final en el texto
    seccion: str = ""     # e.g. "Sección de Instrucción", ""
    numero_plaza: str = "" # e.g. "1", ""
    alias_historico: str = "" # e.g. "JINSTR 1", ""
    observaciones: list[str] = field(default_factory=list)


@dataclass
class ParseIssue:
    """Representa un problema encontrado durante el parsing de un párrafo."""
    paragraph_preview: str  # primeros 200 chars del párrafo
    stage: str              # en qué etapa ocurrió (participant, cargo, organs, provinces)
    error: str              # descripción del error
    context: str = ""       # información adicional para depuración


@dataclass
class ParsedParagraph:
    """Representación intermedia de un párrafo parseado."""
    raw_text: str
    participante: str = ""
    cargo: str = ""
    organ_matches: list[OrganMatch] = field(default_factory=list)
    provincias_explicitas: dict[int, str] = field(default_factory=dict)
    issues: list[ParseIssue] = field(default_factory=list)

    @property
    def organos(self) -> list[str]:
        return [m.raw for m in self.organ_matches]

    @property
    def is_valid(self) -> bool:
        return bool(self.participante) and len(self.participante.split()) >= 2


@dataclass
class ParagraphParseResult:
    """
    Resultado completo del parsing de un párrafo con trazabilidad.

    Contiene toda la información necesaria para entender por qué
    se eligieron ciertos órganos y por qué pudo fallar el parsing.
    """
    raw_text: str
    participante: str = ""
    cargo: str = ""

    # Bloques de origen/destino con posiciones
    bloque_origen: TextBlock | None = None
    bloque_destino: TextBlock | None = None

    # Órganos filtrados por bloque
    organos_origen: list[OrganMatch] = field(default_factory=list)
    organos_destino: list[OrganMatch] = field(default_factory=list)

    # Órganos elegidos (mejor puntuación)
    origen_elegido: OrganMatch | None = None
    destino_elegido: OrganMatch | None = None

    # Resultado final
    tribunal_origen: str = ""
    tribunal_destino: str = ""
    prov_loc_origen: str = ""
    prov_loc_destino: str = ""

    # Diagnóstico
    issues: list[ParseIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return bool(self.participante) and bool(self.tribunal_origen)

    def to_debug_dict(self) -> dict:
        """Convierte en dict para depuración."""
        return {
            "raw_preview": self.raw_text[:200],
            "participante": self.participante,
            "cargo": self.cargo,
            "bloque_origen": self.bloque_origen.text[:100] if self.bloque_origen else None,
            "bloque_destino": self.bloque_destino.text[:100] if self.bloque_destino else None,
            "organos_origen": [o.raw for o in self.organos_origen],
            "organos_destino": [o.raw for o in self.organos_destino],
            "origen_elegido": self.origen_elegido.raw if self.origen_elegido else None,
            "destino_elegido": self.destino_elegido.raw if self.destino_elegido else None,
            "tribunal_origen": self.tribunal_origen,
            "tribunal_destino": self.tribunal_destino,
            "issues": [{"stage": i.stage, "error": i.error, "context": i.context} for i in self.issues],
        }


@dataclass
class ExtractionResult:
    """Resultado completo de una extracción con trazabilidad."""
    rows: list = field(default_factory=list)
    issues: list[ParseIssue] = field(default_factory=list)
    total_paragraphs: int = 0
    valid_paragraphs: int = 0
