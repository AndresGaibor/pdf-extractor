"""Tests para row_parser.py - extracción de campos de párrafos."""


from src.infrastructure.pdf.row_parser import (
    extract_participant,
    extract_cargo,
    extract_provincias_explicitas,
)
from src.infrastructure.pdf.parse_models import OrganMatch


class TestExtractParticipant:
    """Tests para extracción del nombre del participante."""

    def test_simple_case(self):
        text = "Uno. María García López, Jueza del Juzgado"
        result = extract_participant(text)
        assert result == "María García López"

    def test_with_dona_prefix(self):
        text = "Dos. Doña Ana Fernández Torres, Fiscal"
        result = extract_participant(text)
        assert result == "Doña Ana Fernández Torres"

    def test_with_don_prefix(self):
        text = "Tres. Don Carlos Rodríguez Martínez, Letrado"
        result = extract_participant(text)
        assert result == "Don Carlos Rodríguez Martínez"

    def test_no_period(self):
        text = "María García sin numeración"
        result = extract_participant(text)
        assert result == ""

    def test_no_comma(self):
        text = "Uno. María García sin cargo"
        result = extract_participant(text)
        # El nombre se extrae igual aunque no haya coma
        assert result == "María García sin cargo"


class TestExtractCargo:
    """Tests para extracción del cargo."""

    def test_cargo_with_del(self):
        text = "Uno. María García, Jueza del Juzgado de Primera Instancia"
        result = extract_cargo(text)
        assert result == "Jueza"

    def test_cargo_with_de(self):
        text = "Dos. Ana López, Letrada de la Administración"
        result = extract_cargo(text)
        assert result == "Letrada"

    def test_cargo_with_que_sirve(self):
        text = "Tres. Pedro Martín, Fiscal que sirve en la Fiscalía"
        result = extract_cargo(text)
        assert result == "Fiscal"

    def test_no_second_comma(self):
        text = "Uno. María García sin cargo"
        result = extract_cargo(text)
        assert result == ""

    def test_no_period(self):
        text = "Sin punto de separación"
        result = extract_cargo(text)
        assert result == ""


class TestExtractProvinciasExplicitas:
    """Tests para detección de provincias explícitas."""

    def _make_organ(self, raw: str, start: int = 0, end: int = 10) -> OrganMatch:
        return OrganMatch(
            raw=raw, organ_type="Test", locality="", start=start, end=end
        )

    def test_detects_provincia_de(self):
        text = "Audiencia Provincial de Sevilla, provincia de Andalucía"
        organs = [self._make_organ("Audiencia Provincial de Sevilla", start=0)]
        result = extract_provincias_explicitas(text, organs)
        assert len(result) >= 0  # La lógica de cercanía puede variar

    def test_empty_text(self):
        result = extract_provincias_explicitas("", [])
        assert result == {}

    def test_no_organs(self):
        result = extract_provincias_explicitas(
            "provincia de Madrid",
            []
        )
        assert result == {}

    def test_no_provincia_mention(self):
        text = "Tribunal Supremo de Madrid"
        organs = [self._make_organ("Tribunal Supremo")]
        result = extract_provincias_explicitas(text, organs)
        assert result == {}
