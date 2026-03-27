"""Management report tab."""
import tkinter as tk
from tkinter import ttk, messagebox
from styles import (C_WHITE, C_BG, C_BORDER, C_ACCENT, C_ACCENT2, C_TEXT,
                    C_MUTED, C_SIDEBAR, C_ROW_ODD, C_ROW_EVEN, C_SUCCESS, C_WARN,
                    FONT_BODY, FONT_H2, FONT_H3, FONT_SMALL, FONT_TITLE, card_frame)

TIPO_LABEL = {
    'inicial':       'Honorários Iniciais',
    'condicionado':  'Honorários Condicionados',
    'intermediario': 'Honorários Intermediários',
    'exito':         'Honorários de Êxito',
}
TIPO_ORDER = ['inicial', 'condicionado', 'intermediario', 'exito']


class RelatorioGestaoTab(ttk.Frame):
    def __init__(self, parent, db, app):
        super().__init__(parent)
        self.db  = db
        self.app = app
        self._build()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        hdr = ttk.Frame(self, style='TFrame', padding=(24, 18, 24, 6))
        hdr.grid(row=0, column=0, sticky='ew')
        ttk.Label(hdr, text='Relatório de Gestão', style='Title.TLabel').pack(side='left')

        content = ttk.Frame(self, style='TFrame', padding=(24, 6, 24, 24))
        content.grid(row=1, column=0, sticky='nsew')
        content.columnconfigure(0, weight=1, minsize=260)
        content.columnconfigure(1, weight=3)
        content.rowconfigure(0, weight=1)

        self._build_search_panel(content)
        self._build_report_panel(content)

    # ── Left: search + contract list ──────────────────────────────────────────

    def _build_search_panel(self, parent):
        panel = card_frame(parent, padding=16)
        panel.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(5, weight=1)

        ttk.Label(panel, text='Busca', style='H2Card.TLabel').grid(
            row=0, column=0, sticky='w', pady=(0, 10))

        ttk.Label(panel, text='Por cliente', style='MutedCard.TLabel').grid(
            row=1, column=0, sticky='w', pady=(0, 4))
        self.cliente_var = tk.StringVar()
        self.cliente_var.trace_add('write', lambda *_: self._refresh_list())
        ttk.Entry(panel, textvariable=self.cliente_var).grid(
            row=2, column=0, sticky='ew', ipady=4, pady=(0, 10))

        ttk.Label(panel, text='Por número de contrato', style='MutedCard.TLabel').grid(
            row=3, column=0, sticky='w', pady=(0, 4))
        self.num_var = tk.StringVar()
        self.num_var.trace_add('write', lambda *_: self._refresh_list())
        ttk.Entry(panel, textvariable=self.num_var).grid(
            row=4, column=0, sticky='ew', ipady=4, pady=(0, 10))

        tree_frame = ttk.Frame(panel, style='Card.TFrame')
        tree_frame.grid(row=5, column=0, sticky='nsew')
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=('ctt_n', 'cliente'),
                                 show='headings', selectmode='browse')
        self.tree.heading('ctt_n',   text='CTT-N')
        self.tree.heading('cliente', text='Cliente')
        self.tree.column('ctt_n',   width=100, stretch=False)
        self.tree.column('cliente', stretch=True)
        self.tree.tag_configure('odd',  background=C_ROW_ODD)
        self.tree.tag_configure('even', background=C_ROW_EVEN)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

        vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=vsb.set)

        self._refresh_list()

    # ── Right: report detail ──────────────────────────────────────────────────

    def _build_report_panel(self, parent):
        # Outer scrollable area
        outer = ttk.Frame(parent, style='TFrame')
        outer.grid(row=0, column=1, sticky='nsew')
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        canvas = tk.Canvas(outer, bg=C_BG, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky='nsew')
        vsb = ttk.Scrollbar(outer, orient='vertical', command=canvas.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        canvas.configure(yscrollcommand=vsb.set)

        self.report_body = tk.Frame(canvas, bg=C_BG)
        win = canvas.create_window((0, 0), window=self.report_body, anchor='nw')

        def _on_cf(e):
            canvas.configure(scrollregion=canvas.bbox('all'))
        def _on_cr(e):
            canvas.itemconfig(win, width=e.width)

        self.report_body.bind('<Configure>', _on_cf)
        canvas.bind('<Configure>', _on_cr)
        canvas.bind_all('<MouseWheel>',
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), 'units'))

        self.report_body.columnconfigure(0, weight=1)
        self._show_placeholder()

    def _show_placeholder(self):
        for w in self.report_body.winfo_children():
            w.destroy()
        tk.Label(self.report_body, text='Selecione um contrato para ver o relatório.',
                 bg=C_BG, fg=C_MUTED, font=FONT_BODY).grid(
            row=0, column=0, padx=20, pady=40)

    # ── Refresh list ──────────────────────────────────────────────────────────

    def _refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        cn = self.cliente_var.get().strip()
        nn = self.num_var.get().strip()

        if nn:
            rows = self.db.search_contrato_by_numero(nn)
        elif cn:
            rows = self.db.search_contratos_by_cliente_nome(cn)
        else:
            rows = self.db.search_contratos_by_cliente_nome('')

        for i, r in enumerate(rows):
            tag = 'odd' if i % 2 else 'even'
            self.tree.insert('', 'end', iid=str(r['id']),
                             values=(r['ctt_n'], r['cliente_nome']), tags=(tag,))

    def refresh(self):
        self._refresh_list()

    # ── Select ────────────────────────────────────────────────────────────────

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        cid = int(sel[0])
        self._render_report(cid)

    def open_contrato(self, contrato_id):
        try:
            self.tree.selection_set(str(contrato_id))
        except Exception:
            pass
        self._render_report(contrato_id)

    # ── Render ────────────────────────────────────────────────────────────────

    def _render_report(self, contrato_id):
        for w in self.report_body.winfo_children():
            w.destroy()

        cont = self.db.get_contrato(contrato_id)
        if not cont:
            self._show_placeholder()
            return

        body = self.report_body
        body.columnconfigure(0, weight=1)
        row = 0

        # ── Header card ───────────────────────────────────────────────────────
        hcard = tk.Frame(body, bg=C_WHITE, bd=0,
                         highlightthickness=1, highlightbackground=C_BORDER)
        hcard.grid(row=row, column=0, sticky='ew', padx=0, pady=(0, 12))
        hcard.columnconfigure(1, weight=1)
        row += 1

        tk.Label(hcard, text=cont['cliente_nome'], bg=C_WHITE, fg=C_TEXT,
                 font=FONT_H2, anchor='w', padx=16, pady=(12, 2)).grid(
            row=0, column=0, columnspan=2, sticky='w')

        tk.Label(hcard, text=cont['ctt_n'], bg=C_WHITE, fg=C_ACCENT2,
                 font=('Segoe UI', 12, 'bold'), anchor='w', padx=16).grid(
            row=1, column=0, sticky='w')

        tk.Label(hcard, text=cont['tipo'] or '—', bg=C_WHITE, fg=C_ACCENT,
                 font=FONT_H3, anchor='w', padx=8).grid(row=1, column=1, sticky='w')

        fields = [
            ('Descrição',          cont['descricao']  or '—'),
            ('Advogado responsável', cont['advogado']  or '—'),
            ('Observações',        cont['observacoes'] or '—'),
        ]
        for i, (label, value) in enumerate(fields):
            tk.Label(hcard, text=label + ':', bg=C_WHITE, fg=C_MUTED,
                     font=FONT_SMALL, anchor='w', padx=16, pady=2).grid(
                row=2 + i, column=0, sticky='nw')
            tk.Label(hcard, text=value, bg=C_WHITE, fg=C_TEXT,
                     font=FONT_BODY, anchor='w', wraplength=500, justify='left').grid(
                row=2 + i, column=1, sticky='w', padx=(4, 16), pady=2)

        # Spacer
        tk.Frame(hcard, bg=C_WHITE, height=10).grid(
            row=2 + len(fields), column=0, columnspan=2)

        # ── Honorários summary ────────────────────────────────────────────────
        tk.Label(body, text='Resumo dos Honorários', bg=C_BG, fg=C_TEXT,
                 font=FONT_H2, anchor='w').grid(
            row=row, column=0, sticky='w', pady=(0, 8))
        row += 1

        honorarios = self.db.get_honorarios_by_contrato(contrato_id)

        # Group by tipo preserving TIPO_ORDER
        grouped = {t: [] for t in TIPO_ORDER}
        for h in honorarios:
            if h['tipo'] in grouped:
                grouped[h['tipo']].append(h)

        for tipo in TIPO_ORDER:
            hs = grouped[tipo]
            if not hs:
                continue

            # Section header
            sh = tk.Frame(body, bg=C_SIDEBAR)
            sh.grid(row=row, column=0, sticky='ew', pady=(0, 0))
            sh.columnconfigure(0, weight=1)
            row += 1

            tk.Label(sh, text=TIPO_LABEL[tipo], bg=C_SIDEBAR, fg=C_WHITE,
                     font=FONT_H3, anchor='w', padx=12, pady=6).grid(
                row=0, column=0, sticky='w')

            # Table card
            tcard = tk.Frame(body, bg=C_WHITE, bd=0,
                             highlightthickness=1, highlightbackground=C_BORDER)
            tcard.grid(row=row, column=0, sticky='ew', pady=(0, 16))
            tcard.columnconfigure(0, weight=2)
            tcard.columnconfigure(1, weight=1)
            tcard.columnconfigure(2, minsize=80)
            tcard.columnconfigure(3, minsize=110)
            tcard.columnconfigure(4, minsize=110)
            row += 1

            # Column headers
            col_headers = ['Hipótese de incidência', 'Valor integral', 'Gerir', 'Parcelamento', 'Quitação']
            for ci, ch in enumerate(col_headers):
                tk.Label(tcard, text=ch, bg='#EFF3FB', fg=C_SIDEBAR,
                         font=FONT_H3, anchor='w', padx=8, pady=5).grid(
                    row=0, column=ci, sticky='ew')

            # Data rows
            for ri, h in enumerate(hs):
                bg = C_ROW_ODD if ri % 2 == 0 else C_WHITE
                parcelas = self.db.get_parcelas(h['id'])

                # Parcelamento
                parc_text = self._parcelamento_summary(parcelas, h['valor'])

                # Quitação
                quit_status, quit_color = self._quitacao_status(parcelas)

                cells = [
                    h['hipotese'] or '—',
                    h['valor'] or '—',
                    None,          # button
                    parc_text,
                    quit_status,
                ]
                cell_colors = [C_TEXT, C_TEXT, None, C_MUTED, quit_color]

                for ci, (cell, color) in enumerate(zip(cells, cell_colors)):
                    if ci == 2:
                        # Gerir button
                        btn_f = tk.Frame(tcard, bg=bg)
                        btn_f.grid(row=ri + 1, column=ci, sticky='ew', padx=4, pady=2)
                        hid = h['id']
                        ttk.Button(btn_f, text='Gerir', style='Link.TButton',
                                   command=lambda hid=hid: self._open_pagamentos(hid)).pack()
                    else:
                        tk.Label(tcard, text=cell, bg=bg, fg=color,
                                 font=FONT_BODY, anchor='w', padx=8, pady=5,
                                 wraplength=200, justify='left').grid(
                            row=ri + 1, column=ci, sticky='ew')

        if not any(grouped.values()):
            tk.Label(body, text='Nenhum honorário cadastrado para este contrato.',
                     bg=C_BG, fg=C_MUTED, font=FONT_BODY).grid(
                row=row, column=0, sticky='w', pady=8)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _parcelamento_summary(self, parcelas, valor_total):
        if not parcelas:
            return 'Não definido'
        if len(parcelas) == 1:
            return 'À vista'
        return f'{len(parcelas)} parcelas'

    def _quitacao_status(self, parcelas):
        if not parcelas:
            return '—', C_MUTED
        total = len(parcelas)
        pagas = sum(1 for p in parcelas if p['data_pagamento'] and p['data_pagamento'].strip())
        if pagas == 0:
            return 'Pendente', C_WARN
        if pagas < total:
            return f'{pagas}/{total} pagas', C_WARN
        return 'Quitado', C_SUCCESS

    def _open_pagamentos(self, honorario_id):
        self.app.notebook.select(2)
        self.app.tab_pagamentos.load_honorario(honorario_id)
