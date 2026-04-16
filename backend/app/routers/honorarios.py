from fastapi import APIRouter, Depends, HTTPException
from app.database import Database
from app.dependencies import get_db
from app.models import HonorarioResponse, HonorariosPayload, HonorarioSearchResult

router = APIRouter(tags=["honorarios"])


def _row_to_dict(row):
    return dict(row) if row else None


@router.get("/api/contratos/{contrato_id}/honorarios", response_model=list[HonorarioResponse])
def get_honorarios(contrato_id: int, db: Database = Depends(get_db)):
    rows = db.get_honorarios_by_contrato(contrato_id)
    return [_row_to_dict(r) for r in rows]


@router.put("/api/contratos/{contrato_id}/honorarios")
def replace_honorarios(contrato_id: int, data: HonorariosPayload, db: Database = Depends(get_db)):
    rows = [(h.tipo, h.hipotese, h.valor, h.ordem) for h in data.honorarios]
    db.replace_honorarios(contrato_id, rows)
    return {"ok": True}


@router.get("/api/honorarios/search", response_model=list[HonorarioSearchResult])
def search_honorarios(q: str = "", db: Database = Depends(get_db)):
    rows = db.search_contratos_com_honorarios(q)
    return [_row_to_dict(r) for r in rows]


@router.get("/api/honorarios/{honorario_id}", response_model=HonorarioResponse)
def get_honorario(honorario_id: int, db: Database = Depends(get_db)):
    row = db.get_honorario(honorario_id)
    if not row:
        raise HTTPException(404, "Honorario not found")
    return _row_to_dict(row)
