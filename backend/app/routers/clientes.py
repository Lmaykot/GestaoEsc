from fastapi import APIRouter, Depends, HTTPException
from app.database import Database
from app.dependencies import get_db
from app.models import ClienteCreate, ClienteResponse

router = APIRouter(prefix="/api/clientes", tags=["clientes"])


def _row_to_dict(row):
    return dict(row) if row else None


@router.get("", response_model=list[ClienteResponse])
def list_clientes(q: str = "", db: Database = Depends(get_db)):
    rows = db.search_clientes(q) if q else db.get_all_clientes()
    return [_row_to_dict(r) for r in rows]


@router.get("/{cliente_id}", response_model=ClienteResponse)
def get_cliente(cliente_id: int, db: Database = Depends(get_db)):
    row = db.get_cliente(cliente_id)
    if not row:
        raise HTTPException(404, "Cliente not found")
    return _row_to_dict(row)


@router.post("", response_model=ClienteResponse, status_code=201)
def create_cliente(data: ClienteCreate, db: Database = Depends(get_db)):
    cid = db.insert_cliente(
        data.nome, data.cpf_cnpj, data.telefone, data.email,
        data.cep, data.logradouro, data.numero, data.complemento,
        data.cidade, data.estado, data.nome_representante, data.observacoes
    )
    return _row_to_dict(db.get_cliente(cid))


@router.put("/{cliente_id}", response_model=ClienteResponse)
def update_cliente(cliente_id: int, data: ClienteCreate, db: Database = Depends(get_db)):
    if not db.get_cliente(cliente_id):
        raise HTTPException(404, "Cliente not found")
    db.update_cliente(
        cliente_id, data.nome, data.cpf_cnpj, data.telefone, data.email,
        data.cep, data.logradouro, data.numero, data.complemento,
        data.cidade, data.estado, data.nome_representante, data.observacoes
    )
    return _row_to_dict(db.get_cliente(cliente_id))
