from typing import List
from src.domain.interfaces.extraction_interfaces import IPDFExtractor, IExcelExporter
from src.domain.models.extracted_data import ExtractedRow

class ProcessPDFUseCase:
    def __init__(self, pdf_extractor: IPDFExtractor, excel_exporter: IExcelExporter):
        self.pdf_extractor = pdf_extractor
        self.excel_exporter = excel_exporter

    def execute_from_path(self, file_path: str) -> List[ExtractedRow]:
        """Procesa un PDF desde una ruta y devuelve los datos extraídos."""
        return self.pdf_extractor.extract_from_path(file_path)

    def execute_from_bytes(self, file_bytes: bytes) -> List[ExtractedRow]:
        """Procesa un PDF desde bytes y devuelve los datos extraídos."""
        return self.pdf_extractor.extract_from_bytes(file_bytes)

    def generate_excel(self, data: List[ExtractedRow]) -> bytes:
        """Genera el archivo Excel a partir de los datos."""
        return self.excel_exporter.generate_excel_bytes(data)
