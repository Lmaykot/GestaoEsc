import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from styles import (C_WHITE, C_BG, C_BORDER, C_ACCENT, C_ACCENT2, C_TEXT,
                    C_MUTED, C_ROW_ODD, C_ROW_EVEN, C_SUCCESS,
                    FONT_BODY, FONT_H2, FONT_H3, FONT_SMALL, FONT_TITLE,
                    card_frame, section_header)
from ui_honorarios_dialog import HonorariosDialog

TIPO_CONTRATO  = ['Contencioso', 'Consultoria', 'Licenciamento', 'Misto']
STATUS_CONTRATO = ['Ativo', 'Encerrado', 'Quitado']
CONTRATOS_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contratos')

STATUS_COLORS = {
    'Ativo':     ('#DCFCE7', '#15803D'),
    'Encerrado': ('#FEE2E2', '#B91C1C'),
    'Quitado':   ('#DBEAFE', '#1D4ED8'),
}


class CadastroContratoTab(ttk.Frame):
    def __init__(self, parent, db, app):
        super().__init__(parent)
        self.db  = db
        self.app = app
        self.current_cliente_id  = None
        self.current_contrato_id = None
        self._extra_cliente_ids  = []   # additional clients beyond primary
        self._arquivo_path       = ''   # relative path inside contratos/
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

        self.tree = ttk.Treeview(tree_frame, columns=('ctt_n', 'cliente', 'status'),
                                 show='headings', selectmode='browse')
        self.tree.heading('ctt_n',    text='CTT-N')
        self.tree.heading('cliente',  text='Cliente')
        self.tree.heading('status',   text='Status')
        self.tree.column('ctt_n',   width=90, stretch=False)
        self.tree.column('cliente', stretch=True)
        self.tree.column('status',  width=80, stretch=False)
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
        # Scrollable card
        outer = card_frame(parent)
        outer.grid(row=0, column=1, sticky='nsew')
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        canvas = tk.Canvas(outer, bg=C_WHITE, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky='nsew')
        vsb = ttk.Scrollbar(outer, orient='vertical', command=canvas.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        canvas.configure(yscrollcommand=vsb.set)

        panel = tk.Frame(canvas, bg=C_WHITE)
        win = canvas.create_window((0, 0), window=panel, anchor='nw')

        def _on_frame_configure(_e):
            canvas.configure(scrollregion=canvas.bbox('all'))
        def _on_canvas_resize(e):
            canvas.itemconfig(win, width=e.width)

        panel.bind('<Configure>', _on_frame_configure)
        canvas.bind('<Configure>', _on_canvas_resize)
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), 'units'))

        panel.columnconfigure(1, weight=1)
        self._panel = panel
        row = 0

        # Title
        self.form_title = tk.Label(panel, text='Novo Contrato', bg=C_WHITE, fg=C_TEXT, font=FONT_H2)
        self.form_title.grid(row=row, column=0, columnspan=3, sticky='w', padx=20, pady=(16, 4))
        row += 1

        # ── Dados do Contrato ─────────────────────────────────────────────
        sh = section_header(panel, 'Dados do Contrato', icon='📋')
        sh.grid(row=row, column=0, columnspan=3, sticky='ew', padx=20)
        row += 1

        # CTT-N
        tk.Label(panel, text='Número do Contrato (CTT-N)', bg=C_WHITE, fg=C_MUTED,
                 font=FONT_SMALL).grid(row=row, column=0, columnspan=3, sticky='w',
                                       padx=20, pady=(0, 1))
        row += 1
        ctt_row = tk.Frame(panel, bg=C_WHITE)
        ctt_row.grid(row=row, column=0, columnspan=3, sticky='ew', padx=20, pady=(0, 8))
        self.ctt_n_var = tk.StringVar()
        ttk.Entry(ctt_row, textvariable=self.ctt_n_var, state='readonly', width=14).pack(side='left', ipady=4)
        ttk.Button(ctt_row, text='Gerar', style='Small.TButton',
                   command=self._generate_ctt).pack(side='left', padx=(6, 0))
        row += 1

        # Data assinatura + Tipo (same row)
        dt_row = tk.Frame(panel, bg=C_WHITE)
        dt_row.grid(row=row, column=0, columnspan=3, sticky='ew', padx=20, pady=(0, 8))
        dt_row.columnconfigure(0, weight=1)
        dt_row.columnconfigure(1, weight=1)
        tk.Label(dt_row, text='Data da assinatura', bg=C_WHITE, fg=C_MUTED,
                 font=FONT_SMALL).grid(row=0, column=0, sticky='w')
        tk.Label(dt_row, text='Tipo de contrato', bg=C_WHITE, fg=C_MUTED,
                 font=FONT_SMALL).grid(row=0, column=1, sticky='w', padx=(12, 0))
        self.data_ass_var = tk.StringVar()
        ttk.Entry(dt_row, textvariable=self.data_ass_var, width=14).grid(
            row=1, column=0, sticky='w', ipady=4, padx=(0, 4))
        self.tipo_var = tk.StringVar()
        ttk.Combobox(dt_row, textvariable=self.tipo_var,
                     values=TIPO_CONTRATO, state='readonly', width=18).grid(
            row=1, column=1, sticky='w', padx=(12, 0), ipady=4)
        row += 1

        # Status
        tk.Label(panel, text='Status do contrato', bg=C_WHITE, fg=C_MUTED,
                 font=FONT_SMALL).grid(row=row, column=0, columnspan=3, sticky='w',
                                       padx=20, pady=(0, 1))
        row += 1
        status_row = tk.Frame(panel, bg=C_WHITE)
        status_row.grid(row=row, column=0, columnspan=3, sticky='w', padx=20, pady=(0, 8))
        self.status_var = tk.StringVar(value='Ativo')
        for s in STATUS_CONTRATO:
            bg, fg = STATUS_COLORS[s]
            rb = tk.Radiobutton(status_row, text=s, variable=self.status_var, value=s,
                                bg=C_WHITE, fg=fg, activebackground=C_WHITE,
                                selectcolor=bg, font=FONT_SMALL, padx=8, pady=4,
                                relief='solid', bd=1, cursor='hand2')
            rb.pack(side='left', padx=(0, 6))
        row += 1

        # ── Partes ────────────────────────────────────────────────────────
        sh2 = section_header(panel, 'Partes', icon='👥')
        sh2.grid(row=row, column=0, columnspan=3, sticky='ew', padx=20)
        row += 1

        # Primary client search
        tk.Label(panel, text='Cliente principal *', bg=C_WHITE, fg=C_MUTED,
                 font=FONT_SMALL).grid(row=row, column=0, columnspan=3, sticky='w',
                                       padx=20, pady=(0, 1))
        row += 1
        cs_frame = tk.Frame(panel, bg=C_WHITE)
        cs_frame.grid(row=row, column=0, columnspan=3, sticky='ew', padx=20, pady=(0, 2))
        cs_frame.columnconfigure(0, weight=1)
        self._cs_frame = cs_frame

        self.cliente_search_var = tk.StringVar()
        self.cliente_search_var.trace_add('write', lambda *_: self._update_cliente_dropdown())
        cs_entry = ttk.Entry(cs_frame, textvariable=self.cliente_search_var)
        cs_entry.grid(row=0, column=0, sticky='ew', ipady=4)
        cs_entry.bind('<FocusIn>',  lambda e: self._show_dropdown())
        cs_entry.bind('<FocusOut>', lambda e: self.after(150, self._hide_dropdown))

        self.dropdown_frame = tk.Frame(panel, bg=C_WHITE, bd=1, relief='solid')
        self.dropdown_lb = tk.Listbox(self.dropdown_frame, font=FONT_BODY,
                                      bg=C_WHITE, fg=C_TEXT, selectbackground=C_ACCENT,
                                      height=4, bd=0, relief='flat')
        self.dropdown_lb.pack(fill='both', expand=True)
        self.dropdown_lb.bind('<<ListboxSelect>>', self._on_cliente_pick)
        self.dropdown_visible = False
        self._cliente_results = []
        row += 1

        self.cliente_lbl = tk.Label(panel, text='', bg=C_WHITE, fg=C_ACCENT, font=FONT_H3)
        self.cliente_lbl.grid(row=row, column=0, columnspan=3, sticky='w',
                              padx=20, pady=(0, 8))
        row += 1

        # Additional clients
        tk.Label(panel, text='Clientes adicionais', bg=C_WHITE, fg=C_MUTED,
                 font=FONT_SMALL).grid(row=row, column=0, columnspan=3, sticky='w',
                                       padx=20, pady=(0, 2))
        row += 1

        self._extra_clientes_frame = tk.Frame(panel, bg=C_WHITE)
        self._extra_clientes_frame.grid(row=row, column=0, columnspan=3,
                                         sticky='ew', padx=20, pady=(0, 4))
        row += 1

        add_extra_btn = ttk.Button(panel, text='＋ Adicionar cliente',
                                   style='Secondary.TButton',
                                   command=self._open_add_extra_cliente)
        add_extra_btn.grid(row=row, column=0, columnspan=3, sticky='w',
                           padx=20, pady=(0, 8))
        row += 1

        # Advogado
        tk.Label(panel, text='Advogado responsável', bg=C_WHITE, fg=C_MUTED,
                 font=FONT_SMALL).grid(row=row, column=0, columnspan=3, sticky='w',
                                       padx=20, pady=(0, 1))
        row += 1
        self.advogado_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.advogado_var).grid(
            row=row, column=0, columnspan=3, sticky='ew', padx=20, ipady=4, pady=(0, 8))
        row += 1

        # ── Objeto e Observações ──────────────────────────────────────────
        sh3 = section_header(panel, 'Objeto e Observações', icon='📄')
        sh3.grid(row=row, column=0, columnspan=3, sticky='ew', padx=20)
        row += 1

        tk.Label(panel, text='Objeto do contrato', bg=C_WHITE, fg=C_MUTED,
                 font=FONT_SMALL).grid(row=row, column=0, columnspan=3, sticky='w',
                                       padx=20, pady=(0, 1))
        row += 1
        desc_f = tk.Frame(panel, bg=C_WHITE)
        desc_f.grid(row=row, column=0, columnspan=3, sticky='ew', padx=20, pady=(0, 8))
        desc_f.columnconfigure(0, weight=1)
        self.desc_text = tk.Text(desc_f, height=4, wrap='word', font=FONT_BODY,
                                 bg=C_WHITE, fg=C_TEXT, relief='flat', bd=1,
                                 highlightthickness=1, highlightcolor=C_ACCENT,
                                 highlightbackground=C_BORDER)
        self.desc_text.grid(row=0, column=0, sticky='ew')
        desc_vsb = ttk.Scrollbar(desc_f, orient='vertical', command=self.desc_text.yview)
        desc_vsb.grid(row=0, column=1, sticky='ns')
        self.desc_text.configure(yscrollcommand=desc_vsb.set)
        row += 1

        tk.Label(panel, text='Observações adicionais', bg=C_WHITE, fg=C_MUTED,
                 font=FONT_SMALL).grid(row=row, column=0, columnspan=3, sticky='w',
                                       padx=20, pady=(0, 1))
        row += 1
        obs_f = tk.Frame(panel, bg=C_WHITE)
        obs_f.grid(row=row, column=0, columnspan=3, sticky='ew', padx=20, pady=(0, 8))
        obs_f.columnconfigure(0, weight=1)
        self.obs_text = tk.Text(obs_f, height=3, wrap='word', font=FONT_BODY,
                                bg=C_WHITE, fg=C_TEXT, relief='flat', bd=1,
                                highlightthickness=1, highlightcolor=C_ACCENT,
                                highlightbackground=C_BORDER)
        self.obs_text.grid(row=0, column=0, sticky='ew')
        obs_vsb = ttk.Scrollbar(obs_f, orient='vertical', command=self.obs_text.yview)
        obs_vsb.grid(row=0, column=1, sticky='ns')
        self.obs_text.configure(yscrollcommand=obs_vsb.set)
        row += 1

        # ── Documento PDF ─────────────────────────────────────────────────
        sh4 = section_header(panel, 'Documento do Contrato', icon='📎')
        sh4.grid(row=row, column=0, columnspan=3, sticky='ew', padx=20)
        row += 1

        pdf_row = tk.Frame(panel, bg=C_WHITE)
        pdf_row.grid(row=row, column=0, columnspan=3, sticky='ew', padx=20, pady=(0, 8))
        self.arquivo_lbl = tk.Label(pdf_row, text='Nenhum arquivo vinculado',
                                     bg=C_WHITE, fg=C_MUTED, font=FONT_SMALL)
        self.arquivo_lbl.pack(side='left', padx=(0, 8))
        ttk.Button(pdf_row, text='📎 Anexar PDF', style='Secondary.TButton',
                   command=self._attach_pdf).pack(side='left', padx=(0, 6))
        self.open_pdf_btn = ttk.Button(pdf_row, text='Abrir', style='Link.TButton',
                                        command=self._open_pdf)
        self.rem_pdf_btn  = ttk.Button(pdf_row, text='Remover', style='Danger.TButton',
                                        command=self._remove_pdf)
        row += 1

        # Buttons
        btn_row = tk.Frame(panel, bg=C_WHITE)
        btn_row.grid(row=row, column=0, columnspan=3, sticky='e', padx=20, pady=(8, 4))
        ttk.Button(btn_row, text='Cancelar', style='Secondary.TButton',
                   command=self._clear_form).pack(side='left', padx=(0, 8))
        ttk.Button(btn_row, text='Salvar', style='Secondary.TButton',
                   command=self._save_only).pack(side='left', padx=(0, 8))
        ttk.Button(btn_row, text='Salvar e Avançar →',
                   command=self._save_and_advance).pack(side='left')
        row += 1

        self.status_lbl = tk.Label(panel, text='', bg=C_WHITE, fg=C_ACCENT, font=FONT_SMALL)
        self.status_lbl.grid(row=row, column=0, columnspan=3, sticky='w',
                              padx=20, pady=(4, 16))

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

    # ── Extra clients ─────────────────────────────────────────────────────────

    def _open_add_extra_cliente(self):
        """Popup to search and pick an additional client."""
        win = tk.Toplevel(self)
        win.title('Adicionar cliente')
        win.geometry('400x300')
        win.configure(bg=C_BG)
        win.grab_set()

        ttk.Label(win, text='Buscar cliente', style='H2.TLabel').pack(
            anchor='w', padx=16, pady=(12, 4))

        sv = tk.StringVar()
        ent = ttk.Entry(win, textvariable=sv)
        ent.pack(fill='x', padx=16, ipady=4)

        lb = tk.Listbox(win, font=FONT_BODY, bg=C_WHITE, fg=C_TEXT,
                        selectbackground=C_ACCENT, bd=0, relief='flat')
        lb.pack(fill='both', expand=True, padx=16, pady=8)

        results = []

        def _search(*_):
            lb.delete(0, 'end')
            results.clear()
            q = sv.get().strip()
            if not q:
                return
            for c in self.db.search_clientes(q):
                if c['id'] != self.current_cliente_id and c['id'] not in self._extra_cliente_ids:
                    results.append(c)
                    lb.insert('end', c['nome'])

        sv.trace_add('write', _search)

        def _pick(_event=None):
            sel = lb.curselection()
            if not sel:
                return
            c = results[sel[0]]
            self._extra_cliente_ids.append(c['id'])
            self._refresh_extra_clientes()
            win.destroy()

        lb.bind('<Double-Button-1>', _pick)
        ttk.Button(win, text='Adicionar', command=_pick).pack(padx=16, pady=(0, 12))
        ent.focus_set()

    def _refresh_extra_clientes(self):
        for w in self._extra_clientes_frame.winfo_children():
            w.destroy()
        for cid in self._extra_cliente_ids:
            c = self.db.get_cliente(cid)
            if not c:
                continue
            row_f = tk.Frame(self._extra_clientes_frame, bg=C_WHITE,
                             bd=1, relief='solid', padx=6, pady=2)
            row_f.pack(side='left', padx=(0, 6), pady=2)
            tk.Label(row_f, text=c['nome'], bg=C_WHITE, fg=C_TEXT, font=FONT_SMALL).pack(side='left')
            ttk.Button(row_f, text='✕', style='Danger.TButton',
                       command=lambda i=cid: self._remove_extra(i)).pack(side='left', padx=(4, 0))

    def _remove_extra(self, cliente_id):
        if cliente_id in self._extra_cliente_ids:
            self._extra_cliente_ids.remove(cliente_id)
        self._refresh_extra_clientes()

    # ── PDF ───────────────────────────────────────────────────────────────────

    def _attach_pdf(self):
        path = filedialog.askopenfilename(
            title='Selecionar arquivo PDF',
            filetypes=[('Arquivo PDF', '*.pdf'), ('Todos os arquivos', '*.*')]
        )
        if not path:
            return
        ctt_n = self.ctt_n_var.get().strip()
        if not ctt_n:
            messagebox.showwarning('Atenção', 'Gere o número CTT-N antes de anexar o arquivo.')
            return
        cliente_nome = self.cliente_lbl.cget('text').lstrip('✓').strip() or 'Cliente'
        safe_name = f"{ctt_n} - {cliente_nome}.pdf"
        dest = os.path.join(CONTRATOS_DIR, safe_name)
        try:
            shutil.copy2(path, dest)
            self._arquivo_path = safe_name
            self._update_pdf_ui()
        except Exception as e:
            messagebox.showerror('Erro', f'Não foi possível copiar o arquivo:\n{e}')

    def _update_pdf_ui(self):
        if self._arquivo_path:
            self.arquivo_lbl.config(text=self._arquivo_path, fg=C_TEXT)
            self.open_pdf_btn.pack(side='left', padx=(0, 6))
            self.rem_pdf_btn.pack(side='left')
        else:
            self.arquivo_lbl.config(text='Nenhum arquivo vinculado', fg=C_MUTED)
            self.open_pdf_btn.pack_forget()
            self.rem_pdf_btn.pack_forget()

    def _open_pdf(self):
        if not self._arquivo_path:
            return
        full = os.path.join(CONTRATOS_DIR, self._arquivo_path)
        if not os.path.exists(full):
            messagebox.showwarning('Arquivo não encontrado', f'O arquivo não foi encontrado:\n{full}')
            return
        if sys.platform == 'win32':
            os.startfile(full)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', full])
        else:
            subprocess.Popen(['xdg-open', full])

    def _remove_pdf(self):
        self._arquivo_path = ''
        self._update_pdf_ui()

    # ── List ──────────────────────────────────────────────────────────────────

    def _refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        q = self.search_var.get().strip()
        rows = self.db.search_contratos_by_cliente_nome(q)
        for i, r in enumerate(rows):
            tag = 'odd' if i % 2 else 'even'
            self.tree.insert('', 'end', iid=str(r['id']),
                             values=(r['ctt_n'], r['cliente_nome'],
                                     r['status'] if 'status' in r.keys() else 'Ativo'),
                             tags=(tag,))

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
        self.data_ass_var.set(c['data_assinatura'] if 'data_assinatura' in c.keys() else '')
        self.status_var.set(c['status'] if 'status' in c.keys() else 'Ativo')
        self._arquivo_path = c['arquivo_path'] if 'arquivo_path' in c.keys() else ''
        self._update_pdf_ui()
        self.desc_text.delete('1.0', 'end')
        self.desc_text.insert('1.0', c['descricao'] or '')
        self.obs_text.delete('1.0', 'end')
        self.obs_text.insert('1.0', c['observacoes'] or '')
        # Load extra clients
        extra = self.db.get_clientes_by_contrato(cid)
        self._extra_cliente_ids = [ec['id'] for ec in extra if ec['id'] != c['cliente_id']]
        self._refresh_extra_clientes()
        self.status_lbl.config(text='')

    def _clear_form(self):
        self.current_contrato_id = None
        self.current_cliente_id  = None
        self._extra_cliente_ids  = []
        self._arquivo_path       = ''
        self.form_title.config(text='Novo Contrato')
        self.cliente_search_var.set('')
        self.cliente_lbl.config(text='')
        self.ctt_n_var.set('')
        self.tipo_var.set('')
        self.advogado_var.set('')
        self.data_ass_var.set('')
        self.status_var.set('Ativo')
        self.desc_text.delete('1.0', 'end')
        self.obs_text.delete('1.0', 'end')
        self._refresh_extra_clientes()
        self._update_pdf_ui()
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
            'cliente_id':      self.current_cliente_id,
            'ctt_n':           ctt_n,
            'descricao':       self.desc_text.get('1.0', 'end').strip(),
            'tipo':            self.tipo_var.get().strip(),
            'advogado':        self.advogado_var.get().strip(),
            'obs':             self.obs_text.get('1.0', 'end').strip(),
            'data_assinatura': self.data_ass_var.get().strip(),
            'status':          self.status_var.get(),
            'arquivo_path':    self._arquivo_path,
        }

    def _save_only(self):
        data = self._collect_data()
        if not data:
            return
        self._persist(data)
        self.status_lbl.config(text='Contrato salvo.')

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
            self.db.update_contrato(
                self.current_contrato_id,
                data['descricao'], data['tipo'], data['advogado'], data['obs'],
                data['data_assinatura'], data['status'], data['arquivo_path']
            )
            cid = self.current_contrato_id
        else:
            cid = self.db.insert_contrato(
                data['cliente_id'], data['ctt_n'], data['descricao'],
                data['tipo'], data['advogado'], data['obs'],
                data['data_assinatura'], data['status'], data['arquivo_path']
            )
            self.current_contrato_id = cid

        # Persist extra clients (all clients incl. primary in contrato_clientes)
        all_ids = [data['cliente_id']] + [i for i in self._extra_cliente_ids
                                           if i != data['cliente_id']]
        self.db.set_clientes_contrato(cid, all_ids)

        self._refresh_list()
        return cid
