import tkinter as tk
from tkinter import ttk

class GeotechnicalDesignTab(ttk.Frame):
    """Aba para configuracoes e calculos geotecnicos."""

    def __init__(self, parent, main_app=None):
        super().__init__(parent)
        self.main_app = main_app
        self.setup_ui()

    def setup_ui(self):
        """Cria sub-abas basicas de configuracao e metodos de calculo."""
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both", padx=5, pady=5)

        config_frame = ttk.Frame(notebook)
        ttk.Label(config_frame, text="Configura\u00e7\u00f5es gerais").pack(padx=10, pady=10)
        notebook.add(config_frame, text="Configura\u00e7\u00f5es")

        dq_frame = ttk.Frame(notebook)
        ttk.Label(dq_frame, text="M\u00e9todo D\u00e9court-Quaresma (1996)").pack(padx=10, pady=10)
        notebook.add(dq_frame, text="D\u00e9court-Quaresma (1996)")

