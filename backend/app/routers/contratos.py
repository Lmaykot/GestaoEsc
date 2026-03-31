import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.database import Database
from app.dependencies import get_db
from app.models import (
    ContratoCreate, ContratoUpdate, ContratoResponse,
    ContratoClientesPayload, ClienteResponse,
)

router = APIRouter(prefix="/api/contratos", tags=["contratos"])

CONTRATOS_DIR = os.environ.get('CONTRATOS_DIR', os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'contratos'))


def _row_to_dict(row):
    return dict(row) if row else None


@router.get("/next-ctt-n")
def next_ctt_n(db: Database = Depends(get_db)):
    return {"ctt_n": db.get_next_ctt_n()}


@router.get("", response_model=list[ContratoResponse])
def list_contratos(cliente_nome: str = "", numero: str = "", db: Database = Depends(get_db)):
    if numero:
        rows = db.search_contrato_by_numero(numero)
    elif cliente_nome:
        rows = db.search_contratos_by_cliente_nome(cliente_nome)
    else:
        rows = db.search_contratos_by_cliente_nome("")
    return [_row_to_dict(r) for r in rows]


@router.get("/{contrato_id}", response_model=ContratoResponse)
def get_contrato(contrato_id: int, db: Database = Depends(get_db)):
    row = db.get_contrato(contrato_id)
    if not row:
        raise HTTPException(404, "Contrato not found")
    return _row_to_dict(row)


@router.post("", response_model=ContratoResponse, status_code=201)
def create_contrato(data: ContratoCreate, db: Database = Depends(get_db)):
    cid = db.insert_contrato(
        data.cliente_id, data.ctt_n, data.descricao, data.tipo,
        data.advogado, data.observacoes, data.data_assinatura,
        data.status, data.arquivo_path
    )
    return _row_to_dict(db.get_contrato(cid))


@router.put("/{contrato_id}", response_model=ContratoResponse)
def update_contrato(contrato_id: int, data: ContratoUpdate, db: Database = Depends(get_db)):
    if not db.get_contrato(contrato_id):
        raise HTTPException(404, "Contrato not found")
    db.update_contrato(
        contrato_id, data.descricao, data.tipo, data.advogado,
        data.observacoes, data.data_assinatura, data.status, data.arquivo_path
    )
    return _row_to_dict(db.get_contrato(contrato_id))


# -- Extra clients --

@router.get("/{contrato_id}/clientes", response_model=list[ClienteResponse])
def get_contrato_clientes(contrato_id: int, db: Database = Depends(get_db)):
    rows = db.get_clientes_by_contrato(contrato_id)
    return [_row_to_dict(r) for r in rows]


@router.put("/{contrato_id}/clientes")
def set_contrato_clientes(contrato_id: int, data: ContratoClientesPayload, db: Database = Depends(get_db)):
    db.set_clientes_contrato(contrato_id, data.cliente_ids)
    return {"ok": True}


# -- PDF --

@router.post("/{contrato_id}/pdf")
async def upload_pdf(contrato_id: int, file: UploadFile = File(...), db: Database = Depends(get_db)):
    contrato = db.get_contrato(contrato_id)
    if not contrato:
        raise HTTPException(404, "Contrato not found")

    os.makedirs(CONTRATOS_DIR, exist_ok=True)
    filename = f"{contrato['ctt_n']} - {contrato['cliente_nome']}.pdf"
    filepath = os.path.join(CONTRATOS_DIR, filename)

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    db.update_contrato(
        contrato_id, contrato['descricao'], contrato['tipo'],
        contrato['advogado'], contrato['observacoes'],
        contrato['data_assinatura'], contrato['status'], filename
    )
    return {"arquivo_path": filename}


@router.get("/{contrato_id}/pdf")
def download_pdf(contrato_id: int, db: Database = Depends(get_db)):
    contrato = db.get_contrato(contrato_id)
    if not contrato or not contrato['arquivo_path']:
        raise HTTPException(404, "PDF not found")
    filepath = os.path.join(CONTRATOS_DIR, contrato['arquivo_path'])
    if not os.path.exists(filepath):
        raise HTTPException(404, "PDF file not found on disk")
    return FileResponse(filepath, media_type="application/pdf", filename=contrato['arquivo_path'])


@router.delete("/{contrato_id}/pdf")
def remove_pdf(contrato_id: int, db: Database = Depends(get_db)):
    contrato = db.get_contrato(contrato_id)
    if not contrato:
        raise HTTPException(404, "Contrato not found")
    db.update_contrato(
        contrato_id, contrato['descricao'], contrato['tipo'],
        contrato['advogado'], contrato['observacoes'],
        contrato['data_assinatura'], contrato['status'], ''
    )
    return {"ok": True}
