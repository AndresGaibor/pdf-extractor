#!/usr/bin/env python
"""
Validación automática de PDFs reales contra golden files esperados.

Uso:
    uv run python scripts/validate_pdfs.py
    uv run python scripts/validate_pdfs.py --update-expected
    uv run python scripts/validate_pdfs.py --annotate-on-failure
    uv run python scripts/validate_pdfs.py --pdf-dir data/pdfs --strict
"""

import argparse
import logging
import sys
from pathlib import Path

from src.domain.services.transform_data import TransformDataService
from src.infrastructure.pdf.pdf_extractor_pymupdf import PyMuPDFExtractor
from src.infrastructure.persistence.territories_repository_json import (
    TerritoriesRepositoryJSON,
)
from src.app.services.pdf_validation_service import PDFValidationService
from src.domain.models.validation_result import ValidationReport
from src.infrastructure.pdf.pdf_annotator_pymupdf import PDFAnnotator
from src.domain.models.annotation_options import AnnotationOptions

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def discover_pdfs(pdf_dir: str) -> list[Path]:
    """Descubre todos los PDFs en un directorio."""
    pdf_path = Path(pdf_dir)
    if not pdf_path.exists():
        logger.warning("Directorio PDF no existe: %s", pdf_dir)
        return []
    return sorted(pdf_path.glob("*.pdf"))


def build_extractor() -> PyMuPDFExtractor:
    """Construye el extractor con dependencias."""
    territories_repo = TerritoriesRepositoryJSON()
    transform_service = TransformDataService(territories_repo)
    return PyMuPDFExtractor(transform_service)


def run_validation(
    pdf_dir: str,
    expected_dir: str,
    report_dir: str,
    update_expected: bool = False,
    annotate_on_failure: bool = False,
    strict: bool = False,
) -> ValidationReport:
    """Ejecuta la validación completa."""
    validation_service = PDFValidationService(
        expected_dir=expected_dir,
        report_dir=report_dir,
    )
    extractor = build_extractor()
    pdfs = discover_pdfs(pdf_dir)

    report = ValidationReport()
    report.pdfs_processed = len(pdfs)

    if not pdfs:
        logger.warning("No se encontraron PDFs en %s", pdf_dir)
        return report

    for pdf_path in pdfs:
        pdf_name = pdf_path.name
        logger.info("Validando: %s", pdf_name)

        try:
            rows = extractor.extract_from_path(str(pdf_path))
        except Exception as e:
            logger.error("Error extrayendo %s: %s", pdf_name, e)
            report.total_errors.append(f"{pdf_name}: {e}")
            report.pdfs_failed += 1
            continue

        # Si se pide actualizar golden files
        if update_expected:
            validation_service.save_expected(pdf_name, rows)
            logger.info("Expected actualizado para %s (%d filas)", pdf_name, len(rows))
            report.pdfs_passed += 1
            continue

        # Validar
        diff = validation_service.validate(pdf_name, rows)

        if diff is None:
            logger.info("Sin expected para %s - OK", pdf_name)
            report.pdfs_passed += 1
            continue

        report.diffs.append(diff)

        if diff.is_passing:
            logger.info("PASS: %s (%d filas, %d participantes)",
                        pdf_name, diff.actual_rows, diff.matched_participants)
            report.pdfs_passed += 1
        else:
            logger.warning(
                "FAIL: %s - rows=%d/%d, missing=%d, extra=%d, mismatches=%d",
                pdf_name, diff.actual_rows, diff.expected_rows,
                len(diff.missing_participants),
                len(diff.extra_participants),
                len(diff.field_mismatches),
            )
            report.pdfs_failed += 1

            # Anotar PDF si hay fallos
            if annotate_on_failure and diff.missing_participants:
                try:
                    annotator = PDFAnnotator(AnnotationOptions(
                        annotate_mode="mismatches_only",
                    ))
                    annotated_path = annotator.annotate(
                        str(pdf_path),
                        rows,
                        mismatches=diff.missing_participants,
                    )
                    logger.info("PDF anotado: %s", annotated_path)
                except Exception as e:
                    logger.error("Error anotando %s: %s", pdf_name, e)

    # Guardar reporte
    validation_service.save_report(report)

    logger.info(
        "\nResumen: %d/%d pasaron (%.1f%%)",
        report.pdfs_passed, report.pdfs_processed,
        report.overall_pass_rate * 100
    )

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Valida extracción de PDFs contra golden files esperados"
    )
    parser.add_argument(
        "--pdf-dir", default="data/pdfs",
        help="Directorio con PDFs a validar",
    )
    parser.add_argument(
        "--expected-dir", default="data/expected",
        help="Directorio con golden files esperados",
    )
    parser.add_argument(
        "--report-dir", default="artifacts/validation",
        help="Directorio para reportes",
    )
    parser.add_argument(
        "--update-expected", action="store_true",
        help="Regenera los golden files esperados desde la extracción actual",
    )
    parser.add_argument(
        "--annotate-on-failure", action="store_true",
        help="Anota PDFs con highlights donde hay fallos",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Modo estricto: falla si hay cualquier diferencia",
    )

    args = parser.parse_args()

    report = run_validation(
        pdf_dir=args.pdf_dir,
        expected_dir=args.expected_dir,
        report_dir=args.report_dir,
        update_expected=args.update_expected,
        annotate_on_failure=args.annotate_on_failure,
        strict=args.strict,
    )

    if not report.is_passing:
        sys.exit(1)


if __name__ == "__main__":
    main()
