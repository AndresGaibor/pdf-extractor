import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from typing import List

class FilePickerWidget:
    def __init__(self, master, label: str = "Seleccionar archivos PDF"):
        self.master = master
        self.label = label
        self.selected_files: List[str] = []
        
        self.frame = ttk.Frame(master)
        self.btn = ttk.Button(
            self.frame, 
            text=self.label, 
            command=self._pick_files,
            bootstyle=INFO
        )
        self.btn.pack(pady=10)
        
        self.status_label = ttk.Label(self.frame, text="Ningún archivo seleccionado")
        self.status_label.pack()

    def _pick_files(self):
        files = filedialog.askopenfilenames(
            title=self.label,
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if files:
            self.selected_files = list(files)
            count = len(self.selected_files)
            self.status_label.config(text=f"{count} archivo(s) seleccionado(s)")
        else:
            self.selected_files = []
            self.status_label.config(text="Ningún archivo seleccionado")

    def get_selected_files(self) -> List[str]:
        return self.selected_files

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
