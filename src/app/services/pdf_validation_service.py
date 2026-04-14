"""
Servicio de validación de extracción de PDFs contra resultados esperados.

Compara resultados extraídos con golden files JSON y genera reportes
de diferencias con métricas de calidad.
"""

import csv
import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import Optional

from src.domain.models.extracted_data import ExtractedRow
from src.domain.models.validation_result import (
    FieldMismatch,
    ValidationDiff,
    ValidationReport,
)

logger = logging.getLogger(__name__)


class PDFValidationService:
    """Valida resultados de extracción contra golden files esperados."""

    def __init__(
        self,
        expected_dir: str = "data/expected",
        report_dir: str = "artifacts/validation",
    ):
        self.expected_dir = Path(expected_dir)
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def load_expected(self, pdf_name: str) -> Optional[list[dict]]:
        """Carga el golden file esperado para un PDF."""
        safe_name = _safe_filename(pdf_name)
        expected_path = self.expected_dir / f"{safe_name}.expected.json"

        if not expected_path.exists():
            logger.info("No expected file for %s", pdf_name)
            return None

        with open(expected_path, encoding="utf-8") as f:
            return json.load(f)

    def save_expected(self, pdf_name: str, rows: list[ExtractedRow]) -> Path:
        """Guarda un golden file esperado desde filas extraídas."""
        self.expected_dir.mkdir(parents=True, exist_ok=True)
        safe_name = _safe_filename(pdf_name)
        expected_path = self.expected_dir / f"{safe_name}.expected.json"

        data = [row.to_dict() for row in rows]
        with open(expected_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info("Expected saved to %s", expected_path)
        return expected_path

    def validate(
        self,
        pdf_name: str,
        actual_rows: list[ExtractedRow],
        expected_rows: Optional[list[dict]] = None,
    ) -> Optional[ValidationDiff]:
        """
        Valida filas extraídas contra el esperado.

        Si no hay expected_rows, intenta cargarlo del golden file.
        Si tampoco existe golden file, devuelve None (sin validar).
        """
        if expected_rows is None:
            expected_rows = self.load_expected(pdf_name)

        if expected_rows is None:
            return None

        return self._compute_diff(pdf_name, expected_rows, actual_rows)

    def _compute_diff(
        self,
        pdf_name: str,
        expected: list[dict],
        actual: list[ExtractedRow],
    ) -> ValidationDiff:
        """Calcula las diferencias entre esperado y actual."""
        diff = ValidationDiff(
            pdf_name=pdf_name,
            expected_rows=len(expected),
            actual_rows=len(actual),
            total_expected_participants=len(expected),
        )

        # Normalizar filas para comparación
        expected_normalized = [normalize_row(r) for r in expected]
        actual_normalized = [normalize_row(r.to_dict()) for r in actual]

        # Buscar participantes esperados en los actuales
        expected_participants = {
            normalize_value(r.get("participante", ""))
            for r in expected_normalized
            if r.get("participante")
        }
        actual_participants = {
            normalize_value(r.get("participante", ""))
            for r in actual_normalized
            if r.get("participante")
        }

        matched = expected_participants & actual_participants
        diff.matched_participants = len(matched)
        diff.missing_participants = list(expected_participants - actual_participants)
        diff.extra_participants = list(actual_participants - expected_participants)

        # Comparar campo por campo para participantes coincidentes
        for exp_row in expected_normalized:
            participant = exp_row.get("participante", "")
            norm_participant = normalize_value(participant)

            if norm_participant not in actual_participants:
                continue

            # Buscar fila actual correspondiente
            act_row = next(
                (r for r in actual_normalized
                 if normalize_value(r.get("participante", "")) == norm_participant),
                None,
            )
            if act_row is None:
                continue

            # Comparar campos
            for field_name in [
                "cargo", "tribunal_origen", "tribunal_destino",
                "prov_loc_origen", "prov_loc_destino",
            ]:
                exp_val = normalize_value(exp_row.get(field_name, ""))
                act_val = normalize_value(act_row.get(field_name, ""))

                if exp_val and act_val and exp_val != act_val:
                    diff.field_mismatches.append(FieldMismatch(
                        participante=participant,
                        field=field_name,
                        expected=exp_val,
                        actual=act_val,
                    ))

        return diff

    def save_report(self, report: ValidationReport) -> Path:
        """Guarda el reporte en JSON y CSV."""
        # JSON
        json_path = self.report_dir / "latest_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)

        # CSV
        csv_path = self.report_dir / "latest_report.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "pdf", "expected_rows", "actual_rows",
                "matched", "total_expected", "match_rate",
                "missing_participants", "extra_participants",
                "field_mismatches", "is_passing",
            ])
            for d in report.diffs:
                writer.writerow([
                    d.pdf_name,
                    d.expected_rows,
                    d.actual_rows,
                    d.matched_participants,
                    d.total_expected_participants,
                    round(d.participant_match_rate, 3),
                    "; ".join(d.missing_participants),
                    "; ".join(d.extra_participants),
                    len(d.field_mismatches),
                    d.is_passing,
                ])

        logger.info("Report saved to %s and %s", json_path, csv_path)
        return json_path


def normalize_value(value: str) -> str:
    """
    Normaliza un valor para comparación tolerante.

    - Elimina espacios múltiples
    - Convierte a minúsculas
    - Normaliza acentos (NFD -> NFC sin combining marks)
    - Elimina guiones raros OCR
    - Normaliza variantes de separación
    """
    if not value:
        return ""

    value = value.strip()

    # Minúsculas
    value = value.lower()

    # Normalizar acentos: convertir á->a, é->e, etc.
    value = unicodedata.normalize("NFD", value)
    value = "".join(
        c for c in value
        if unicodedata.category(c) != "Mn"
    )

    # Normalizar separadores
    value = value.replace("-", " ")
    value = re.sub(r"\s+", " ", value)

    # Eliminar prefijos Doña/Don
    value = re.sub(r"^\s*(don|do[ñn]a)\s+", "", value)

    return value.strip()


def normalize_row(row: dict) -> dict:
    """Normaliza todos los valores de una fila."""
    return {k: normalize_value(v) if isinstance(v, str) else v
            for k, v in row.items()}


def _safe_filename(name: str) -> str:
    """Convierte un nombre de archivo en uno seguro para path."""
    safe = re.sub(r'[<>:"/\\|?*]', '_', name)
    safe = re.sub(r'\s+', '_', safe)
    return safe
