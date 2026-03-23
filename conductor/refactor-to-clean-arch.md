# Refactor Implementation Plan: Clean Architecture

This plan details the transition of the PDF extractor project to a Clean Architecture structure, improving maintainability, testability, and separation of concerns.

## Objective
Refactor the existing monolithic/grouped scripts into a modular structure:
- **Domain**: Pure business logic, models, and interfaces.
- **Application**: Use cases orchestrating domain objects.
- **Infrastructure**: Implementation details (PDF parsing, Excel generation, data persistence).
- **Presentation**: User interface (Streamlit GUI) and its controllers.

## Key Files & Context
- `extraccion.py`, `extractors.py`, `territorios.py`: Current logic to be redistributed.
- `gui.py`: Current Streamlit interface to be modularized.
- `constants.py`: Shared constants.
- `territorios_espana.json`: External data dependency.

## Implementation Steps

### Phase 1: Domain & Models
1. **Create `domain/models/extracted_data.py`**:
   - Define a dataclass `ExtractedRow` to represent the output record.
2. **Create `domain/errors/domain_errors.py`**:
   - Define custom exceptions like `PDFProcessingError`, `ExcelGenerationError`.
3. **Create `domain/services/transform_data.py`**:
   - Move `_resolver_localidad` and formatting logic here.
4. **Create `domain/interfaces/`**:
   - `IPDFExtractor`: Interface for converting PDF/bytes to domain models.
   - `IExcelExporter`: Interface for generating Excel files from models.

### Phase 2: Infrastructure (Adapters)
1. **Create `infrastructure/pdf/pdf_extractor_pymupdf.py`**:
   - Implement `IPDFExtractor` using `pymupdf4llm`.
   - Incorporate `_limpiar_cabeceras_boe` and the extraction regex/logic from `extractors.py`.
2. **Create `infrastructure/excel/excel_exporter_openpyxl.py`**:
   - Implement `IExcelExporter` using `openpyxl`.
   - Include styling and layout logic from `generar_excel_bytes`.
3. **Create `infrastructure/persistence/territories_repository_json.py`**:
   - Refactor `territorios.py` to act as a repository for Spanish territory data.

### Phase 3: Application (Use Cases)
1. **Create `app/use_cases/process_pdf.py`**:
   - Implement `ProcessPDFUseCase`.
   - Orchestrate: Extract -> Transform -> (Optional) Export.

### Phase 4: Presentation (GUI)
1. **Create `presentation/gui/widgets/file_picker.py`**:
   - Modularize the `st.file_uploader`.
2. **Create `presentation/gui/controllers/process_controller.py`**:
   - Bridge between GUI events and `ProcessPDFUseCase`.
3. **Create `presentation/gui/views/home_view.py`**:
   - Refactor the main layout, metrics, and dataframes from `gui.py`.
4. **Create `presentation/gui/main_window.py`**:
   - The main entry point for Streamlit.

### Phase 5: Integration & Cleanup
1. **Create `main.py`**:
   - Simple entry point that calls the Streamlit application.
2. **Update `pyproject.toml`** (if needed) and `README.md`.
3. **Delete old files**: `extraccion.py`, `extractors.py`, `gui.py`, `territorios.py` after verification.

## Verification & Testing
- **Unit Tests**: Test `transform_data.py` and infrastructure implementations individually.
- **Integration Test**: Run the full flow (PDF -> Excel) to ensure data integrity.
- **Manual GUI Test**: Launch the new Streamlit interface and verify multi-file upload and download functionality.
