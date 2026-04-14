"""
Validación del baseline técnico actual del extractor.

NO convertir estos tests en especificación semántica.
Solo miden el estado actual para detectar regresión técnica.

Ver hallazgos en: tests/unit/pdf/fixtures/baseline_notes.py
"""

import pytest

from src.domain.services.transform_data import TransformDataService
from src.infrastructure.persistence.territories_repository_json import (
    TerritoriesRepositoryJSON,
)
from src.infrastructure.pdf.pdf_extractor_pymupdf import PyMuPDFExtractor

from tests.unit.pdf.fixtures.baseline_notes import CURRENT_BASELINE


@pytest.fixture
def extractor():
    territories_repo = TerritoriesRepositoryJSON()
    transform_service = TransformDataService(territories_repo)
    return PyMuPDFExtractor(transform_service)


class TestCurrentBaselineSummary:
    """
    Tests de resumen del estado actual del extractor.

    No validan fila por fila. Solo miden métricas generales para
    detectar si una refactorización empeora o mejora el resultado.
    """

    @pytest.mark.skip(
        reason="Requiere PDFs reales en data/pdfs. Ejecutar manualmente tras colocar los PDFs."
    )
    def test_jueces_row_count_baseline(self, extractor):
        """
        El PDF de jueces tiene 20 movimientos resolutivos (Uno a Veinte).
        El extractor actual devuelve 13 filas.
        Este test documenta la diferencia, no la valida como correcta.
        """
        baseline = CURRENT_BASELINE["jueces"]
        assert baseline["expected_resolutive_rows_in_pdf"] == 20
        assert baseline["current_rows_in_excel"] == 13
        assert baseline["missing_rows"] == 7

    @pytest.mark.skip(
        reason="Requiere PDFs reales en data/pdfs. Ejecutar manualmente tras colocar los PDFs."
    )
    def test_magistrados_row_count_baseline(self, extractor):
        """
        El PDF de magistrados tiene 169 movimientos resolutivos.
        El extractor actual devuelve 170 filas (1 espuria).
        Este test documenta la diferencia, no la valida como correcta.
        """
        baseline = CURRENT_BASELINE["magistrados"]
        assert baseline["expected_resolutive_rows_in_pdf"] == 169
        assert baseline["current_rows_in_excel"] == 170
        assert baseline["extra_rows"] == 1

    def test_baseline_notes_are_documented(self):
        """Verifica que las notas de baseline están documentadas."""
        assert "jueces" in CURRENT_BASELINE
        assert "magistrados" in CURRENT_BASELINE
        assert CURRENT_BASELINE["jueces"]["missing_rows"] > 0
        assert CURRENT_BASELINE["magistrados"]["extra_rows"] > 0
