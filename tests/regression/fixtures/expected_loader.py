"""
Loader de golden files esperados para tests de regresión.
"""

import json
from pathlib import Path

EXPECTED_DIR = Path("data/expected")


def load_expected(pdf_name: str) -> list[dict] | None:
    """Carga el golden file esperado para un PDF."""
    safe_name = _safe_filename(pdf_name)
    expected_path = EXPECTED_DIR / f"{safe_name}.expected.json"

    if not expected_path.exists():
        return None

    with open(expected_path, encoding="utf-8") as f:
        return json.load(f)


def discover_cases() -> list[tuple[str, str | None]]:
    """
    Descubre pares (pdf_path, expected_path) para tests parametrizados.

    Devuelve lista de (pdf_path, expected_path_or_None).
    Si no hay expected, el test solo valida que no explote.
    """
    from src.app.services.pdf_validation_service import _safe_filename

    pdf_dir = Path("data/pdfs")
    if not pdf_dir.exists():
        return []

    cases = []
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        safe_name = _safe_filename(pdf_path.name)
        expected_path = EXPECTED_DIR / f"{safe_name}.expected.json"
        expected = str(expected_path) if expected_path.exists() else None
        cases.append((str(pdf_path), expected))

    return cases


def _safe_filename(name: str) -> str:
    import re
    safe = re.sub(r'[<>:"/\\|?*]', '_', name)
    safe = re.sub(r'\s+', '_', safe)
    return safe
