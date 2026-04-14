"""
Tests de párrafos reales de BOE con validación completa del pipeline.

Itera sobre todos los casos de jueces y magistrados, ejecuta el parser
y valida campo por campo contra los expected.
"""

import pytest

from src.domain.services.transform_data import TransformDataService
from src.infrastructure.persistence.territories_repository_json import (
    TerritoriesRepositoryJSON,
)
from src.infrastructure.pdf.organ_extractor import extract_organs
from src.infrastructure.pdf.row_parser import parse_paragraph

from tests.unit.pdf.fixtures.paragraph_cases_jueces import PARAGRAPH_CASES_JUECES
from tests.unit.pdf.fixtures.paragraph_cases_magistrados import PARAGRAPH_CASES_MAGISTRADOS


ALL_PARAGRAPH_CASES = PARAGRAPH_CASES_JUECES + PARAGRAPH_CASES_MAGISTRADOS


def _norm(value: str) -> str:
    """Normaliza un valor para comparación tolerante."""
    if value is None:
        return ""
    return " ".join(str(value).split()).strip()


@pytest.fixture
def transform_service():
    territories_repo = TerritoriesRepositoryJSON()
    return TransformDataService(territories_repo)


@pytest.mark.parametrize(
    "case",
    ALL_PARAGRAPH_CASES,
    ids=[case["id"] for case in ALL_PARAGRAPH_CASES],
)
def test_parse_real_boe_paragraph(case, transform_service):
    """
    Parsea un párrafo real de BOE y valida la salida contra expected.

    Valida:
    - participant
    - cargo
    - tribunal_origen
    - tribunal_destino
    - prov_loc_origen (si no es TODO_CONFIRM_OUTPUT)
    - prov_loc_destino (si no es TODO_CONFIRM_OUTPUT)
    - alias históricos no detectados como órganos
    """
    paragraph = case["paragraph"]
    expected = case["expected"]

    organ_matches = extract_organs(paragraph)
    row = parse_paragraph(paragraph, organ_matches, transform_service)

    assert row is not None, f"No se obtuvo fila para el caso {case['id']}"

    assert _norm(row.participante) == _norm(expected["participante"]), (
        f"Participante: expected={expected['participante']!r}, got={row.participante!r}"
    )
    assert _norm(row.cargo) == _norm(expected["cargo"]), (
        f"Cargo: expected={expected['cargo']!r}, got={row.cargo!r}"
    )
    assert _norm(row.tribunal_origen) == _norm(expected["tribunal_origen"]), (
        f"Tribunal origen: expected={expected['tribunal_origen']!r}, got={row.tribunal_origen!r}"
    )
    assert _norm(row.tribunal_destino) == _norm(expected["tribunal_destino"]), (
        f"Tribunal destino: expected={expected['tribunal_destino']!r}, got={row.tribunal_destino!r}"
    )

    # Verificar provincias solo si no son TODO_CONFIRM_OUTPUT
    if expected.get("prov_loc_origen") != "TODO_CONFIRM_OUTPUT":
        assert _norm(row.prov_loc_origen) == _norm(expected["prov_loc_origen"]), (
            f"Prov origen: expected={expected['prov_loc_origen']!r}, got={row.prov_loc_origen!r}"
        )

    if expected.get("prov_loc_destino") != "TODO_CONFIRM_OUTPUT":
        assert _norm(row.prov_loc_destino) == _norm(expected["prov_loc_destino"]), (
            f"Prov destino: expected={expected['prov_loc_destino']!r}, got={row.prov_loc_destino!r}"
        )

    # Verificar que los alias históricos no fueron detectados como órganos
    for forbidden in case.get("assert_not_in_organs", []):
        assert all(
            _norm(m.raw) != _norm(forbidden) for m in organ_matches
        ), f"El alias histórico '{forbidden}' fue detectado como órgano en {case['id']}"
