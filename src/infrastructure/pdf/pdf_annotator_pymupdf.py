"""
Anotador de PDFs usando PyMuPDF (fitz).

Resalta textos detectados en amarillo sobre una copia del PDF.
Soporta búsqueda de texto por contenido sin necesitar coordenadas.
"""

import logging
from pathlib import Path

from src.domain.models.annotation_options import AnnotationOptions
from src.domain.models.extracted_data import ExtractedRow

logger = logging.getLogger(__name__)


class PDFAnnotator:
    """Anota PDFs con highlights amarillos sobre textos detectados."""

    def __init__(self, options: AnnotationOptions | None = None):
        self.options = options or AnnotationOptions()

    def annotate(
        self,
        pdf_path: str,
        rows: list[ExtractedRow],
        output_path: str | None = None,
        mismatches: list[str] | None = None,
    ) -> str:
        """
        Anota un PDF resaltando los textos de las filas extraídas.

        Args:
            pdf_path: ruta al PDF original
            rows: filas extraídas del PDF
            output_path: ruta de salida (si None, usa output_dir del options)
            mismatches: lista de participantes con fallos (si annotate_mode=mismatches_only)

        Returns:
            Ruta al PDF anotado.
        """
        import fitz  # importación diferida de PyMuPDF

        doc = fitz.open(pdf_path)
        texts_to_highlight = self._collect_texts(rows, mismatches)

        for span in texts_to_highlight:
            if span.label not in self.options.labels_to_highlight:
                continue

            # Buscar el texto en todas las páginas
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_instances = page.search_for(span.text)

                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors(
                        stroke=self.options.highlight_color
                    )
                    highlight.update()

                    if self.options.add_comments:
                        highlight.set_info(
                            title=f"Detectado: {span.label}",
                            content=span.text
                        )
                        highlight.update()

        # Determinar ruta de salida
        if output_path:
            out_path = Path(output_path)
        elif self.options.in_place:
            out_path = Path(pdf_path)
        else:
            self.options.output_dir = Path(self.options.output_dir)
            self.options.output_dir.mkdir(parents=True, exist_ok=True)
            base = Path(pdf_path).stem
            out_path = self.options.output_dir / f"{base}.annotated.pdf"

        # Asegurar que el directorio existe
        out_path.parent.mkdir(parents=True, exist_ok=True)

        doc.save(str(out_path))
        doc.close()

        logger.info("PDF anotado guardado en %s", out_path)
        return str(out_path)

    def _collect_texts(
        self,
        rows: list[ExtractedRow],
        mismatches: list[str] | None = None,
    ) -> list:
        """
        Recolecta los textos a resaltar desde las filas extraídas.
        """
        from src.domain.models.annotation_options import DetectedSpan

        spans = []

        for row in rows:
            # Determinar si este participante debe anotarse
            if mismatches is not None:
                if row.participante not in mismatches:
                    continue

            if row.participante:
                spans.append(DetectedSpan(
                    text=row.participante,
                    label="participante",
                ))

            if row.tribunal_origen:
                spans.append(DetectedSpan(
                    text=row.tribunal_origen,
                    label="origen",
                ))

            if row.tribunal_destino:
                spans.append(DetectedSpan(
                    text=row.tribunal_destino,
                    label="destino",
                ))

        return spans
