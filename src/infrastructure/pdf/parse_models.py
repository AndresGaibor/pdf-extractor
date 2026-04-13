"""
Modelos intermedios para el parsing de párrafos de BOE.

Estos modelos permiten inspeccionar cada etapa del proceso de extracción
sin saltar directamente de texto crudo a ExtractedRow.
"""

from dataclasses import dataclass, field


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
class ExtractionResult:
    """Resultado completo de una extracción con trazabilidad."""
    rows: list = field(default_factory=list)
    issues: list[ParseIssue] = field(default_factory=list)
    total_paragraphs: int = 0
    valid_paragraphs: int = 0
