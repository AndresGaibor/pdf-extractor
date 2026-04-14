"""
Tests de párrafos reales con separación SPEC vs BASELINE.

- `active`: deben pasar (especificación firme)
- `xfail`: representan bugs actuales del extractor
- `pending_semantics`: saltados hasta decidir convención funcional

Los expected representan la verdad semántica correcta según el BOE,
no el comportamiento actual del extractor.
"""

import pytest

from src.domain.services.transform_data import TransformDataService
from src.infrastructure.persistence.territories_repository_json import (
    TerritoriesRepositoryJSON,
)
from src.infrastructure.pdf.organ_extractor import extract_organs
from src.infrastructure.pdf.row_parser import parse_paragraph

from tests.unit.pdf.fixtures.spec_cases_jueces import SPEC_CASES_JUECES
from tests.unit.pdf.fixtures.spec_cases_magistrados import SPEC_CASES_MAGISTRADOS


ALL_SPEC_CASES = SPEC_CASES_JUECES + SPEC_CASES_MAGISTRADOS

# Construir parámetros con marcas xfail/skip según el status
SPEC_PARAMS = []
for _c in ALL_SPEC_CASES:
    cid = _c["id"]
    if _c.get("status") == "xfail":
        mark = pytest.mark.xfail(reason=_c.get("reason", "bug actual del extractor"))
    elif _c.get("status") == "pending_semantics":
        mark = pytest.mark.skip(reason=f"pending semantics: {_c.get('reason', '')}")
    else:
        mark = ()
    SPEC_PARAMS.append(pytest.param(_c, marks=mark, id=cid))


def norm(value: str) -> str:
    """Normalización simple: colapsar espacios, no quitar tildes."""
    if value is None:
        return ""
    return " ".join(str(value).split()).strip()


@pytest.fixture
def transform_service():
    territories_repo = TerritoriesRepositoryJSON()
    return TransformDataService(territories_repo)


def _assert_expected(row, expected):
    """Valida campos esperados contra la fila extraída."""
    assert norm(row.participante) == norm(expected["participante"]), (
        f"participante: expected={expected['participante']!r}, got={row.participante!r}"
    )
    assert norm(row.cargo) == norm(expected["cargo"]), (
        f"cargo: expected={expected['cargo']!r}, got={row.cargo!r}"
    )
    assert norm(row.tribunal_origen) == norm(expected["tribunal_origen"]), (
        f"tribunal_origen: expected={expected['tribunal_origen']!r}, got={row.tribunal_origen!r}"
    )
    assert norm(row.tribunal_destino) == norm(expected["tribunal_destino"]), (
        f"tribunal_destino: expected={expected['tribunal_destino']!r}, got={row.tribunal_destino!r}"
    )

    # Provincias: solo validar si el expected no es un placeholder pendiente
    for field in ["prov_loc_origen", "prov_loc_destino"]:
        exp_val = expected.get(field, "")
        if exp_val and "PENDING" not in exp_val and "TODO" not in exp_val:
            assert norm(getattr(row, field)) == norm(exp_val), (
                f"{field}: expected={exp_val!r}, got={getattr(row, field)!r}"
            )


@pytest.mark.parametrize("case", SPEC_PARAMS)
def test_spec_paragraph_case(case, transform_service):
    """
    Valida un párrafo real contra su especificación semántica.

    - active: validación estricta
    - xfail: validación que se espera falle (bug actual)
    - pending_semantics: saltado
    """
    paragraph = case["paragraph"]
    expected = case.get("expected", {})

    organ_matches = extract_organs(paragraph)
    row = parse_paragraph(paragraph, organ_matches, transform_service)

    assert row is not None, f"No se obtuvo fila para el caso {case['id']}"

    _assert_expected(row, expected)

    # Verificar que los aliases no se toman como órganos
    for forbidden in case.get("assert_not_in_organs", []):
        assert all(
            norm(m.raw) != norm(forbidden) for m in organ_matches
        ), f"El alias histórico '{forbidden}' fue detectado como órgano en {case['id']}"
