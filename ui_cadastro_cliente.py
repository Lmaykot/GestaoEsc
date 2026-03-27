import tkinter as tk
from tkinter import ttk, messagebox
from styles import (C_WHITE, C_BG, C_BORDER, C_ACCENT, C_TEXT, C_MUTED,
                    C_ROW_ODD, C_ROW_EVEN, FONT_BODY, FONT_H2, FONT_H3,
                    FONT_SMALL, FONT_TITLE, card_frame, field_label)


class CadastroClienteTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.current_cliente_id = None
        self.configure(style='TFrame')
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header
        hdr = ttk.Frame(self, style='TFrame', padding=(24, 18, 24, 6))
        hdr.grid(row=0, column=0, sticky='ew')
        ttk.Label(hdr, text='Cadastro de Cliente', style='Title.TLabel').pack(side='left')

        # Main content area (two columns: search list | form)
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

        ttk.Label(panel, text='Buscar cliente', style='H2Card.TLabel').grid(
            row=0, column=0, sticky='w', pady=(0, 8))

        search_row = ttk.Frame(panel, style='Card.TFrame')
        search_row.grid(row=1, column=0, sticky='ew', pady=(0, 8))
        search_row.columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *_: self._refresh_list())
        ent = ttk.Entry(search_row, textvariable=self.search_var)
        ent.grid(row=0, column=0, sticky='ew', ipady=4)

        tree_frame = ttk.Frame(panel, style='Card.TFrame')
        tree_frame.grid(row=2, column=0, sticky='nsew')
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=('nome',), show='headings', selectmode='browse')
        self.tree.heading('nome', text='Nome do Cliente')
        self.tree.column('nome', stretch=True)
        self.tree.tag_configure('odd', background=C_ROW_ODD)
        self.tree.tag_configure('even', background=C_ROW_EVEN)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

        vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=vsb.set)

        ttk.Button(panel, text='+ Novo Cliente', command=self._clear_form).grid(
            row=3, column=0, sticky='ew', pady=(8, 0))

        self._refresh_list()

    def _build_form_panel(self, parent):
        panel = card_frame(parent, padding=20)
        panel.grid(row=0, column=1, sticky='nsew')
        panel.columnconfigure(1, weight=1)

        self.form_title = ttk.Label(panel, text='Novo Cliente', style='H2Card.TLabel')
        self.form_title.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 16))

        fields = [
            ('nome',             'Nome do cliente *'),
            ('cpf_cnpj',         'CPF / CNPJ'),
            ('telefone',         'Telefone'),
            ('email',            'E-mail'),
            ('endereco',         'Endereço'),
            ('nome_representante', 'Nome do representante (PJ)'),
        ]
        self.vars = {}
        for i, (key, label) in enumerate(fields, start=1):
            ttk.Label(panel, text=label, style='MutedCard.TLabel').grid(
                row=i, column=0, sticky='w', padx=(0, 12), pady=3)
            v = tk.StringVar()
            self.vars[key] = v
            ttk.Entry(panel, textvariable=v).grid(
                row=i, column=1, sticky='ew', ipady=4, pady=3)

        # Observações (Text widget)
        ttk.Label(panel, text='Observações', style='MutedCard.TLabel').grid(
            row=len(fields) + 1, column=0, sticky='nw', padx=(0, 12), pady=(8, 3))
        obs_frame = ttk.Frame(panel, style='Card.TFrame')
        obs_frame.grid(row=len(fields) + 1, column=1, sticky='ew', pady=(8, 3))
        obs_frame.columnconfigure(0, weight=1)
        self.obs_text = tk.Text(obs_frame, height=4, wrap='word',
                                font=FONT_BODY, bg=C_WHITE, fg=C_TEXT,
                                relief='flat', bd=1,
                                highlightthickness=1, highlightcolor=C_ACCENT,
                                highlightbackground=C_BORDER)
        self.obs_text.grid(row=0, column=0, sticky='ew')

        # Buttons
        btn_row = ttk.Frame(panel, style='Card.TFrame')
        btn_row.grid(row=len(fields) + 2, column=0, columnspan=2, sticky='e', pady=(16, 0))

        ttk.Button(btn_row, text='Cancelar', style='Secondary.TButton',
                   command=self._clear_form).pack(side='left', padx=(0, 8))
        ttk.Button(btn_row, text='Salvar', command=self._save).pack(side='left')

        self.status_lbl = ttk.Label(panel, text='', style='MutedCard.TLabel')
        self.status_lbl.grid(row=len(fields) + 3, column=0, columnspan=2, sticky='w', pady=(8, 0))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        q = self.search_var.get().strip()
        clientes = self.db.search_clientes(q) if q else self.db.get_all_clientes()
        for i, c in enumerate(clientes):
            tag = 'odd' if i % 2 else 'even'
            self.tree.insert('', 'end', iid=str(c['id']), values=(c['nome'],), tags=(tag,))

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        cid = int(sel[0])
        c = self.db.get_cliente(cid)
        if not c:
            return
        self.current_cliente_id = cid
        self.form_title.config(text='Editar Cliente')
        self.vars['nome'].set(c['nome'] or '')
        self.vars['telefone'].set(c['telefone'] or '')
        self.vars['email'].set(c['email'] or '')
        self.vars['endereco'].set(c['endereco'] or '')
        self.vars['nome_representante'].set(c['nome_representante'] or '')
        self.obs_text.delete('1.0', 'end')
        self.obs_text.insert('1.0', c['observacoes'] or '')
        self.status_lbl.config(text='')

    def _clear_form(self):
        self.current_cliente_id = None
        self.form_title.config(text='Novo Cliente')
        for v in self.vars.values():
            v.set('')
        self.obs_text.delete('1.0', 'end')
        self.status_lbl.config(text='')
        self.tree.selection_remove(self.tree.selection())

    def _save(self):
        nome = self.vars['nome'].get().strip()
        if not nome:
            messagebox.showwarning('Atenção', 'O nome do cliente é obrigatório.')
            return
        telefone = self.vars['telefone'].get().strip()
        email    = self.vars['email'].get().strip()
        endereco = self.vars['endereco'].get().strip()
        nome_repr = self.vars['nome_representante'].get().strip()
        obs      = self.obs_text.get('1.0', 'end').strip()

        if self.current_cliente_id:
            self.db.update_cliente(self.current_cliente_id, nome, telefone, email, endereco, nome_repr, obs)
            self.status_lbl.config(text='Cliente atualizado com sucesso.', foreground=C_ACCENT)
        else:
            self.db.insert_cliente(nome, telefone, email, endereco, nome_repr, obs)
            self.status_lbl.config(text='Cliente cadastrado com sucesso.', foreground=C_ACCENT)
            self._clear_form()

        self._refresh_list()
