"""Tests para organ_patterns.py - verificación de patrones individuales."""

import re

from src.infrastructure.pdf.organ_patterns import (
    ORGAN_PATTERNS,
    compile_organ_pattern,
    TRIBUNAL_TYPES,
    JUZGADO_SPECIALIZATIONS,
    CARGO_SEPARATORS,
    ORGAN_STOP_WORDS,
)


class TestOrganPatternsExist:
    """Verifica que los patrones están bien definidos."""

    def test_patterns_list_not_empty(self):
        assert len(ORGAN_PATTERNS) > 0

    def test_each_pattern_has_required_fields(self):
        for p in ORGAN_PATTERNS:
            assert p.name, f"Pattern missing name: {p}"
            assert p.pattern, f"Pattern missing regex: {p}"
            assert p.type_name, f"Pattern missing type_name: {p}"

    def test_compiled_pattern_works(self):
        compiled = compile_organ_pattern()
        assert compiled is not None
        assert isinstance(compiled, re.Pattern)


class TestTribunalSupremoPattern:
    def test_matches_simple(self):
        text = "Tribunal Supremo"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None
        assert match.group(0).strip() == "Tribunal Supremo"

    def test_matches_with_parenthesis(self):
        text = "Tribunal Supremo (Sala Primera)"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None
        assert "Tribunal Supremo" in match.group(0)

    def test_no_locality(self):
        pattern = next(p for p in ORGAN_PATTERNS if p.name == "tribunal_supremo")
        assert pattern.has_locality is False


class TestTribunalConstitucionalPattern:
    def test_matches(self):
        text = "Tribunal Constitucional"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None

    def test_no_locality(self):
        pattern = next(p for p in ORGAN_PATTERNS if p.name == "tribunal_constitucional")
        assert pattern.has_locality is False


class TestAudienciaNacionalPattern:
    def test_matches_simple(self):
        text = "Audiencia Nacional"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None

    def test_matches_with_extension(self):
        text = "Audiencia Nacional de lo Penal"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None


class TestTSJPattern:
    def test_matches_with_locality(self):
        text = "Tribunal Superior de Justicia de Madrid"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None
        assert "Madrid" in match.group(0)

    def test_has_locality(self):
        pattern = next(p for p in ORGAN_PATTERNS if p.name == "tsj")
        assert pattern.has_locality is True


class TestAudienciaProvincialPattern:
    def test_matches(self):
        text = "Audiencia Provincial de Sevilla"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None
        assert "Sevilla" in match.group(0)

    def test_has_locality(self):
        pattern = next(p for p in ORGAN_PATTERNS if p.name == "audiencia_provincial")
        assert pattern.has_locality is True


class TestJuzgadoEspecializadoPattern:
    def test_matches_with_number(self):
        text = "Juzgado de lo Penal nº 2 de Cádiz"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None

    def test_matches_without_locality(self):
        text = "Juzgado de Instrucción nº 5"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None

    def test_matches_primera_instancia(self):
        text = "Juzgado de Primera Instancia nº 3 de Valencia"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None

    def test_matches_violencia_genero(self):
        text = "Juzgado de Violencia sobre la Mujer nº 1 de Granada"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None


class TestJuzgadoCentralPattern:
    def test_matches(self):
        text = "Juzgado Central de Instrucción nº 6"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None

    def test_no_locality(self):
        pattern = next(p for p in ORGAN_PATTERNS if p.name == "juzgado_central")
        assert pattern.has_locality is False


class TestOficinaJusticiaPattern:
    def test_matches(self):
        text = "Oficina de Justicia de Bilbao"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None


class TestTribunalInstanciaPattern:
    def test_matches(self):
        text = "Tribunal de Instancia de Zaragoza"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None

    def test_matches_central(self):
        text = "Tribunal Central de Instancia"
        compiled = compile_organ_pattern()
        match = compiled.search(text)
        assert match is not None


class TestCatalogs:
    """Verifica los catálogos de tipos y conectores."""

    def test_tribunal_types_not_empty(self):
        assert len(TRIBUNAL_TYPES) > 0

    def test_juzgado_specializations_not_empty(self):
        assert len(JUZGADO_SPECIALIZATIONS) > 0

    def test_cargo_separators(self):
        assert " del " in CARGO_SEPARATORS
        assert " de " in CARGO_SEPARATORS

    def test_stop_words_not_empty(self):
        assert len(ORGAN_STOP_WORDS) > 0
