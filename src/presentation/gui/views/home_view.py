import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinter import ttk

from src.presentation.gui.controllers.process_controller import ProcessController
from src.presentation.gui.widgets.file_picker import FilePickerWidget


class HomeView(ctk.CTkFrame):
    def __init__(self, master, controller: ProcessController):
        super().__init__(master)
        self.controller = controller
        self.all_rows = []
        self._setup_ui()

    def _setup_ui(self):
        # Título
        title_label = ctk.CTkLabel(
            self,
            text="Extractor de Datos de PDF",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # Widget de selección de archivos
        self.file_picker = FilePickerWidget(self)
        self.file_picker.pack(fill="x", pady=10)

        # Botón de procesamiento
        self.process_btn = ctk.CTkButton(
            self,
            text="Procesar PDFs",
            command=self._on_process,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.process_btn.pack(pady=10)

        # Panel de métricas
        self.metrics_frame = ctk.CTkFrame(self)
        self.metrics_frame.pack(fill="x", pady=20)

        self.lbl_count = ctk.CTkLabel(
            self.metrics_frame,
            text="Participantes: 0",
            font=ctk.CTkFont(family="Helvetica", size=10, weight="bold")
        )
        self.lbl_count.pack(side="left", padx=20, pady=10)

        self.lbl_files = ctk.CTkLabel(
            self.metrics_frame,
            text="PDFs: 0",
            font=ctk.CTkFont(family="Helvetica", size=10, weight="bold")
        )
        self.lbl_files.pack(side="left", padx=20, pady=10)

        # Tabla de resultados
        self._setup_table()

        # Botón de descarga
        self.download_btn = ctk.CTkButton(
            self,
            text="Descargar Excel",
            command=self._on_download,
            fg_color="#3498db",
            hover_color="#2980b9",
            state="disabled"
        )
        self.download_btn.pack(pady=20)

    def _setup_table(self):
        # Crear un Treeview estándar de tkinter para la tabla de resultados
        table_container = ctk.CTkFrame(self)
        table_container.pack(fill="both", expand=True)

        columns = ("participante", "cargo", "t_origen", "t_destino", "loc_origen", "loc_destino")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings")

        # Configurar encabezadas
        self.tree.heading("participante", text="Participante")
        self.tree.heading("cargo", text="Cargo")
        self.tree.heading("t_origen", text="T. Origen")
        self.tree.heading("t_destino", text="T. Destino")
        self.tree.heading("loc_origen", text="Loc. Origen")
        self.tree.heading("loc_destino", text="Loc. Destino")

        # Configurar columnas
        for col in columns:
            self.tree.column(col, stretch=True, width=150)

        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _on_process(self):
        file_paths = self.file_picker.get_selected_files()
        if not file_paths:
            messagebox.showwarning("Atención", "Por favor, seleccione al menos un archivo PDF.")
            return

        self.process_btn.configure(state="disabled")

        try:
            all_rows, errors = self.controller.process_files_by_path(file_paths)
            self.all_rows = all_rows

            if errors:
                error_msg = "\n".join([f"{name}: {err}" for name, err in errors])
                messagebox.showerror("Errores durante el procesamiento", f"Ocurrieron errores en los siguientes archivos:\n\n{error_msg}")

            if all_rows:
                self._update_results(all_rows, len(file_paths))
                self.download_btn.configure(state="normal")
            else:
                messagebox.showinfo("Información", "No se encontraron datos para extraer en los PDFs seleccionados.")
                self.download_btn.configure(state="disabled")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {str(e)}")
        finally:
            self.process_btn.configure(state="normal")

    def _update_results(self, rows, num_files):
        # Limpiar tabla actual
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Actualizar métricas
        self.lbl_count.configure(text=f"Participantes: {len(rows)}")
        self.lbl_files.configure(text=f"PDFs: {num_files}")

        # Actualizar tabla
        for r in rows:
            self.tree.insert("", "end", values=(
                r.participante,
                r.cargo,
                r.tribunal_origen,
                r.tribunal_destino,
                r.prov_loc_origen,
                r.prov_loc_destino
            ))

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
