# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

```bash
python main.py
# or
python3 main.py
```

No dependencies to install — pure Python stdlib (tkinter + sqlite3). The SQLite database (`gestao_contratos.db`) is auto-created on first run.

## Architecture

**GestaoEsc** is a Portuguese-language legal contract management desktop app (tkinter + SQLite).

### Data Model (4 tables, hierarchical)

```
clientes → contratos → honorarios → parcelas
```

- **clientes**: clients/companies
- **contratos**: legal contracts (each has a unique CTT-N number, belongs to a client)
- **honorarios**: fee structures (4 types: inicial, condicionado, intermediário, êxito) attached to a contract
- **parcelas**: payment installments for each honorario

All database access goes through the `Database` class in `database.py`. Foreign keys are enforced.

### UI Structure

`main.py` creates a `ttk.Notebook` with 4 tabs, each implemented in its own file:

| File | Tab | Purpose |
|------|-----|---------|
| `ui_cadastro_cliente.py` | Tab 1 | Client registration and editing |
| `ui_cadastro_contrato.py` | Tab 2 | Contract registration; opens `HonorariosDialog` |
| `ui_gestao_pagamentos.py` | Tab 3 | Payment installment management |
| `ui_relatorio.py` | Tab 4 | Management report with payment status |

All tabs follow the same layout pattern: **left panel** (search + Treeview list) / **right panel** (form or detail view).

`styles.py` centralizes the entire color palette, fonts, and widget style definitions. Use the constants (`C_ACCENT`, `C_BG`, etc.) and helpers (`card_frame()`, `section_label()`, `field_label()`) from there rather than hardcoding styles.

### Key Interactions Between Tabs

- Tab 2 → opens `HonorariosDialog` (modal) after saving a contract
- Tab 4 report → "Gerir" link buttons switch focus to Tab 3 for the selected honorario
- CTT-N numbers are auto-generated via `db.get_next_ctt_n()`

## Domain Vocabulary

The UI and code use Portuguese legal terminology:
- **CTT-N**: contract number (e.g. CTT-N-001)
- **Honorários**: attorney fees (the fee structure tied to a contract)
- **Parcelas**: payment installments
- **Quitação**: payment settlement status (Quitado / Pendente / Parcialmente)
- **Hipótese de incidência**: the condition/hypothesis under which a fee applies
