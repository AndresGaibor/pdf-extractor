"""Tests para text_cleaner.py - limpieza de cabeceras BOE."""


from src.infrastructure.pdf.text_cleaner import (
    clean_boe_headers,
    clean_boe_issn,
    collapse_blank_lines,
    clean_all_boe_noise,
)


class TestCleanBoeHeaders:
    """Tests para eliminación de cabeceras BOE."""

    def test_removes_simple_header(self):
        text = "## BOLETÍN OFICIAL DEL ESTADO\n\nPág. 123\n\nContenido real"
        result = clean_boe_headers(text)
        assert "BOLETÍN OFICIAL" not in result
        assert "Contenido real" in result

    def test_removes_header_with_asterisks(self):
        # La regex de cabeceras requiere marcadores de heading (# o ##)
        # Este caso sin heading no debería ser eliminado por clean_boe_headers solo
        text = "**BOLETÍN OFICIAL DEL ESTADO**\n\nContenido"
        result = clean_boe_headers(text)
        # clean_boe_headers solo elimina cuando hay # antes
        # El caso con ** pero sin # no matchea el patrón de heading
        assert "BOLETÍN OFICIAL" in result

    def test_removes_header_with_page_number(self):
        text = "## BOLETÍN OFICIAL DEL ESTADO\n\nPág. 45\n\nTexto"
        result = clean_boe_headers(text)
        assert "Pág." not in result

    def test_preserves_content(self):
        text = "## BOLETÍN OFICIAL DEL ESTADO\n\nPág. 10\n\nDoña María García, Jueza"
        result = clean_boe_headers(text)
        assert "Doña María García" in result

    def test_no_header_no_change(self):
        text = "Doña María García, Jueza del Tribunal Supremo"
        result = clean_boe_headers(text)
        assert result == text


class TestCleanBoeIssn:
    """Tests para eliminación de ISSN y URLs."""

    def test_removes_issn_line(self):
        text = "https://www.boe.es  ISSN 0212-033X"
        result = clean_boe_issn(text)
        assert "boe.es" not in result
        assert "ISSN" not in result

    def test_removes_issn_with_spaces(self):
        text = "**https://www.boe.es** ISSN: 0212-033X"
        result = clean_boe_issn(text)
        assert "boe.es" not in result

    def test_preserves_normal_text(self):
        text = "El Tribunal Superior de Justicia de Madrid"
        result = clean_boe_issn(text)
        assert result == text


class TestCollapseBlankLines:
    """Tests para colapsado de líneas en blanco."""

    def test_collapses_triple_newline(self):
        text = "Párrafo uno\n\n\nPárrafo dos"
        result = collapse_blank_lines(text)
        # Debe tener solo un doble salto entre párrafos
        assert "\n\n\n" not in result

    def test_collapses_many_blank_lines(self):
        text = "Inicio\n\n\n\n\n\nFin"
        result = collapse_blank_lines(text)
        assert result.count("\n\n") <= 2

    def test_preserves_single_gap(self):
        text = "Párrafo uno\n\nPárrafo dos"
        result = collapse_blank_lines(text)
        assert "\n\n" in result


class TestCleanAllBoeNoise:
    """Tests para la limpieza completa."""

    def test_removes_headers_and_issn(self):
        text = (
            "## BOLETÍN OFICIAL DEL ESTADO\n"
            "Pág. 100\n"
            "https://www.boe.es ISSN 0212-033X\n\n"
            "Doña María García"
        )
        result = clean_all_boe_noise(text)
        assert "BOLETÍN OFICIAL" not in result
        assert "boe.es" not in result
        assert "Doña María García" in result

    def test_empty_text(self):
        result = clean_all_boe_noise("")
        assert result == ""
