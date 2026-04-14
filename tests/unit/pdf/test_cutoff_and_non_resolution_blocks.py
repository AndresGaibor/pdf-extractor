"""
Tests de bloques no resolutivos que no deben generar ExtractedRow.

Valida que:
- "Veintiuno. Incidencias..." no genera fila
- "Excluir las siguientes solicitudes:" no genera fila
- "La incidencia que en la resolución..." no genera fila
"""

import pytest

from src.domain.services.transform_data import TransformDataService
from src.infrastructure.persistence.territories_repository_json import (
    TerritoriesRepositoryJSON,
)
from src.infrastructure.pdf.organ_extractor import extract_organs
from src.infrastructure.pdf.row_parser import parse_paragraph

from tests.unit.pdf.fixtures.non_resolution_cases import NON_RESOLUTION_CASES


@pytest.fixture
def transform_service():
    territories_repo = TerritoriesRepositoryJSON()
    return TransformDataService(territories_repo)


@pytest.mark.parametrize(
    "case",
    NON_RESOLUTION_CASES,
    ids=[case["id"] for case in NON_RESOLUTION_CASES],
)
def test_non_resolution_blocks_do_not_generate_rows(case, transform_service):
    """
    Verifica que los bloques no resolutivos no produzcan ExtractedRow.
    """
    paragraph = case["paragraph"]
    organ_matches = extract_organs(paragraph)
    row = parse_paragraph(paragraph, organ_matches, transform_service)

    assert row is None, (
        f"El bloque no resolutivo {case['id']} no debería producir ExtractedRow."
    )
