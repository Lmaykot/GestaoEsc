import sqlite3
import os

DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'gestao_contratos.db'))


class Database:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()
        self._migrate()

    def _create_tables(self):
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf_cnpj TEXT DEFAULT '',
                telefone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                endereco TEXT DEFAULT '',
                cep TEXT DEFAULT '',
                logradouro TEXT DEFAULT '',
                numero TEXT DEFAULT '',
                complemento TEXT DEFAULT '',
                cidade TEXT DEFAULT '',
                estado TEXT DEFAULT '',
                nome_representante TEXT DEFAULT '',
                observacoes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS contratos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                ctt_n TEXT UNIQUE NOT NULL,
                descricao TEXT DEFAULT '',
                tipo TEXT DEFAULT '',
                advogado TEXT DEFAULT '',
                observacoes TEXT DEFAULT '',
                data_assinatura TEXT DEFAULT '',
                status TEXT DEFAULT 'Ativo',
                arquivo_path TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            );

            CREATE TABLE IF NOT EXISTS contrato_clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contrato_id INTEGER NOT NULL,
                cliente_id INTEGER NOT NULL,
                ordem INTEGER DEFAULT 0,
                FOREIGN KEY (contrato_id) REFERENCES contratos(id),
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            );

            CREATE TABLE IF NOT EXISTS honorarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contrato_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                hipotese TEXT DEFAULT '',
                valor TEXT DEFAULT '',
                ordem INTEGER DEFAULT 0,
                FOREIGN KEY (contrato_id) REFERENCES contratos(id)
            );

            CREATE TABLE IF NOT EXISTS parcelas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                honorario_id INTEGER NOT NULL,
                num_parcela INTEGER,
                valor TEXT DEFAULT '',
                vencimento TEXT DEFAULT '',
                nota_fiscal TEXT DEFAULT '',
                data_pagamento TEXT DEFAULT '',
                FOREIGN KEY (honorario_id) REFERENCES honorarios(id)
            );
        ''')
        self.conn.commit()

    def _migrate(self):
        migrations = [
            "ALTER TABLE clientes ADD COLUMN cpf_cnpj TEXT DEFAULT ''",
            "ALTER TABLE clientes ADD COLUMN cep TEXT DEFAULT ''",
            "ALTER TABLE clientes ADD COLUMN logradouro TEXT DEFAULT ''",
            "ALTER TABLE clientes ADD COLUMN numero TEXT DEFAULT ''",
            "ALTER TABLE clientes ADD COLUMN complemento TEXT DEFAULT ''",
            "ALTER TABLE clientes ADD COLUMN cidade TEXT DEFAULT ''",
            "ALTER TABLE clientes ADD COLUMN estado TEXT DEFAULT ''",
            "ALTER TABLE contratos ADD COLUMN data_assinatura TEXT DEFAULT ''",
            "ALTER TABLE contratos ADD COLUMN status TEXT DEFAULT 'Ativo'",
            "ALTER TABLE contratos ADD COLUMN arquivo_path TEXT DEFAULT ''",
        ]
        for sql in migrations:
            try:
                self.conn.execute(sql)
                self.conn.commit()
            except Exception:
                pass

    # -- Clientes --

    def insert_cliente(self, nome, cpf_cnpj, telefone, email,
                       cep, logradouro, numero, complemento, cidade, estado,
                       nome_repr, obs):
        cur = self.conn.execute(
            '''INSERT INTO clientes
               (nome,cpf_cnpj,telefone,email,cep,logradouro,numero,complemento,cidade,estado,
                nome_representante,observacoes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
            (nome, cpf_cnpj, telefone, email,
             cep, logradouro, numero, complemento, cidade, estado,
             nome_repr, obs)
        )
        self.conn.commit()
        return cur.lastrowid

    def update_cliente(self, cid, nome, cpf_cnpj, telefone, email,
                       cep, logradouro, numero, complemento, cidade, estado,
                       nome_repr, obs):
        self.conn.execute(
            '''UPDATE clientes SET
               nome=?,cpf_cnpj=?,telefone=?,email=?,cep=?,logradouro=?,
               numero=?,complemento=?,cidade=?,estado=?,
               nome_representante=?,observacoes=?
               WHERE id=?''',
            (nome, cpf_cnpj, telefone, email,
             cep, logradouro, numero, complemento, cidade, estado,
             nome_repr, obs, cid)
        )
        self.conn.commit()

    def get_cliente(self, cid):
        return self.conn.execute('SELECT * FROM clientes WHERE id=?', (cid,)).fetchone()

    def search_clientes(self, query):
        return self.conn.execute(
            'SELECT * FROM clientes WHERE nome LIKE ? ORDER BY nome',
            (f'%{query}%',)
        ).fetchall()

    def get_all_clientes(self):
        return self.conn.execute('SELECT * FROM clientes ORDER BY nome').fetchall()

    # -- Contratos --

    def get_next_ctt_n(self):
        row = self.conn.execute(
            "SELECT ctt_n FROM contratos ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if not row:
            return 'CTT-N-001'
        try:
            num = int(row['ctt_n'].split('-')[-1]) + 1
        except (ValueError, IndexError):
            num = self.conn.execute('SELECT COUNT(*) FROM contratos').fetchone()[0] + 1
        return f'CTT-N-{num:03d}'

    def insert_contrato(self, cliente_id, ctt_n, descricao, tipo, advogado, obs,
                        data_assinatura='', status='Ativo', arquivo_path=''):
        cur = self.conn.execute(
            '''INSERT INTO contratos
               (cliente_id,ctt_n,descricao,tipo,advogado,observacoes,data_assinatura,status,arquivo_path)
               VALUES (?,?,?,?,?,?,?,?,?)''',
            (cliente_id, ctt_n, descricao, tipo, advogado, obs,
             data_assinatura, status, arquivo_path)
        )
        self.conn.commit()
        return cur.lastrowid

    def update_contrato(self, cid, descricao, tipo, advogado, obs,
                        data_assinatura='', status='Ativo', arquivo_path=''):
        self.conn.execute(
            '''UPDATE contratos SET
               descricao=?,tipo=?,advogado=?,observacoes=?,
               data_assinatura=?,status=?,arquivo_path=?
               WHERE id=?''',
            (descricao, tipo, advogado, obs,
             data_assinatura, status, arquivo_path, cid)
        )
        self.conn.commit()

    def get_contrato(self, cid):
        return self.conn.execute('''
            SELECT c.*, cl.nome AS cliente_nome
            FROM contratos c JOIN clientes cl ON c.cliente_id=cl.id
            WHERE c.id=?
        ''', (cid,)).fetchone()

    def search_contratos_by_cliente_nome(self, nome):
        return self.conn.execute('''
            SELECT c.*, cl.nome AS cliente_nome
            FROM contratos c JOIN clientes cl ON c.cliente_id=cl.id
            WHERE cl.nome LIKE ? ORDER BY c.ctt_n
        ''', (f'%{nome}%',)).fetchall()

    def search_contrato_by_numero(self, numero):
        padded = numero.zfill(3) if numero.isdigit() else numero
        return self.conn.execute('''
            SELECT c.*, cl.nome AS cliente_nome
            FROM contratos c JOIN clientes cl ON c.cliente_id=cl.id
            WHERE c.ctt_n LIKE ? OR c.ctt_n LIKE ? ORDER BY c.ctt_n
        ''', (f'%{numero}%', f'CTT-N-{padded}%')).fetchall()

    def search_contratos_com_honorarios(self, query):
        q = f'%{query}%'
        return self.conn.execute('''
            SELECT h.id AS honorario_id, h.tipo, h.hipotese, h.valor,
                   c.id AS contrato_id, c.ctt_n, cl.nome AS cliente_nome
            FROM honorarios h
            JOIN contratos c ON h.contrato_id = c.id
            JOIN clientes cl ON c.cliente_id = cl.id
            WHERE cl.nome LIKE ? OR c.ctt_n LIKE ?
            ORDER BY c.ctt_n, h.tipo, h.ordem
        ''', (q, q)).fetchall()

    def get_contratos_by_cliente(self, cliente_id):
        return self.conn.execute(
            'SELECT * FROM contratos WHERE cliente_id=? ORDER BY ctt_n', (cliente_id,)
        ).fetchall()

    # -- Contrato <-> Clientes --

    def get_clientes_by_contrato(self, contrato_id):
        return self.conn.execute('''
            SELECT cl.* FROM clientes cl
            JOIN contrato_clientes cc ON cc.cliente_id = cl.id
            WHERE cc.contrato_id = ?
            ORDER BY cc.ordem
        ''', (contrato_id,)).fetchall()

    def set_clientes_contrato(self, contrato_id, cliente_ids):
        self.conn.execute('DELETE FROM contrato_clientes WHERE contrato_id=?', (contrato_id,))
        for ordem, cid in enumerate(cliente_ids):
            self.conn.execute(
                'INSERT INTO contrato_clientes (contrato_id,cliente_id,ordem) VALUES (?,?,?)',
                (contrato_id, cid, ordem)
            )
        self.conn.commit()

    # -- Honorarios --

    def replace_honorarios(self, contrato_id, rows):
        existing = self.get_honorarios_by_contrato(contrato_id)
        for h in existing:
            self.conn.execute('DELETE FROM parcelas WHERE honorario_id=?', (h['id'],))
        self.conn.execute('DELETE FROM honorarios WHERE contrato_id=?', (contrato_id,))
        for r in rows:
            self.conn.execute(
                'INSERT INTO honorarios (contrato_id,tipo,hipotese,valor,ordem) VALUES (?,?,?,?,?)',
                (contrato_id, r[0], r[1], r[2], r[3])
            )
        self.conn.commit()

    def get_honorarios_by_contrato(self, contrato_id):
        return self.conn.execute(
            'SELECT * FROM honorarios WHERE contrato_id=? ORDER BY tipo,ordem', (contrato_id,)
        ).fetchall()

    def get_honorario(self, hid):
        return self.conn.execute('SELECT * FROM honorarios WHERE id=?', (hid,)).fetchone()

    # -- Parcelas --

    def save_parcelas(self, honorario_id, parcelas):
        self.conn.execute('DELETE FROM parcelas WHERE honorario_id=?', (honorario_id,))
        for p in parcelas:
            self.conn.execute(
                'INSERT INTO parcelas (honorario_id,num_parcela,valor,vencimento,nota_fiscal,data_pagamento) VALUES (?,?,?,?,?,?)',
                (honorario_id, p['num'], p['valor'], p['vencimento'], p['nota_fiscal'], p['data_pagamento'])
            )
        self.conn.commit()

    def get_parcelas(self, honorario_id):
        return self.conn.execute(
            'SELECT * FROM parcelas WHERE honorario_id=? ORDER BY num_parcela', (honorario_id,)
        ).fetchall()

    def get_inadimplentes(self):
        return self.conn.execute('''
            SELECT p.id AS parcela_id, p.vencimento, p.valor, p.nota_fiscal,
                   h.id AS honorario_id, h.tipo, h.hipotese,
                   c.id AS contrato_id, c.ctt_n,
                   cl.id AS cliente_id, cl.nome AS cliente_nome
            FROM parcelas p
            JOIN honorarios h ON p.honorario_id = h.id
            JOIN contratos c ON h.contrato_id = c.id
            JOIN clientes cl ON c.cliente_id = cl.id
            WHERE p.vencimento < date('now')
              AND (p.data_pagamento IS NULL OR p.data_pagamento = '')
            ORDER BY p.vencimento ASC, c.ctt_n
        ''').fetchall()

    def close(self):
        self.conn.close()
