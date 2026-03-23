import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from ttkbootstrap.constants import BOTH, DISABLED, INFO, LEFT, NORMAL, PRIMARY, SUCCESS, X, YES
from ttkbootstrap.tableview import Tableview

from src.presentation.gui.controllers.process_controller import ProcessController
from src.presentation.gui.widgets.file_picker import FilePickerWidget


class HomeView(ttk.Frame):
    def __init__(self, master, controller: ProcessController):
        super().__init__(master, padding=20)
        self.controller = controller
        self.all_rows = []
        self._setup_ui()

    def _setup_ui(self):
        # Título
        title_label = ttk.Label(
            self, 
            text="Extractor de Datos de PDF", 
            font=("Helvetica", 18, "bold"),
            bootstyle=PRIMARY
        )
        title_label.pack(pady=(0, 20))

        # Widget de selección de archivos
        self.file_picker = FilePickerWidget(self)
        self.file_picker.pack(fill=X, pady=10)

        # Botón de procesamiento
        self.process_btn = ttk.Button(
            self, 
            text="Procesar PDFs", 
            command=self._on_process,
            bootstyle=SUCCESS
        )
        self.process_btn.pack(pady=10)

        # Panel de métricas
        self.metrics_frame = ttk.Frame(self)
        self.metrics_frame.pack(fill=X, pady=20)
        
        self.lbl_count = ttk.Label(self.metrics_frame, text="Participantes: 0", font=("Helvetica", 10, "bold"))
        self.lbl_count.pack(side=LEFT, padx=20)
        
        self.lbl_files = ttk.Label(self.metrics_frame, text="PDFs: 0", font=("Helvetica", 10, "bold"))
        self.lbl_files.pack(side=LEFT, padx=20)

        # Tabla de resultados
        self._setup_table()

        # Botón de descarga
        self.download_btn = ttk.Button(
            self, 
            text="📥 Descargar Excel", 
            command=self._on_download,
            bootstyle=INFO,
            state=DISABLED
        )
        self.download_btn.pack(pady=20)

    def _setup_table(self):
        self.coldata = [
            {"text": "Participante", "stretch": True},
            {"text": "Cargo", "stretch": True},
            {"text": "T. Origen", "stretch": True},
            {"text": "T. Destino", "stretch": True},
            {"text": "Loc. Origen", "stretch": True},
            {"text": "Loc. Destino", "stretch": True},
        ]
        
        self.table = Tableview(
            master=self,
            coldata=self.coldata,
            rowdata=[],
            paginated=True,
            searchable=True,
            bootstyle=PRIMARY,
            height=10
        )
        self.table.pack(fill=BOTH, expand=YES)

    def _on_process(self):
        file_paths = self.file_picker.get_selected_files()
        if not file_paths:
            messagebox.showwarning("Atención", "Por favor, seleccione al menos un archivo PDF.")
            return

        self.process_btn.config(state=DISABLED)
        
        try:
            all_rows, errors = self.controller.process_files_by_path(file_paths)
            self.all_rows = all_rows

            if errors:
                error_msg = "\n".join([f"{name}: {err}" for name, err in errors])
                messagebox.showerror("Errores durante el procesamiento", f"Ocurrieron errores en los siguientes archivos:\n\n{error_msg}")

            if all_rows:
                self._update_results(all_rows, len(file_paths))
                self.download_btn.config(state=NORMAL)
            else:
                messagebox.showinfo("Información", "No se encontraron datos para extraer en los PDFs seleccionados.")
                self.download_btn.config(state=DISABLED)
                
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {str(e)}")
        finally:
            self.process_btn.config(state=NORMAL)

    def _update_results(self, rows, num_files):
        # Actualizar métricas
        self.lbl_count.config(text=f"Participantes: {len(rows)}")
        self.lbl_files.config(text=f"PDFs: {num_files}")

        # Actualizar tabla
        table_data = []
        for r in rows:
            table_data.append((
                r.participante,
                r.cargo,
                r.tribunal_origen,
                r.tribunal_destino,
                r.prov_loc_origen,
                r.prov_loc_destino
            ))
        
        self.table.build_table_data(coldata=self.coldata, rowdata=table_data)

    def _on_download(self):
        if not self.all_rows:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="participantes.xlsx"
        )
        
        if file_path:
            try:
                excel_bytes = self.controller.get_excel_report(self.all_rows)
                with open(file_path, "wb") as f:
                    f.write(excel_bytes)
                messagebox.showinfo("Éxito", f"Archivo guardado correctamente en:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")
