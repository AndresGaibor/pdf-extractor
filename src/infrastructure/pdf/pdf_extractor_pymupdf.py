"""
Extractor de PDF usando PyMuPDF como motor de conversión a markdown.

Este módulo actúa como orquestador del pipeline de extracción:
1. Lee PDF y convierte a markdown (PyMuPDF)
2. Limpia ruido BOE
3. Agrupa párrafos numerados
4. Extrae órganos judiciales
5. Parsea cada párrafo en ExtractedRow

La lógica de parsing vive en módulos separados para ser testeable
independientemente del motor PDF.
"""

import logging
import os
import tempfile
from typing import List

from src.domain.models.extracted_data import ExtractedRow
from src.domain.interfaces.extraction_interfaces import IPDFExtractor
from src.domain.services.transform_data import TransformDataService

from src.infrastructure.pdf.text_cleaner import clean_all_boe_noise
from src.infrastructure.pdf.paragraph_splitter import build_candidate_paragraphs
from src.infrastructure.pdf.organ_extractor import extract_organs
from src.infrastructure.pdf.row_parser import parse_paragraph
from src.infrastructure.pdf.parse_debug import (
    DebugRecorder,
    log_parse_issue,
    log_paragraph_summary,
)

logger = logging.getLogger(__name__)


class PyMuPDFExtractor(IPDFExtractor):
    """Orquestador de extracción de datos de PDFs BOE."""

    def __init__(
        self,
        transform_service: TransformDataService,
        debug: bool = False,
    ):
        self.transform_service = transform_service
        self.debug = debug
        self._debug_recorder = DebugRecorder(enabled=debug)

    def extract_from_path(self, file_path: str) -> List[ExtractedRow]:
        """Extrae datos de un archivo PDF en disco."""
        import pymupdf4llm  # importación diferida

        md_text = pymupdf4llm.to_markdown(file_path)
        return self._extract_from_markdown(md_text)

    def extract_from_bytes(self, file_bytes: bytes) -> List[ExtractedRow]:
        """Extrae datos de un PDF en memoria (bytes)."""
        import pymupdf4llm  # importación diferida

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            md_text = pymupdf4llm.to_markdown(tmp_path)
            return self._extract_from_markdown(md_text)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _extract_from_markdown(self, md_text: str) -> List[ExtractedRow]:
        """
        Pipeline principal de extracción desde texto markdown.

        Orquesta: limpieza -> agrupación -> parsing -> resultados.
        """
        # 1. Limpiar ruido BOE
        clean_text = clean_all_boe_noise(md_text)

        # 2. Agrupar párrafos numerados
        parrafos = build_candidate_paragraphs(clean_text)

        # 3. Parsear cada párrafo
        filas: List[ExtractedRow] = []
        for parrafo in parrafos:
            try:
                row = self._parsear_fila(parrafo)
                if row:
                    filas.append(row)
            except Exception as e:
                # Ya no se ocultan errores silenciosamente
                log_parse_issue(parrafo, "fila", str(e))
                self._debug_recorder.record_paragraph(
                    parrafo,
                    issues=[{"stage": "fila", "error": str(e)}],
                )
                continue

        # Guardar datos de depuración si están habilitados
        if self.debug:
            self._debug_recorder.save()

        return filas

    def _parsear_fila(self, parrafo: str) -> ExtractedRow | None:
        """
        Parsea un párrafo individual y devuelve un ExtractedRow.

        Coordina extracción de órganos y parsing de campos.
        """
        # Extraer órganos judiciales usando el sistema de patrones
        organ_matches = extract_organs(parrafo)

        # Parsear participante, cargo y provincias
        row = parse_paragraph(parrafo, organ_matches, self.transform_service)

        # Logging para depuración
        if row:
            log_paragraph_summary(parrafo, row.participante, [o.raw for o in organ_matches], [])
            self._debug_recorder.record_paragraph(
                parrafo,
                participante=row.participante,
                cargo=row.cargo,
                organos=[o.raw for o in organ_matches],
                row=row.to_dict(),
            )
        else:
            log_parse_issue(
                parrafo,
                "participante",
                "Participante vacío o menos de 2 palabras",
                context=f"Órganos encontrados: {len(organ_matches)}",
            )
            self._debug_recorder.record_paragraph(
                parrafo,
                organos=[o.raw for o in organ_matches],
                issues=[{"stage": "participante", "error": "vacío o inválido"}],
            )

        return row
