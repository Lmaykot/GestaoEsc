# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

### Docker (recommended)
```bash
docker compose up
```
- API: `http://localhost:8000`
- Frontend: `http://localhost:3000`

### Local development

Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Architecture

**GestaoEsc** is a Portuguese-language legal contract management web app.

- **Backend**: FastAPI + SQLite (`backend/`)
- **Frontend**: React + TypeScript + Vite (`frontend/`)
- **Deploy**: Docker Compose via GitHub Container Registry images

### Data Model (5 tables)

```
clientes ←→ contrato_clientes ←→ contratos → honorarios → parcelas
```

- **clientes**: clients/companies (fields: nome, cpf_cnpj, telefone, email, cep, logradouro, numero, complemento, cidade, estado, nome_representante, observacoes)
- **contratos**: legal contracts (each has a unique CTT-N number; fields: cliente_id, ctt_n, descricao, tipo, advogado, observacoes, data_assinatura, status, arquivo_path)
- **contrato_clientes**: many-to-many join between contratos and clientes (supports multiple clients per contract beyond the primary client)
- **honorarios**: fee structures (4 types: inicial, condicionado, intermediário, êxito) attached to a contract
- **parcelas**: payment installments for each honorario

All database access goes through the `Database` class in `backend/app/database.py`. Foreign keys are enforced. Schema migrations are handled idempotently in `Database._migrate()`. The DB path is configurable via `DB_PATH` env var (defaults to `backend/data/gestao_contratos.db`).

### Backend Structure (`backend/app/`)

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app, CORS, router registration |
| `database.py` | `Database` class — all SQL queries |
| `models.py` | Pydantic request/response schemas |
| `dependencies.py` | FastAPI dependency injection (DB instance) |
| `routers/clientes.py` | `/api/clientes` endpoints |
| `routers/contratos.py` | `/api/contratos` endpoints |
| `routers/honorarios.py` | `/api/honorarios` endpoints |
| `routers/parcelas.py` | `/api/parcelas` endpoints |
| `routers/relatorio.py` | `/api/relatorio` endpoint |

### Frontend Structure (`frontend/src/`)

| Path | Purpose |
|------|---------|
| `App.tsx` | Router setup |
| `layouts/AppShell.tsx` | Top-level layout with tab navigation |
| `pages/CadastroCliente/` | Client registration and editing |
| `pages/CadastroContrato/` | Contract registration |
| `pages/HonorariosDialog/` | Fee table editor (modal) |
| `pages/GestaoPagamentos/` | Payment installment management |
| `pages/Relatorio/` | Management report with payment status |
| `design-system/components/` | Shared UI components (Button, Input, Select, Card, Modal, DataTable, etc.) |

### Contract Features

- **Status**: Ativo / Encerrado / Quitado
- **Multiple clients**: a contract has one primary client (`contratos.cliente_id`) plus optional additional clients stored in `contrato_clientes`
- **PDF attachment**: linked to the contract via `arquivo_path`, stored in `contratos/` volume
- **CTT-N numbers**: auto-generated via `db.get_next_ctt_n()` (format: `CTT-N-001`)

## Domain Vocabulary

The UI and code use Portuguese legal terminology:
- **CTT-N**: contract number (e.g. CTT-N-001)
- **Honorários**: attorney fees (the fee structure tied to a contract)
- **Parcelas**: payment installments
- **Quitação**: payment settlement status (Quitado / Pendente / Parcialmente)
- **Hipótese de incidência**: the condition/hypothesis under which a fee applies
