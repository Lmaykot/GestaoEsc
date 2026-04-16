from fastapi import APIRouter, Depends, HTTPException
from app.database import Database
from app.dependencies import get_db
from app.models import (
    RelatorioResponse, RelatorioHonorario, ContratoResponse,
    ClienteResponse, ParcelaResponse, InadimplenteRow,
)

router = APIRouter(prefix="/api/relatorio", tags=["relatorio"])


def _row_to_dict(row):
    return dict(row) if row else None


def _calc_quitacao(parcelas: list[dict]) -> str:
    if not parcelas:
        return "Pendente"
    pagas = sum(1 for p in parcelas if p.get('data_pagamento'))
    total = len(parcelas)
    if pagas == 0:
        return "Pendente"
    if pagas == total:
        return "Quitado"
    return f"{pagas}/{total} pagas"


@router.get("/inadimplentes", response_model=list[InadimplenteRow])
def get_inadimplentes(db: Database = Depends(get_db)):
    rows = db.get_inadimplentes()
    return [dict(r) for r in rows]


@router.get("/{contrato_id}", response_model=RelatorioResponse)
def get_relatorio(contrato_id: int, db: Database = Depends(get_db)):
    contrato_row = db.get_contrato(contrato_id)
    if not contrato_row:
        raise HTTPException(404, "Contrato not found")

    contrato = _row_to_dict(contrato_row)
    honorarios_rows = db.get_honorarios_by_contrato(contrato_id)
    clientes_extras = [_row_to_dict(r) for r in db.get_clientes_by_contrato(contrato_id)]

    honorarios = []
    for h_row in honorarios_rows:
        h = _row_to_dict(h_row)
        parcelas_rows = db.get_parcelas(h['id'])
        parcelas = [_row_to_dict(p) for p in parcelas_rows]
        pagas = sum(1 for p in parcelas if p.get('data_pagamento'))
        honorarios.append(RelatorioHonorario(
            id=h['id'],
            tipo=h['tipo'],
            hipotese=h['hipotese'],
            valor=h['valor'],
            ordem=h['ordem'],
            parcelas=[ParcelaResponse(**p) for p in parcelas],
            total_parcelas=len(parcelas),
            parcelas_pagas=pagas,
            status_quitacao=_calc_quitacao(parcelas),
        ))

    return RelatorioResponse(
        contrato=ContratoResponse(**contrato),
        honorarios=honorarios,
        clientes_extras=[ClienteResponse(**c) for c in clientes_extras],
    )
