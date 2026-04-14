"""
Modelos para anotación de PDFs con highlights.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DetectedSpan:
    """Representa un texto detectado que se puede resaltar en el PDF."""
    text: str
    label: str  # participante, cargo, origen, destino, provincia
    page: Optional[int] = None


@dataclass
class AnnotationOptions:
    """Opciones para la anotación de PDFs."""
    output_dir: str = "artifacts/annotated"
    in_place: bool = False
    annotate_mode: str = "all"  # "all" | "mismatches_only"
    highlight_color: tuple[float, float, float] = (1.0, 1.0, 0.0)  # amarillo
    labels_to_highlight: list[str] = field(default_factory=lambda: [
        "participante", "origen", "destino",
    ])
    add_comments: bool = True

    @property
    def should_create_copy(self) -> bool:
        return not self.in_place
