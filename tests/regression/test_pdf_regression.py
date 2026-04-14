"""
Tests de regresión con PDFs reales de data/pdfs.

Estos tests validan que el extractor no regrese en calidad
cuando se hacen cambios al parser.

Se ejecutan con:
    uv run pytest -m regression

En CI actual no son obligatorios (se excluyen del run principal).
"""

import json
import os

import pytest

from src.domain.services.transform_data import TransformDataService
from src.infrastructure.pdf.pdf_extractor_pymupdf import PyMuPDFExtractor
from src.infrastructure.persistence.territories_repository_json import (
    TerritoriesRepositoryJSON,
)
from src.app.services.pdf_validation_service import (
    normalize_value,
)
from tests.regression.fixtures.expected_loader import discover_cases


@pytest.fixture(scope="module")
def extractor():
    """Extractor compartido para todos los tests de regresión."""
    territories_repo = TerritoriesRepositoryJSON()
    transform_service = TransformDataService(territories_repo)
    return PyMuPDFExtractor(transform_service)


@pytest.mark.regression
class TestPdfRegression:
    """Tests de regresión end-to-end con PDFs reales."""

    @pytest.mark.parametrize("pdf_path,expected_path", discover_cases())
    def test_pdf_does_not_crash(self, extractor, pdf_path, expected_path):
        """El extractor no debe explotar con ningún PDF real."""
        rows = extractor.extract_from_path(pdf_path)
        assert rows is not None
        # Si hay expected, al menos debemos tener algo
        if expected_path and os.path.exists(expected_path):
            with open(expected_path, encoding="utf-8") as f:
                expected = json.load(f)
            # Debe extraer al menos el 50% de las filas esperadas
            assert len(rows) >= len(expected) * 0.5, (
                f"Extrajo solo {len(rows)} de {len(expected)} filas esperadas"
            )

    @pytest.mark.parametrize("pdf_path,expected_path", discover_cases())
    def test_pdf_participant_match_rate(self, extractor, pdf_path, expected_path):
        """La tasa de coincidencia de participantes debe ser >= 90%."""
        if expected_path is None or not os.path.exists(expected_path):
            pytest.skip(f"No hay expected file para {pdf_path}")

        with open(expected_path, encoding="utf-8") as f:
            expected = json.load(f)

        rows = extractor.extract_from_path(pdf_path)

        expected_participants = {
            normalize_value(r.get("participante", ""))
            for r in expected
            if r.get("participante")
        }
        actual_participants = {
            normalize_value(r.participante)
            for r in rows
            if r.participante
        }

        matched = expected_participants & actual_participants
        total = len(expected_participants)

        if total == 0:
            return

        match_rate = len(matched) / total
        assert match_rate >= 0.90, (
            f"Participant match rate: {match_rate:.1%} "
            f"({len(matched)}/{total}). "
            f"Missing: {expected_participants - actual_participants}"
        )

    @pytest.mark.parametrize("pdf_path,expected_path", discover_cases())
    def test_pdf_row_count_tolerance(self, extractor, pdf_path, expected_path):
        """El conteo de filas debe estar dentro de un 10% del esperado."""
        if expected_path is None or not os.path.exists(expected_path):
            pytest.skip(f"No hay expected file para {pdf_path}")

        with open(expected_path, encoding="utf-8") as f:
            expected = json.load(f)

        rows = extractor.extract_from_path(pdf_path)
        expected_count = len(expected)
        actual_count = len(rows)

        if expected_count == 0:
            return

        tolerance = max(1, int(expected_count * 0.10))
        assert abs(actual_count - expected_count) <= tolerance, (
            f"Row count difference: {actual_count} vs {expected_count} "
            f"(tolerance: ±{tolerance})"
        )


@pytest.mark.regression
class TestValidationService:
    """Tests del servicio de validación."""

    def test_normalize_value_strips_accents(self):
        assert normalize_value("María") == "maria"
        assert normalize_value("Juzgado") == "juzgado"

    def test_normalize_value_strips_don_dona(self):
        assert normalize_value("Doña Ana") == "ana"
        assert normalize_value("Don Pedro") == "pedro"

    def test_normalize_value_collapses_spaces(self):
        assert normalize_value("Tribunal   Supremo") == "tribunal supremo"

    def test_normalize_value_handles_empty(self):
        assert normalize_value("") == ""
        assert normalize_value("   ") == ""

    def test_normalize_value_normalizes_hyphens(self):
        assert normalize_value("Contencioso-Administrativo") == "contencioso administrativo"
