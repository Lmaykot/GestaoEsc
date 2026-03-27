"""Dialog for entering / editing fee tables (honorários) for a contract."""
import tkinter as tk
from tkinter import ttk, messagebox
from styles import (C_WHITE, C_BG, C_BORDER, C_ACCENT, C_ACCENT2, C_TEXT,
                    C_MUTED, C_SIDEBAR, FONT_BODY, FONT_H2, FONT_H3, FONT_SMALL,
                    card_frame)

TIPOS = [
    ('inicial',      'Honorários Iniciais',       'Momento de incidência'),
    ('condicionado', 'Honorários Condicionados',   'Hipótese de incidência'),
    ('intermediario','Honorários Intermediários',  'Hipótese de incidência'),
    ('exito',        'Honorários de Êxito',        'Hipótese de incidência'),
]


class HonorariosDialog(tk.Toplevel):
    def __init__(self, parent, db, contrato_id, ctt_n, cliente_nome, on_save=None):
        super().__init__(parent)
        self.db           = db
        self.contrato_id  = contrato_id
        self.on_save_cb   = on_save
        self.title(f'Honorários — {ctt_n}  |  {cliente_nome}')
        self.geometry('840x680')
        self.minsize(700, 500)
        self.configure(bg=C_BG)
        self.grab_set()
        self.resizable(True, True)

        # section_rows[tipo] = list of (hipotese_var, valor_var, row_frame)
        self.section_rows: dict[str, list] = {t[0]: [] for t in TIPOS}

        self._build()
        self._load_existing()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header
        hdr = tk.Frame(self, bg=C_SIDEBAR, padx=20, pady=12)
        hdr.grid(row=0, column=0, sticky='ew')
        tk.Label(hdr, text='Cadastro de Honorários', bg=C_SIDEBAR, fg=C_WHITE,
                 font=FONT_H2).pack(side='left')

        # Scrollable body
        canvas = tk.Canvas(self, bg=C_BG, highlightthickness=0)
        canvas.grid(row=1, column=0, sticky='nsew')
        vsb = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        vsb.grid(row=1, column=1, sticky='ns')
        canvas.configure(yscrollcommand=vsb.set)

        self.body = tk.Frame(canvas, bg=C_BG)
        body_win = canvas.create_window((0, 0), window=self.body, anchor='nw')

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox('all'))
        def _on_canvas_resize(e):
            canvas.itemconfig(body_win, width=e.width)

        self.body.bind('<Configure>', _on_configure)
        canvas.bind('<Configure>', _on_canvas_resize)
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), 'units'))

        self.body.columnconfigure(0, weight=1)

        for row_idx, (tipo, titulo, col_label) in enumerate(TIPOS):
            self._build_section(self.body, row_idx * 2, tipo, titulo, col_label)
            # Spacer
            tk.Frame(self.body, bg=C_BG, height=16).grid(
                row=row_idx * 2 + 1, column=0, sticky='ew')

        # Footer buttons
        footer = tk.Frame(self, bg=C_BG, padx=20, pady=12)
        footer.grid(row=2, column=0, sticky='ew')
        ttk.Button(footer, text='Cancelar', style='Secondary.TButton',
                   command=self.destroy).pack(side='right', padx=(8, 0))
        ttk.Button(footer, text='Salvar Honorários', command=self._save).pack(side='right')

    def _build_section(self, parent, row_idx, tipo, titulo, col_label):
        outer = tk.Frame(parent, bg=C_BG, padx=20, pady=0)
        outer.grid(row=row_idx, column=0, sticky='ew')
        outer.columnconfigure(0, weight=1)

        # Section title
        tk.Label(outer, text=titulo, bg=C_BG, fg=C_ACCENT2,
                 font=FONT_H3).grid(row=0, column=0, sticky='w', pady=(0, 6))

        card = tk.Frame(outer, bg=C_WHITE, bd=1, relief='flat',
                        highlightthickness=1, highlightbackground=C_BORDER)
        card.grid(row=1, column=0, sticky='ew')
        card.columnconfigure(0, weight=3)
        card.columnconfigure(1, weight=1)

        # Table header
        hdr_bg = C_SIDEBAR
        tk.Label(card, text=col_label, bg=hdr_bg, fg=C_WHITE,
                 font=FONT_H3, anchor='w', padx=8, pady=6).grid(
            row=0, column=0, sticky='ew')
        tk.Label(card, text='Valor', bg=hdr_bg, fg=C_WHITE,
                 font=FONT_H3, anchor='w', padx=8, pady=6).grid(
            row=0, column=1, sticky='ew')
        tk.Label(card, text='', bg=hdr_bg, fg=C_WHITE, width=3).grid(
            row=0, column=2)

        # Rows container
        rows_frame = tk.Frame(card, bg=C_WHITE)
        rows_frame.grid(row=1, column=0, columnspan=3, sticky='ew')
        rows_frame.columnconfigure(0, weight=3)
        rows_frame.columnconfigure(1, weight=1)

        setattr(self, f'rows_frame_{tipo}', rows_frame)

        # Add button
        add_btn = ttk.Button(card, text='＋', style='Add.TButton',
                             command=lambda t=tipo: self._add_row(t))
        add_btn.grid(row=2, column=0, columnspan=3, sticky='ew', padx=6, pady=6)

        # Start with 2 blank rows
        self._add_row(tipo)
        self._add_row(tipo)

    # ── Row management ────────────────────────────────────────────────────────

    def _add_row(self, tipo, hipotese='', valor=''):
        parent = getattr(self, f'rows_frame_{tipo}')
        idx = len(self.section_rows[tipo])
        bg = '#F8FAFC' if idx % 2 == 0 else C_WHITE

        row_f = tk.Frame(parent, bg=bg)
        row_f.grid(row=idx, column=0, columnspan=3, sticky='ew')
        row_f.columnconfigure(0, weight=3)
        row_f.columnconfigure(1, weight=1)

        h_var = tk.StringVar(value=hipotese)
        v_var = tk.StringVar(value=valor)

        h_ent = tk.Entry(row_f, textvariable=h_var, bg=bg, fg=C_TEXT,
                         relief='flat', bd=0, font=FONT_BODY,
                         highlightthickness=1,
                         highlightbackground=C_BORDER,
                         highlightcolor=C_ACCENT)
        h_ent.grid(row=0, column=0, sticky='ew', padx=(6, 2), pady=4, ipady=4)

        v_ent = tk.Entry(row_f, textvariable=v_var, bg=bg, fg=C_TEXT,
                         relief='flat', bd=0, font=FONT_BODY,
                         highlightthickness=1,
                         highlightbackground=C_BORDER,
                         highlightcolor=C_ACCENT)
        v_ent.grid(row=0, column=1, sticky='ew', padx=(2, 2), pady=4, ipady=4)

        del_btn = ttk.Button(row_f, text='✕', style='Danger.TButton',
                             command=lambda r=row_f, t=tipo: self._del_row(r, t))
        del_btn.grid(row=0, column=2, padx=(2, 6), pady=2)

        self.section_rows[tipo].append((h_var, v_var, row_f))

    def _del_row(self, row_frame, tipo):
        for i, (hv, vv, rf) in enumerate(self.section_rows[tipo]):
            if rf is row_frame:
                rf.destroy()
                self.section_rows[tipo].pop(i)
                break
        # Re-color remaining rows
        parent = getattr(self, f'rows_frame_{tipo}')
        for j, (hv, vv, rf) in enumerate(self.section_rows[tipo]):
            bg = '#F8FAFC' if j % 2 == 0 else C_WHITE
            rf.configure(bg=bg)
            rf.grid(row=j, column=0, columnspan=3, sticky='ew')
            for child in rf.winfo_children():
                if isinstance(child, tk.Entry):
                    child.configure(bg=bg)

    # ── Load existing ─────────────────────────────────────────────────────────

    def _load_existing(self):
        rows = self.db.get_honorarios_by_contrato(self.contrato_id)
        if not rows:
            return
        # Clear default blank rows first
        for tipo in self.section_rows:
            for _, _, rf in self.section_rows[tipo]:
                rf.destroy()
            self.section_rows[tipo].clear()

        for r in rows:
            self._add_row(r['tipo'], r['hipotese'] or '', r['valor'] or '')

        # Ensure at least 2 rows per section
        for tipo in self.section_rows:
            while len(self.section_rows[tipo]) < 2:
                self._add_row(tipo)

    # ── Save ──────────────────────────────────────────────────────────────────

    def _save(self):
        all_rows = []
        for tipo, _, _ in TIPOS:
            for ordem, (hv, vv, _) in enumerate(self.section_rows[tipo]):
                hipotese = hv.get().strip()
                valor    = vv.get().strip()
                if hipotese or valor:
                    all_rows.append((tipo, hipotese, valor, ordem))

        self.db.replace_honorarios(self.contrato_id, all_rows)

        if self.on_save_cb:
            self.on_save_cb()

        messagebox.showinfo('Salvo', 'Honorários salvos com sucesso.')
        self.destroy()
