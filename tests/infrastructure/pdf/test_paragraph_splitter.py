"""Tests para paragraph_splitter.py - agrupación de párrafos numerados."""


from src.infrastructure.pdf.paragraph_splitter import (
    build_candidate_paragraphs,
    is_numbered_paragraph,
    split_paragraphs_only,
)


class TestBuildCandidateParagraphs:
    """Tests para la construcción de párrafos candidatos."""

    def test_groups_numbered_paragraphs(self):
        text = (
            "Uno. Doña María García.\n\n"
            "Continuación del párrafo uno.\n\n"
            "Dos. Don Carlos Rodríguez."
        )
        result = build_candidate_paragraphs(text)
        assert len(result) == 2
        assert result[0].startswith("Uno.")
        assert "Continuación" in result[0]
        assert result[1].startswith("Dos.")

    def test_skips_unnumbered_blocks(self):
        text = "Texto sin numeración.\n\nUno. Doña María."
        result = build_candidate_paragraphs(text)
        assert len(result) == 1
        assert result[0].startswith("Uno.")

    def test_multiple_continuations(self):
        text = (
            "Uno. Doña María.\n\n"
            "Primera continuación.\n\n"
            "Segunda continuación.\n\n"
            "Dos. Don Carlos."
        )
        result = build_candidate_paragraphs(text)
        assert len(result) == 2
        assert "Primera continuación" in result[0]
        assert "Segunda continuación" in result[0]

    def test_empty_text(self):
        result = build_candidate_paragraphs("")
        assert result == []

    def test_only_unnumbered(self):
        text = "Texto sin numeración.\n\nOtro texto."
        result = build_candidate_paragraphs(text)
        assert result == []

    def test_filters_blank_paragraphs(self):
        text = "\n\n\nUno. Doña María.\n\n\nDos. Don Carlos.\n\n"
        result = build_candidate_paragraphs(text)
        assert len(result) == 2
        assert all(p.strip() for p in result)

    def test_handles_various_numberings(self):
        text = (
            "Veinte. Doña Ana.\n\n"
            "Treinta y uno. Don Pedro.\n\n"
            "Ciento cinco. Doña Luisa."
        )
        result = build_candidate_paragraphs(text)
        assert len(result) == 3


class TestIsNumberedParagraph:
    """Tests para detección de párrafos numerados."""

    def test_returns_true_for_valid_numbering(self):
        assert is_numbered_paragraph("Uno. Doña María") is True
        assert is_numbered_paragraph("Dos. Don Carlos") is True
        assert is_numbered_paragraph("Veinte. Doña Ana") is True
        assert is_numbered_paragraph("Ciento. Don Pedro") is True

    def test_returns_false_for_unnumbered(self):
        assert is_numbered_paragraph("Texto sin número") is False
        assert is_numbered_paragraph("1. Número arábigo") is False
        assert is_numbered_paragraph("a) Letra minúscula") is False

    def test_case_sensitive(self):
        # La numeración usa mayúscula inicial
        assert is_numbered_paragraph("uno. minúscula") is False
        assert is_numbered_paragraph("Uno. Mayúscula") is True


class TestSplitParagraphsOnly:
    """Tests para división simple sin agrupación."""

    def test_splits_by_double_newline(self):
        text = "Párrafo uno\n\nPárrafo dos\n\nPárrafo tres"
        result = split_paragraphs_only(text)
        assert len(result) == 3

    def test_filters_empty(self):
        text = "Uno.\n\n\n\nDos."
        result = split_paragraphs_only(text)
        assert len(result) == 2

    def test_preserves_content(self):
        text = "Doña María García\n\nTribunal Supremo"
        result = split_paragraphs_only(text)
        assert "Doña María García" in result[0]
        assert "Tribunal Supremo" in result[1]
