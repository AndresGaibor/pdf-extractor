from typing import List, Tuple
from src.app.use_cases.process_pdf import ProcessPDFUseCase
from src.domain.models.extracted_data import ExtractedRow

class ProcessController:
    def __init__(self, process_use_case: ProcessPDFUseCase):
        self.process_use_case = process_use_case

    def process_files_by_path(self, file_paths: List[str]) -> Tuple[List[ExtractedRow], List[Tuple[str, str]]]:
        all_rows = []
        errors = []

        for path in file_paths:
            try:
                rows = self.process_use_case.execute_from_path(path)
                all_rows.extend(rows)
            except Exception as e:
                import os
                filename = os.path.basename(path)
                errors.append((filename, str(e)))
        
        return all_rows, errors

    def process_files(self, uploaded_files) -> Tuple[List[ExtractedRow], List[Tuple[str, str]]]:
        all_rows = []
        errors = []

        for file in uploaded_files:
            try:
                # El objeto 'file' de streamlit tiene un método read()
                file_bytes = file.read()
                rows = self.process_use_case.execute_from_bytes(file_bytes)
                all_rows.extend(rows)
            except Exception as e:
                errors.append((file.name, str(e)))
        
        return all_rows, errors

    def get_excel_report(self, data: List[ExtractedRow]) -> bytes:
        return self.process_use_case.generate_excel(data)
