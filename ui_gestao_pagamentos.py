"""Payment management tab."""
import tkinter as tk
from tkinter import ttk, messagebox
from styles import (C_WHITE, C_BG, C_BORDER, C_ACCENT, C_ACCENT2, C_TEXT,
                    C_MUTED, C_SIDEBAR, C_ROW_ODD, C_ROW_EVEN, C_SUCCESS, C_WARN,
                    FONT_BODY, FONT_H2, FONT_H3, FONT_SMALL, FONT_TITLE,
                    FONT_MONO, card_frame)

TIPO_LABEL = {
    'inicial':       'Honorários Iniciais',
    'condicionado':  'Honorários Condicionados',
    'intermediario': 'Honorários Intermediários',
    'exito':         'Honorários de Êxito',
}


class GestaoPagamentosTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.current_honorario_id = None
        self._search_after_id = None
        self._loading = False
        self._build()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        hdr = ttk.Frame(self, style='TFrame', padding=(24, 18, 24, 6))
        hdr.grid(row=0, column=0, sticky='ew')
        ttk.Label(hdr, text='Gestão de Pagamentos', style='Title.TLabel').pack(side='left')

        content = ttk.Frame(self, style='TFrame', padding=(24, 6, 24, 24))
        content.grid(row=1, column=0, sticky='nsew')
        content.columnconfigure(0, weight=1, minsize=320)
        content.columnconfigure(1, weight=3)
        content.rowconfigure(0, weight=1)

        self._build_selector(content)
        self._build_detail(content)

    def _build_selector(self, parent):
        panel = card_frame(parent, padding=16)
        panel.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(3, weight=1)

        ttk.Label(panel, text='Selecionar honorário', style='H2Card.TLabel').grid(
            row=0, column=0, sticky='w', pady=(0, 10))

        ttk.Label(panel, text='Buscar por cliente ou nº do contrato', style='MutedCard.TLabel').grid(
            row=1, column=0, sticky='w', pady=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self._on_search_changed)
        ttk.Entry(panel, textvariable=self.search_var).grid(
            row=2, column=0, sticky='ew', ipady=4, pady=(0, 8))

        tree_frame = ttk.Frame(panel, style='Card.TFrame')
        tree_frame.grid(row=3, column=0, sticky='nsew')
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=('info',),
                                 show='tree headings', selectmode='browse')
        self.tree.heading('#0', text='Contrato / Honorário', anchor='w')
        self.tree.heading('info', text='Detalhes', anchor='w')
        self.tree.column('#0', width=200, stretch=True)
        self.tree.column('info', width=180, stretch=True)
        self.tree.tag_configure('contrato', font=FONT_H3)
        self.tree.tag_configure('honorario', font=FONT_BODY)
        self.tree.tag_configure('odd', background=C_ROW_ODD)
        self.tree.tag_configure('even', background=C_ROW_EVEN)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)

        vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=vsb.set)

        self._refresh_tree()

    def _build_detail(self, parent):
        self.detail_panel = card_frame(parent, padding=20)
        self.detail_panel.grid(row=0, column=1, sticky='nsew')
        self.detail_panel.columnconfigure(0, weight=1)
        self.detail_panel.rowconfigure(2, weight=1)

        # Info area
        info = ttk.Frame(self.detail_panel, style='Card.TFrame')
        info.grid(row=0, column=0, sticky='ew', pady=(0, 16))
        info.columnconfigure(1, weight=1)

        self.lbl_cliente = ttk.Label(info, text='—', style='H2Card.TLabel')
        self.lbl_cliente.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 4))

        self.lbl_ctt = ttk.Label(info, text='', style='CTT.TLabel')
        self.lbl_ctt.grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 8))

        fields = [
            ('Tipo de honorários',   'lbl_tipo'),
            ('Hipótese de incidência','lbl_hipotese'),
            ('Valor integral',       'lbl_valor'),
        ]
        for i, (label, attr) in enumerate(fields):
            ttk.Label(info, text=label + ':', style='MutedCard.TLabel').grid(
                row=2 + i, column=0, sticky='w', padx=(0, 12), pady=2)
            lbl = ttk.Label(info, text='—', style='Card.TLabel')
            lbl.grid(row=2 + i, column=1, sticky='w', pady=2)
            setattr(self, attr, lbl)

        ttk.Separator(self.detail_panel, orient='horizontal').grid(
            row=1, column=0, sticky='ew', pady=(0, 12))

        # Parcelas table
        ttk.Label(self.detail_panel, text='Planilha de parcelas',
                  style='H2Card.TLabel').grid(row=2, column=0, sticky='nw', pady=(0, 8))

        table_outer = ttk.Frame(self.detail_panel, style='Card.TFrame')
        table_outer.grid(row=3, column=0, sticky='nsew')
        table_outer.columnconfigure(0, weight=1)
        table_outer.rowconfigure(1, weight=1)
        self.detail_panel.rowconfigure(3, weight=1)

        # Header
        hdr_cols = ['Parcela', 'Valor', 'Vencimento', 'Nota Fiscal', 'Data Pagamento', '']
        hdr_widths = [60, 120, 100, 100, 120, 30]
        hdr_bg = C_SIDEBAR
        hdr_row = tk.Frame(table_outer, bg=hdr_bg)
        hdr_row.grid(row=0, column=0, sticky='ew')
        for col, (text, w) in enumerate(zip(hdr_cols, hdr_widths)):
            tk.Label(hdr_row, text=text, bg=hdr_bg, fg=C_WHITE,
                     font=FONT_H3, anchor='w', padx=6, pady=6,
                     width=w // 7).grid(row=0, column=col, sticky='ew')
            hdr_row.columnconfigure(col, weight=1 if col in (1, 2, 3, 4) else 0)

        # Scrollable rows
        canvas = tk.Canvas(table_outer, bg=C_WHITE, highlightthickness=0, height=260)
        canvas.grid(row=1, column=0, sticky='nsew')
        vsb2 = ttk.Scrollbar(table_outer, orient='vertical', command=canvas.yview)
        vsb2.grid(row=1, column=1, sticky='ns')
        canvas.configure(yscrollcommand=vsb2.set)

        self.parcelas_frame = tk.Frame(canvas, bg=C_WHITE)
        win = canvas.create_window((0, 0), window=self.parcelas_frame, anchor='nw')

        def _on_cf(e):
            canvas.configure(scrollregion=canvas.bbox('all'))
        def _on_cr(e):
            canvas.itemconfig(win, width=e.width)

        self.parcelas_frame.bind('<Configure>', _on_cf)
        canvas.bind('<Configure>', _on_cr)

        self.parcelas_frame.columnconfigure(0, minsize=60)
        self.parcelas_frame.columnconfigure(1, weight=1)
        self.parcelas_frame.columnconfigure(2, weight=1)
        self.parcelas_frame.columnconfigure(3, weight=1)
        self.parcelas_frame.columnconfigure(4, weight=1)

        # Buttons
        btn_row = ttk.Frame(self.detail_panel, style='Card.TFrame')
        btn_row.grid(row=4, column=0, sticky='ew', pady=(10, 0))

        ttk.Button(btn_row, text='＋ Adicionar Parcela', style='Small.TButton',
                   command=self._add_parcela_row).pack(side='left', padx=(0, 8))
        ttk.Button(btn_row, text='Salvar Parcelas', command=self._save_parcelas).pack(side='left')

        self._parcela_rows = []  # list of dicts with StringVars

    # ── Tree (hierarchical) ────────────────────────────────────────────────────

    def _on_search_changed(self, *_args):
        """Debounce search: wait 300ms after last keystroke before refreshing."""
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(300, self._refresh_tree)

    def _refresh_tree(self):
        self._search_after_id = None
        self.tree.delete(*self.tree.get_children())

        q = self.search_var.get().strip()
        rows = self.db.search_contratos_com_honorarios(q)

        # Group by contract
        contratos = {}
        for r in rows:
            ctt_n = r['ctt_n']
            if ctt_n not in contratos:
                contratos[ctt_n] = {
                    'cliente_nome': r['cliente_nome'],
                    'contrato_id': r['contrato_id'],
                    'honorarios': [],
                }
            contratos[ctt_n]['honorarios'].append(r)

        idx = 0
        for ctt_n, data in contratos.items():
            # Contract node
            contrato_iid = f'c_{data["contrato_id"]}'
            self.tree.insert('', 'end', iid=contrato_iid,
                             text=f'  {ctt_n}  —  {data["cliente_nome"]}',
                             values=('',),
                             tags=('contrato',), open=False)

            for h in data['honorarios']:
                tipo_lbl = TIPO_LABEL.get(h['tipo'], h['tipo'])
                valor_str = f'R$ {h["valor"]}' if h['valor'] else ''
                hipotese_str = h['hipotese'] or ''
                detail = valor_str
                if hipotese_str:
                    detail = f'{valor_str}  •  {hipotese_str}' if valor_str else hipotese_str

                tag = 'odd' if idx % 2 == 0 else 'even'
                self.tree.insert(contrato_iid, 'end',
                                 iid=f'h_{h["honorario_id"]}',
                                 text=f'    {tipo_lbl}',
                                 values=(detail,),
                                 tags=('honorario', tag))
                idx += 1

    def _on_tree_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        if iid.startswith('h_'):
            hid = int(iid[2:])
            self.load_honorario(hid)
        elif iid.startswith('c_'):
            # Expand/collapse contract node on click
            if self.tree.item(iid, 'open'):
                self.tree.item(iid, open=False)
            else:
                self.tree.item(iid, open=True)

    # ── Load honorario ────────────────────────────────────────────────────────

    def load_honorario(self, honorario_id):
        self.current_honorario_id = honorario_id
        h = self.db.get_honorario(honorario_id)
        if not h:
            return
        cont = self.db.get_contrato(h['contrato_id'])
        if not cont:
            return

        self.lbl_cliente.config(text=cont['cliente_nome'])
        self.lbl_ctt.config(text=cont['ctt_n'])
        self.lbl_tipo.config(text=TIPO_LABEL.get(h['tipo'], h['tipo']))
        self.lbl_hipotese.config(text=h['hipotese'] or '—')
        self.lbl_valor.config(text=h['valor'] or '—')

        # Select in tree if visible
        try:
            self.tree.selection_set(f'h_{honorario_id}')
            self.tree.see(f'h_{honorario_id}')
        except Exception:
            pass

        self._load_parcelas(honorario_id)

    def _load_parcelas(self, honorario_id):
        # Clear existing rows
        for row_data in self._parcela_rows:
            row_data['frame'].destroy()
        self._parcela_rows.clear()

        parcelas = self.db.get_parcelas(honorario_id)
        for p in parcelas:
            self._add_parcela_row(
                num=str(p['num_parcela'] or ''),
                valor=p['valor'] or '',
                vencimento=p['vencimento'] or '',
                nota_fiscal=p['nota_fiscal'] or '',
                data_pagamento=p['data_pagamento'] or ''
            )

    # ── Parcela rows ──────────────────────────────────────────────────────────

    def _add_parcela_row(self, num='', valor='', vencimento='', nota_fiscal='', data_pagamento=''):
        idx = len(self._parcela_rows)
        if not num:
            num = str(idx + 1)
        bg = C_ROW_ODD if idx % 2 == 0 else C_ROW_EVEN

        row_f = tk.Frame(self.parcelas_frame, bg=bg)
        row_f.grid(row=idx, column=0, columnspan=6, sticky='ew')
        row_f.columnconfigure(0, minsize=60)
        row_f.columnconfigure(1, weight=1)
        row_f.columnconfigure(2, weight=1)
        row_f.columnconfigure(3, weight=1)
        row_f.columnconfigure(4, weight=1)

        vars_ = {}
        data = [
            ('num',           num,           0, False),
            ('valor',         valor,         1, True),
            ('vencimento',    vencimento,    2, True),
            ('nota_fiscal',   nota_fiscal,   3, True),
            ('data_pagamento',data_pagamento,4, True),
        ]
        for key, val, col, editable in data:
            v = tk.StringVar(value=val)
            vars_[key] = v
            state = 'normal' if editable else 'readonly'
            ent = tk.Entry(row_f, textvariable=v, bg=bg, fg=C_TEXT,
                           relief='flat', bd=0, font=FONT_BODY,
                           highlightthickness=1,
                           highlightbackground=C_BORDER,
                           highlightcolor=C_ACCENT,
                           state=state)
            ent.grid(row=0, column=col, sticky='ew', padx=(4, 2), pady=3, ipady=3)

        del_btn = ttk.Button(row_f, text='✕', style='Danger.TButton',
                             command=lambda rf=row_f: self._del_parcela_row(rf))
        del_btn.grid(row=0, column=5, padx=(2, 4), pady=2)

        row_data = {'frame': row_f, 'vars': vars_}
        self._parcela_rows.append(row_data)

    def _del_parcela_row(self, row_frame):
        for i, rd in enumerate(self._parcela_rows):
            if rd['frame'] is row_frame:
                row_frame.destroy()
                self._parcela_rows.pop(i)
                break
        self._renum_parcelas()

    def _renum_parcelas(self):
        for i, rd in enumerate(self._parcela_rows):
            bg = C_ROW_ODD if i % 2 == 0 else C_ROW_EVEN
            rd['frame'].configure(bg=bg)
            rd['frame'].grid(row=i, column=0, columnspan=6, sticky='ew')
            rd['vars']['num'].set(str(i + 1))
            for child in rd['frame'].winfo_children():
                if isinstance(child, tk.Entry):
                    child.configure(bg=bg)

    # ── Save ──────────────────────────────────────────────────────────────────

    def _save_parcelas(self):
        if not self.current_honorario_id:
            messagebox.showwarning('Atenção', 'Selecione um honorário antes de salvar.')
            return
        parcelas = []
        for rd in self._parcela_rows:
            v = rd['vars']
            parcelas.append({
                'num':           v['num'].get().strip(),
                'valor':         v['valor'].get().strip(),
                'vencimento':    v['vencimento'].get().strip(),
                'nota_fiscal':   v['nota_fiscal'].get().strip(),
                'data_pagamento': v['data_pagamento'].get().strip(),
            })
        self.db.save_parcelas(self.current_honorario_id, parcelas)
        messagebox.showinfo('Salvo', 'Parcelas salvas com sucesso.')
        self._refresh_tree()
