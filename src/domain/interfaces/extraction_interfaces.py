from abc import ABC, abstractmethod
from typing import List
from src.domain.models.extracted_data import ExtractedRow

class IPDFExtractor(ABC):
    @abstractmethod
    def extract_from_path(self, file_path: str) -> List[ExtractedRow]:
        """Extrae datos de un archivo PDF dado su ruta."""
        pass

    @abstractmethod
    def extract_from_bytes(self, file_bytes: bytes) -> List[ExtractedRow]:
        """Extrae datos de bytes de un PDF."""
        pass

class IExcelExporter(ABC):
    @abstractmethod
    def generate_excel_bytes(self, data: List[ExtractedRow]) -> bytes:
        """Genera un archivo Excel en memoria y devuelve los bytes."""
        pass
