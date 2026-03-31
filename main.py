"""
Gestão de Contratos Advocatícios
Entry point — run with: python main.py
Requires Python 3.8+ (stdlib only, no pip installs needed)
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Ensure imports resolve relative to this file's directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from styles import apply_styles, C_BG, C_SIDEBAR, FONT_BODY
from ui_cadastro_cliente import CadastroClienteTab
from ui_cadastro_contrato import CadastroContratoTab
from ui_gestao_pagamentos import GestaoPagamentosTab
from ui_relatorio import RelatorioGestaoTab


class GestaoEscApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Gestão de Contratos Advocatícios')
        self.geometry('1280x820')
        self.minsize(900, 600)
        self.configure(bg=C_BG)

        # High-DPI support on Windows
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        apply_styles(self)

        # Ensure contracts PDF directory exists
        contratos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contratos')
        os.makedirs(contratos_dir, exist_ok=True)

        self.db = Database()
        self._build()

        self.protocol('WM_DELETE_WINDOW', self._on_close)

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky='nsew')

        self.tab_cliente   = CadastroClienteTab(self.notebook, self.db)
        self.tab_contrato  = CadastroContratoTab(self.notebook, self.db, self)
        self.tab_pagamentos = GestaoPagamentosTab(self.notebook, self.db)
        self.tab_relatorio  = RelatorioGestaoTab(self.notebook, self.db, self)

        self.notebook.add(self.tab_cliente,    text='  Cadastro de Cliente  ')
        self.notebook.add(self.tab_contrato,   text='  Cadastro de Contrato  ')
        self.notebook.add(self.tab_pagamentos, text='  Gestão de Pagamentos  ')
        self.notebook.add(self.tab_relatorio,  text='  Relatório de Gestão  ')

    def _on_close(self):
        self.db.close()
        self.destroy()


if __name__ == '__main__':
    app = GestaoEscApp()
    app.mainloop()
