"""
Utilidades de logging y trazabilidad para depuración del parsing.

Proporciona funciones para registrar problemas de parsing
y un modo debug que guarda información detallada de cada párrafo.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from src.infrastructure.pdf.parse_models import (
    ExtractionResult,
    ParseIssue,
)

logger = logging.getLogger(__name__)


def log_parse_issue(parrafo: str, stage: str, error: str, context: str = "") -> None:
    """Registra un problema de parsing con contexto para depuración."""
    preview = parrafo[:200].replace('\n', ' ')
    logger.warning(
        "Parse issue [%s]: %s | Contexto: %s | Extra: %s",
        stage, error, preview, context
    )


def log_paragraph_summary(
    parrafo: str,
    participante: str,
    organos: list[str],
    issues: list[ParseIssue],
) -> None:
    """Registra un resumen del parsing de un párrafo."""
    if issues:
        logger.info(
            "Párrafo parseado: participante=%s, órganos=%d, issues=%d | %s",
            participante or "(ninguno)",
            len(organos),
            len(issues),
            parrafo[:100].replace('\n', ' ')
        )
    else:
        logger.debug(
            "Párrafo OK: participante=%s, órganos=%d | %s",
            participante or "(ninguno)",
            len(organos),
            parrafo[:100].replace('\n', ' ')
        )


class DebugRecorder:
    """
    Graba información detallada de cada párrafo parseado
    para análisis posterior.

    Uso:
        recorder = DebugRecorder(output_dir="data/debug")
        recorder.record_paragraph(...)
        recorder.save()
    """

    def __init__(self, output_dir: str = "data/debug", enabled: bool = False):
        self.enabled = enabled
        self.output_dir = Path(output_dir)
        self.entries: list[dict] = []

    def record_paragraph(
        self,
        raw_text: str,
        participante: str = "",
        cargo: str = "",
        organos: list[str] = None,
        provincias: dict[int, str] = None,
        row: Optional[dict] = None,
        issues: list[dict] = None,
    ) -> None:
        """Graba la información de un párrafo parseado."""
        if not self.enabled:
            return

        self.entries.append({
            "paragraph_preview": raw_text[:200],
            "participante": participante,
            "cargo": cargo,
            "organos": organos or [],
            "provincias_explicitas": provincias or {},
            "row": row,
            "issues": issues or [],
        })

    def save(self) -> Optional[Path]:
        """Guarda todas las entradas en un archivo JSON."""
        if not self.enabled or not self.entries:
            return None

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / "extraction_debug.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)

        logger.info("Debug data saved to %s", output_path)
        return output_path

    def reset(self) -> None:
        """Limpia las entradas guardadas."""
        self.entries.clear()


def extraction_result_to_debug_dict(result: ExtractionResult) -> dict:
    """Convierte un ExtractionResult en un dict para depuración."""
    return {
        "total_paragraphs": result.total_paragraphs,
        "valid_paragraphs": result.valid_paragraphs,
        "rows_extracted": len(result.rows),
        "issues_count": len(result.issues),
        "issues": [
            {
                "paragraph_preview": issue.paragraph_preview,
                "stage": issue.stage,
                "error": issue.error,
                "context": issue.context,
            }
            for issue in result.issues
        ],
        "rows": [r.to_dict() for r in result.rows],
    }
