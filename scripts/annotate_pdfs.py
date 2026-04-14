#!/usr/bin/env python
"""
Anotación de PDFs con highlights amarillos sobre textos detectados.

Uso:
    uv run python scripts/annotate_pdfs.py --pdf data/PDF.pdf
    uv run python scripts/annotate_pdfs.py --pdf-dir data/pdfs
    uv run python scripts/annotate_pdfs.py --copy --pdf data/PDF.pdf
"""

import argparse
import logging
from pathlib import Path

from src.domain.services.transform_data import TransformDataService
from src.infrastructure.pdf.pdf_extractor_pymupdf import PyMuPDFExtractor
from src.infrastructure.persistence.territories_repository_json import (
    TerritoriesRepositoryJSON,
)
from src.infrastructure.pdf.pdf_annotator_pymupdf import PDFAnnotator
from src.domain.models.annotation_options import AnnotationOptions

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def build_extractor() -> PyMuPDFExtractor:
    """Construye el extractor con dependencias."""
    territories_repo = TerritoriesRepositoryJSON()
    transform_service = TransformDataService(territories_repo)
    return PyMuPDFExtractor(transform_service)


def annotate_single(
    pdf_path: str,
    output_dir: str = "artifacts/annotated",
    in_place: bool = False,
) -> str:
    """Anota un solo PDF con los textos detectados."""
    extractor = build_extractor()
    rows = extractor.extract_from_path(pdf_path)

    options = AnnotationOptions(
        output_dir=output_dir,
        in_place=in_place,
    )
    annotator = PDFAnnotator(options)

    output_path = annotator.annotate(pdf_path, rows)
    logger.info("PDF anotado: %s (%d filas, %d highlights)",
                output_path, len(rows),
                sum(1 for r in rows if r.participante))
    return output_path


def annotate_directory(
    pdf_dir: str,
    output_dir: str = "artifacts/annotated",
    in_place: bool = False,
) -> list[str]:
    """Anota todos los PDFs en un directorio."""
    pdf_path = Path(pdf_dir)
    results = []

    for pdf_file in sorted(pdf_path.glob("*.pdf")):
        try:
            out = annotate_single(str(pdf_file), output_dir, in_place)
            results.append(out)
        except Exception as e:
            logger.error("Error anotando %s: %s", pdf_file.name, e)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Anota PDFs con highlights amarillos"
    )
    parser.add_argument(
        "--pdf", type=str,
        help="Ruta a un PDF específico para anotar",
    )
    parser.add_argument(
        "--pdf-dir", type=str, default="data/pdfs",
        help="Directorio con PDFs para anotar",
    )
    parser.add_argument(
        "--output-dir", type=str, default="artifacts/annotated",
        help="Directorio de salida para PDFs anotados",
    )
    parser.add_argument(
        "--copy", action="store_true", default=True,
        help="Crear copia anotada (por defecto, no sobrescribe original)",
    )
    parser.add_argument(
        "--in-place", action="store_true",
        help="Sobrescribir el original (¡cuidado!)",
    )

    args = parser.parse_args()

    if args.pdf:
        annotate_single(
            args.pdf,
            output_dir=args.output_dir,
            in_place=args.in_place,
        )
    else:
        results = annotate_directory(
            args.pdf_dir,
            output_dir=args.output_dir,
            in_place=args.in_place,
        )
        logger.info("Anotados %d PDFs", len(results))


if __name__ == "__main__":
    main()
