import tkinter as tk
from tkinter import ttk, messagebox
from styles import (C_WHITE, C_BG, C_BORDER, C_ACCENT, C_TEXT, C_MUTED,
                    C_ROW_ODD, C_ROW_EVEN, FONT_BODY, FONT_H2, FONT_H3,
                    FONT_SMALL, FONT_TITLE, card_frame)
from ui_honorarios_dialog import HonorariosDialog

TIPO_CONTRATO = ['Contencioso', 'Consultoria', 'Licenciamento', 'Misto']


class CadastroContratoTab(ttk.Frame):
    def __init__(self, parent, db, app):
        super().__init__(parent)
        self.db  = db
        self.app = app
        self.current_cliente_id = None
        self.current_contrato_id = None
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        hdr = ttk.Frame(self, style='TFrame', padding=(24, 18, 24, 6))
        hdr.grid(row=0, column=0, sticky='ew')
        ttk.Label(hdr, text='Cadastro de Contrato', style='Title.TLabel').pack(side='left')

        content = ttk.Frame(self, style='TFrame', padding=(24, 6, 24, 24))
        content.grid(row=1, column=0, sticky='nsew')
        content.columnconfigure(0, weight=1, minsize=260)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        self._build_list_panel(content)
        self._build_form_panel(content)

    def _build_list_panel(self, parent):
        panel = card_frame(parent, padding=16)
        panel.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        ttk.Label(panel, text='Buscar contrato', style='H2Card.TLabel').grid(
            row=0, column=0, sticky='w', pady=(0, 8))

        search_row = ttk.Frame(panel, style='Card.TFrame')
        search_row.grid(row=1, column=0, sticky='ew', pady=(0, 8))
        search_row.columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *_: self._refresh_list())
        ttk.Entry(search_row, textvariable=self.search_var).grid(
            row=0, column=0, sticky='ew', ipady=4)

        tree_frame = ttk.Frame(panel, style='Card.TFrame')
        tree_frame.grid(row=2, column=0, sticky='nsew')
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=('ctt_n', 'cliente'),
                                 show='headings', selectmode='browse')
        self.tree.heading('ctt_n',    text='CTT-N')
        self.tree.heading('cliente',  text='Cliente')
        self.tree.column('ctt_n',   width=100, stretch=False)
        self.tree.column('cliente', stretch=True)
        self.tree.tag_configure('odd',  background=C_ROW_ODD)
        self.tree.tag_configure('even', background=C_ROW_EVEN)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

        vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=vsb.set)

        ttk.Button(panel, text='+ Novo Contrato', command=self._clear_form).grid(
            row=3, column=0, sticky='ew', pady=(8, 0))

        self._refresh_list()

    def _build_form_panel(self, parent):
        panel = card_frame(parent, padding=20)
        panel.grid(row=0, column=1, sticky='nsew')
        panel.columnconfigure(1, weight=1)

        self.form_title = ttk.Label(panel, text='Novo Contrato', style='H2Card.TLabel')
        self.form_title.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 16))

        # ── Cliente search inside form ─────────────────────────────────────
        ttk.Label(panel, text='Buscar cliente *', style='MutedCard.TLabel').grid(
            row=1, column=0, sticky='w', padx=(0, 12), pady=3)

        cs_frame = ttk.Frame(panel, style='Card.TFrame')
        cs_frame.grid(row=1, column=1, columnspan=2, sticky='ew', pady=3)
        cs_frame.columnconfigure(0, weight=1)
        self._cs_frame = cs_frame

        self.cliente_search_var = tk.StringVar()
        self.cliente_search_var.trace_add('write', lambda *_: self._update_cliente_dropdown())
        cs_entry = ttk.Entry(cs_frame, textvariable=self.cliente_search_var)
        cs_entry.grid(row=0, column=0, sticky='ew', ipady=4)
        cs_entry.bind('<FocusIn>',  lambda e: self._show_dropdown())
        cs_entry.bind('<FocusOut>', lambda e: self.after(150, self._hide_dropdown))

        # Dropdown list (placed relative to cs_frame)
        self.dropdown_frame = tk.Frame(panel, bg=C_WHITE, bd=1, relief='solid')
        self.dropdown_lb = tk.Listbox(self.dropdown_frame, font=FONT_BODY,
                                      bg=C_WHITE, fg=C_TEXT, selectbackground=C_ACCENT,
                                      height=5, bd=0, relief='flat')
        self.dropdown_lb.pack(fill='both', expand=True)
        self.dropdown_lb.bind('<<ListboxSelect>>', self._on_cliente_pick)
        self.dropdown_visible = False
        self._cliente_results = []

        # Selected client label
        self.cliente_lbl = ttk.Label(panel, text='', style='Accent.TLabel')
        self.cliente_lbl.grid(row=2, column=1, columnspan=2, sticky='w', pady=(0, 8))

        # CTT-N
        ttk.Label(panel, text='CTT-N', style='MutedCard.TLabel').grid(
            row=3, column=0, sticky='w', padx=(0, 12), pady=3)
        self.ctt_n_var = tk.StringVar()
        ctt_entry = ttk.Entry(panel, textvariable=self.ctt_n_var, state='readonly')
        ctt_entry.grid(row=3, column=1, sticky='w', ipady=4, pady=3)
        ttk.Button(panel, text='Gerar', style='Small.TButton',
                   command=self._generate_ctt).grid(row=3, column=2, padx=(6, 0), pady=3)

        # Descrição
        ttk.Label(panel, text='Descrição do contrato', style='MutedCard.TLabel').grid(
            row=4, column=0, sticky='nw', padx=(0, 12), pady=(8, 3))
        desc_f = ttk.Frame(panel, style='Card.TFrame')
        desc_f.grid(row=4, column=1, columnspan=2, sticky='ew', pady=(8, 3))
        desc_f.columnconfigure(0, weight=1)
        self.desc_text = tk.Text(desc_f, height=5, wrap='word', font=FONT_BODY,
                                 bg=C_WHITE, fg=C_TEXT, relief='flat', bd=1,
                                 highlightthickness=1, highlightcolor=C_ACCENT,
                                 highlightbackground=C_BORDER)
        self.desc_text.grid(row=0, column=0, sticky='ew')
        desc_vsb = ttk.Scrollbar(desc_f, orient='vertical', command=self.desc_text.yview)
        desc_vsb.grid(row=0, column=1, sticky='ns')
        self.desc_text.configure(yscrollcommand=desc_vsb.set)

        # Tipo de contrato
        ttk.Label(panel, text='Tipo de contrato', style='MutedCard.TLabel').grid(
            row=5, column=0, sticky='w', padx=(0, 12), pady=3)
        self.tipo_var = tk.StringVar()
        tipo_cb = ttk.Combobox(panel, textvariable=self.tipo_var,
                               values=TIPO_CONTRATO, state='readonly', width=20)
        tipo_cb.grid(row=5, column=1, sticky='w', pady=3)

        # Advogado
        ttk.Label(panel, text='Advogado responsável', style='MutedCard.TLabel').grid(
            row=6, column=0, sticky='w', padx=(0, 12), pady=3)
        self.advogado_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.advogado_var).grid(
            row=6, column=1, columnspan=2, sticky='ew', ipady=4, pady=3)

        # Observações adicionais
        ttk.Label(panel, text='Observações adicionais', style='MutedCard.TLabel').grid(
            row=7, column=0, sticky='nw', padx=(0, 12), pady=(8, 3))
        obs_f = ttk.Frame(panel, style='Card.TFrame')
        obs_f.grid(row=7, column=1, columnspan=2, sticky='ew', pady=(8, 3))
        obs_f.columnconfigure(0, weight=1)
        self.obs_text = tk.Text(obs_f, height=3, wrap='word', font=FONT_BODY,
                                bg=C_WHITE, fg=C_TEXT, relief='flat', bd=1,
                                highlightthickness=1, highlightcolor=C_ACCENT,
                                highlightbackground=C_BORDER)
        self.obs_text.grid(row=0, column=0, sticky='ew')
        obs_vsb = ttk.Scrollbar(obs_f, orient='vertical', command=self.obs_text.yview)
        obs_vsb.grid(row=0, column=1, sticky='ns')
        self.obs_text.configure(yscrollcommand=obs_vsb.set)

        # Buttons
        btn_row = ttk.Frame(panel, style='Card.TFrame')
        btn_row.grid(row=8, column=0, columnspan=3, sticky='e', pady=(16, 0))

        ttk.Button(btn_row, text='Cancelar', style='Secondary.TButton',
                   command=self._clear_form).pack(side='left', padx=(0, 8))
        ttk.Button(btn_row, text='Salvar', style='Secondary.TButton',
                   command=self._save_only).pack(side='left', padx=(0, 8))
        ttk.Button(btn_row, text='Salvar e Avançar →', command=self._save_and_advance).pack(side='left')

        self.status_lbl = ttk.Label(panel, text='', style='MutedCard.TLabel')
        self.status_lbl.grid(row=9, column=0, columnspan=3, sticky='w', pady=(8, 0))

    # ── Client dropdown ───────────────────────────────────────────────────────

    def _update_cliente_dropdown(self):
        q = self.cliente_search_var.get().strip()
        if not q:
            self._hide_dropdown()
            return
        clientes = self.db.search_clientes(q)
        self.dropdown_lb.delete(0, 'end')
        for c in clientes:
            self.dropdown_lb.insert('end', c['nome'])
        self._cliente_results = clientes
        if clientes:
            self._show_dropdown()
        else:
            self._hide_dropdown()

    def _show_dropdown(self):
        q = self.cliente_search_var.get().strip()
        if not q:
            return
        self.dropdown_frame.place(in_=self._cs_frame, x=0, rely=1.0,
                                  relwidth=1.0, anchor='nw')
        self.dropdown_frame.lift()
        self.dropdown_visible = True

    def _hide_dropdown(self):
        self.dropdown_frame.place_forget()
        self.dropdown_visible = False

    def _on_cliente_pick(self, _event=None):
        sel = self.dropdown_lb.curselection()
        if not sel:
            return
        idx = sel[0]
        c = self._cliente_results[idx]
        self.current_cliente_id = c['id']
        self.cliente_search_var.set(c['nome'])
        self.cliente_lbl.config(text=f"✓ {c['nome']}")
        self._hide_dropdown()

    # ── List ──────────────────────────────────────────────────────────────────

    def _refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        q = self.search_var.get().strip()
        if q:
            rows = self.db.search_contratos_by_cliente_nome(q)
        else:
            rows = self.db.search_contratos_by_cliente_nome('')
        for i, r in enumerate(rows):
            tag = 'odd' if i % 2 else 'even'
            self.tree.insert('', 'end', iid=str(r['id']),
                             values=(r['ctt_n'], r['cliente_nome']), tags=(tag,))

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        cid = int(sel[0])
        c = self.db.get_contrato(cid)
        if not c:
            return
        self.current_contrato_id = cid
        self.current_cliente_id  = c['cliente_id']
        self.form_title.config(text='Editar Contrato')
        self.cliente_search_var.set(c['cliente_nome'])
        self.cliente_lbl.config(text=f"✓ {c['cliente_nome']}")
        self.ctt_n_var.set(c['ctt_n'])
        self.tipo_var.set(c['tipo'] or '')
        self.advogado_var.set(c['advogado'] or '')
        self.desc_text.delete('1.0', 'end')
        self.desc_text.insert('1.0', c['descricao'] or '')
        self.obs_text.delete('1.0', 'end')
        self.obs_text.insert('1.0', c['observacoes'] or '')
        self.status_lbl.config(text='')

    def _clear_form(self):
        self.current_contrato_id = None
        self.current_cliente_id  = None
        self.form_title.config(text='Novo Contrato')
        self.cliente_search_var.set('')
        self.cliente_lbl.config(text='')
        self.ctt_n_var.set('')
        self.tipo_var.set('')
        self.advogado_var.set('')
        self.desc_text.delete('1.0', 'end')
        self.obs_text.delete('1.0', 'end')
        self.status_lbl.config(text='')
        self.tree.selection_remove(self.tree.selection())

    def _generate_ctt(self):
        if not self.current_contrato_id:
            self.ctt_n_var.set(self.db.get_next_ctt_n())

    # ── Save ──────────────────────────────────────────────────────────────────

    def _collect_data(self):
        if not self.current_cliente_id:
            messagebox.showwarning('Atenção', 'Selecione um cliente antes de salvar.')
            return None
        ctt_n = self.ctt_n_var.get().strip()
        if not ctt_n:
            messagebox.showwarning('Atenção', 'Gere ou informe o número do contrato (CTT-N).')
            return None
        return {
            'cliente_id': self.current_cliente_id,
            'ctt_n':      ctt_n,
            'descricao':  self.desc_text.get('1.0', 'end').strip(),
            'tipo':       self.tipo_var.get().strip(),
            'advogado':   self.advogado_var.get().strip(),
            'obs':        self.obs_text.get('1.0', 'end').strip(),
        }

    def _save_only(self):
        data = self._collect_data()
        if not data:
            return
        self._persist(data)
        self.status_lbl.config(text='Contrato salvo.', foreground=C_ACCENT)

    def _save_and_advance(self):
        data = self._collect_data()
        if not data:
            return
        cid = self._persist(data)
        c = self.db.get_contrato(cid)
        HonorariosDialog(
            self, self.db, cid,
            c['ctt_n'], c['cliente_nome'],
            on_save=lambda: self.app.tab_relatorio.refresh() if hasattr(self.app, 'tab_relatorio') else None
        )

    def _persist(self, data):
        if self.current_contrato_id:
            # Can't update ctt_n easily – just update other fields via raw SQL
            self.db.conn.execute(
                'UPDATE contratos SET descricao=?,tipo=?,advogado=?,observacoes=? WHERE id=?',
                (data['descricao'], data['tipo'], data['advogado'], data['obs'], self.current_contrato_id)
            )
            self.db.conn.commit()
            self._refresh_list()
            return self.current_contrato_id
        else:
            cid = self.db.insert_contrato(
                data['cliente_id'], data['ctt_n'], data['descricao'],
                data['tipo'], data['advogado'], data['obs']
            )
            self.current_contrato_id = cid
            self._refresh_list()
            return cid
