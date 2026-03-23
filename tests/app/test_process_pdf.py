from src.app.use_cases.process_pdf import ProcessPDFUseCase
from src.domain.models.extracted_data import ExtractedRow


class FakePDFExtractor:
    def __init__(self, rows):
        self.rows = rows
        self.path_calls = []
        self.bytes_calls = []

    def extract_from_path(self, file_path: str):
        self.path_calls.append(file_path)
        return self.rows

    def extract_from_bytes(self, file_bytes: bytes):
        self.bytes_calls.append(file_bytes)
        return self.rows


class FakeExcelExporter:
    def __init__(self, payload: bytes = b"excel"):
        self.payload = payload
        self.calls = []

    def generate_excel_bytes(self, data):
        self.calls.append(data)
        return self.payload


def build_rows():
    return [
        ExtractedRow(
            participante="Ana Perez",
            cargo="Jueza",
            tribunal_origen="Juzgado de lo Penal",
            tribunal_destino="Audiencia Provincial",
            prov_loc_origen="Sevilla (Andalucía)",
            prov_loc_destino="Madrid",
        )
    ]


def test_execute_from_path_delegates_to_pdf_extractor():
    rows = build_rows()
    extractor = FakePDFExtractor(rows)
    exporter = FakeExcelExporter()
    use_case = ProcessPDFUseCase(extractor, exporter)

    result = use_case.execute_from_path("data/ejemplo.pdf")

    assert result == rows
    assert extractor.path_calls == ["data/ejemplo.pdf"]


def test_execute_from_bytes_delegates_to_pdf_extractor():
    rows = build_rows()
    extractor = FakePDFExtractor(rows)
    exporter = FakeExcelExporter()
    use_case = ProcessPDFUseCase(extractor, exporter)

    result = use_case.execute_from_bytes(b"pdf-bytes")

    assert result == rows
    assert extractor.bytes_calls == [b"pdf-bytes"]


def test_generate_excel_delegates_to_excel_exporter():
    rows = build_rows()
    extractor = FakePDFExtractor(rows)
    exporter = FakeExcelExporter(payload=b"excel-bytes")
    use_case = ProcessPDFUseCase(extractor, exporter)

    result = use_case.generate_excel(rows)

    assert result == b"excel-bytes"
    assert exporter.calls == [rows]
