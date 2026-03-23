import ttkbootstrap as ttk
from src.infrastructure.persistence.territories_repository_json import TerritoriesRepositoryJSON
from src.domain.services.transform_data import TransformDataService
from src.infrastructure.pdf.pdf_extractor_pymupdf import PyMuPDFExtractor
from src.infrastructure.excel.excel_exporter_openpyxl import OpenPyXLExporter
from src.app.use_cases.process_pdf import ProcessPDFUseCase
from src.presentation.gui.controllers.process_controller import ProcessController
from src.presentation.gui.views.home_view import HomeView

def run_app():
    # Inicializar la ventana principal con un tema de ttkbootstrap
    app = ttk.Window(
        title="Extractor PDF - Clean Architecture 2",
        themename="flatly",
        size=(1000, 800),
        resizable=(True, True)
    )

    # Inyección de dependencias
    territories_repo = TerritoriesRepositoryJSON()
    transform_service = TransformDataService(territories_repo)
    pdf_extractor = PyMuPDFExtractor(transform_service)
    excel_exporter = OpenPyXLExporter()
    
    process_use_case = ProcessPDFUseCase(pdf_extractor, excel_exporter)
    controller = ProcessController(process_use_case)
    
    # Inicializar y empaquetar la vista principal
    view = HomeView(app, controller)
    view.pack(fill="both", expand=True)

    app.mainloop()

if __name__ == "__main__":
    run_app()
