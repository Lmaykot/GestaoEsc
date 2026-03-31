from fastapi import APIRouter, Depends
from app.database import Database
from app.dependencies import get_db
from app.models import ParcelaResponse, ParcelasPayload

router = APIRouter(prefix="/api/honorarios/{honorario_id}/parcelas", tags=["parcelas"])


def _row_to_dict(row):
    return dict(row) if row else None


@router.get("", response_model=list[ParcelaResponse])
def get_parcelas(honorario_id: int, db: Database = Depends(get_db)):
    rows = db.get_parcelas(honorario_id)
    return [_row_to_dict(r) for r in rows]


@router.put("")
def save_parcelas(honorario_id: int, data: ParcelasPayload, db: Database = Depends(get_db)):
    parcelas = [
        {
            'num': p.num,
            'valor': p.valor,
            'vencimento': p.vencimento,
            'nota_fiscal': p.nota_fiscal,
            'data_pagamento': p.data_pagamento,
        }
        for p in data.parcelas
    ]
    db.save_parcelas(honorario_id, parcelas)
    return {"ok": True}
