"""Tests para organ_extractor.py - extracción de órganos de texto."""


from src.infrastructure.pdf.organ_extractor import (
    extract_organs,
    _separate_tipo_localidad,
)


class TestExtractOrgans:
    """Tests de alto nivel para la extracción de órganos."""

    def test_single_organ(self):
        text = "Tribunal Supremo"
        results = extract_organs(text)
        assert len(results) == 1
        assert results[0].raw == "Tribunal Supremo"
        assert results[0].organ_type == "Tribunal Supremo"

    def test_two_organs(self):
        text = "Audiencia Provincial de Sevilla y Audiencia Provincial de Cádiz"
        results = extract_organs(text)
        assert len(results) == 2

    def test_deduplication(self):
        text = "Tribunal Supremo y el Tribunal Supremo"
        results = extract_organs(text)
        assert len(results) == 1

    def test_tsj_with_locality(self):
        text = "Tribunal Superior de Justicia de Madrid"
        results = extract_organs(text)
        assert len(results) == 1
        assert results[0].organ_type == "Tribunal Superior de Justicia"
        assert results[0].locality.lower() == "madrid"

    def test_audiencia_provincial_with_locality(self):
        text = "Audiencia Provincial de Barcelona"
        results = extract_organs(text)
        assert len(results) == 1
        assert results[0].organ_type == "Audiencia Provincial"

    def test_juzgado_penal_with_number(self):
        text = "Juzgado de lo Penal nº 2 de Valencia"
        results = extract_organs(text)
        assert len(results) == 1

    def test_juzgado_instruccion(self):
        text = "Juzgado de Instrucción nº 5 de Zaragoza"
        results = extract_organs(text)
        assert len(results) == 1

    def test_juzgado_primera_instancia(self):
        text = "Juzgado de Primera Instancia nº 3 de Sevilla"
        results = extract_organs(text)
        assert len(results) == 1

    def test_juzgado_central(self):
        text = "Juzgado Central de Instrucción nº 6"
        results = extract_organs(text)
        assert len(results) == 1
        assert results[0].organ_type == "Juzgado Central"

    def test_audiencia_nacional(self):
        text = "Audiencia Nacional"
        results = extract_organs(text)
        assert len(results) == 1
        assert results[0].organ_type == "Audiencia Nacional"

    def test_tribunal_constitucional(self):
        text = "Tribunal Constitucional"
        results = extract_organs(text)
        assert len(results) == 1
        assert results[0].organ_type == "Tribunal Constitucional"

    def test_oficina_justicia(self):
        text = "Oficina de Justicia de Bilbao"
        results = extract_organs(text)
        assert len(results) == 1
        assert results[0].organ_type == "Oficina de Justicia"

    def test_empty_text(self):
        results = extract_organs("")
        assert len(results) == 0

    def test_no_organs(self):
        text = "Este texto no contiene órganos judiciales."
        results = extract_organs(text)
        assert len(results) == 0

    def test_ordered_by_position(self):
        text = "Audiencia Provincial de Cádiz y Tribunal Superior de Justicia de Madrid"
        results = extract_organs(text)
        assert len(results) == 2
        assert results[0].start < results[1].start

    def test_matches_have_positions(self):
        text = "Tribunal Supremo"
        results = extract_organs(text)
        assert results[0].start >= 0
        assert results[0].end > results[0].start


class TestSeparateTipoLocalidad:
    """Tests para la separación tipo/localidad."""

    def test_tribunal_supremo_no_locality(self):
        tipo, loc = _separate_tipo_localidad("Tribunal Supremo", "Tribunal Supremo")
        assert tipo == "Tribunal Supremo"
        assert loc == ""

    def test_tsj_with_locality(self):
        tipo, loc = _separate_tipo_localidad(
            "Tribunal Superior de Justicia de Cataluña",
            "Tribunal Superior de Justicia"
        )
        assert tipo == "Tribunal Superior de Justicia"
        assert "Cataluña" in loc

    def test_audiencia_provincial_with_locality(self):
        tipo, loc = _separate_tipo_localidad(
            "Audiencia Provincial de Málaga",
            "Audiencia Provincial"
        )
        assert tipo == "Audiencia Provincial"
        assert "Málaga" in loc

    def test_juzgado_penal_with_locality(self):
        tipo, loc = _separate_tipo_localidad(
            "Juzgado de lo Penal nº 1 de Granada",
            "Juzgado"
        )
        assert "Juzgado de lo Penal" in tipo
        assert "Granada" in loc
