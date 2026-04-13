import customtkinter as ctk
from typing import List
from tkinter import filedialog


class FilePickerWidget:
    def __init__(self, master, label: str = "Seleccionar archivos PDF"):
        self.master = master
        self.label = label
        self.selected_files: List[str] = []

        self.frame = ctk.CTkFrame(master)
        self.btn = ctk.CTkButton(
            self.frame,
            text=self.label,
            command=self._pick_files,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.btn.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.frame, text="Ningún archivo seleccionado")
        self.status_label.pack(pady=5)

    def _pick_files(self):
        files = filedialog.askopenfilenames(
            title=self.label,
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if files:
            self.selected_files = list(files)
            count = len(self.selected_files)
            self.status_label.configure(text=f"{count} archivo(s) seleccionado(s)")
        else:
            self.selected_files = []
            self.status_label.configure(text="Ningún archivo seleccionado")

    def get_selected_files(self) -> List[str]:
        return self.selected_files

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
