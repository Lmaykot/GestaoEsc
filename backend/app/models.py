from pydantic import BaseModel


# -- Clientes --

class ClienteCreate(BaseModel):
    nome: str
    cpf_cnpj: str = ''
    telefone: str = ''
    email: str = ''
    cep: str = ''
    logradouro: str = ''
    numero: str = ''
    complemento: str = ''
    cidade: str = ''
    estado: str = ''
    nome_representante: str = ''
    observacoes: str = ''


class ClienteResponse(ClienteCreate):
    id: int
    created_at: str | None = None


# -- Contratos --

class ContratoCreate(BaseModel):
    cliente_id: int
    ctt_n: str
    descricao: str = ''
    tipo: str = ''
    advogado: str = ''
    observacoes: str = ''
    data_assinatura: str = ''
    status: str = 'Ativo'
    arquivo_path: str = ''


class ContratoUpdate(BaseModel):
    descricao: str = ''
    tipo: str = ''
    advogado: str = ''
    observacoes: str = ''
    data_assinatura: str = ''
    status: str = 'Ativo'
    arquivo_path: str = ''


class ContratoResponse(ContratoCreate):
    id: int
    cliente_nome: str = ''
    created_at: str | None = None


# -- Contrato Clientes --

class ContratoClientesPayload(BaseModel):
    cliente_ids: list[int]


# -- Honorarios --

class HonorarioRow(BaseModel):
    tipo: str
    hipotese: str = ''
    valor: str = ''
    ordem: int = 0


class HonorariosPayload(BaseModel):
    honorarios: list[HonorarioRow]


class HonorarioResponse(HonorarioRow):
    id: int
    contrato_id: int


class HonorarioSearchResult(BaseModel):
    honorario_id: int
    tipo: str
    hipotese: str
    valor: str
    contrato_id: int
    ctt_n: str
    cliente_nome: str


# -- Parcelas --

class ParcelaRow(BaseModel):
    num: int
    valor: str = ''
    vencimento: str = ''
    nota_fiscal: str = ''
    data_pagamento: str = ''


class ParcelasPayload(BaseModel):
    parcelas: list[ParcelaRow]


class ParcelaResponse(BaseModel):
    id: int
    honorario_id: int
    num_parcela: int
    valor: str
    vencimento: str
    nota_fiscal: str
    data_pagamento: str


# -- Relatorio --

class RelatorioHonorario(BaseModel):
    id: int
    tipo: str
    hipotese: str
    valor: str
    ordem: int
    parcelas: list[ParcelaResponse]
    total_parcelas: int
    parcelas_pagas: int
    status_quitacao: str


class RelatorioResponse(BaseModel):
    contrato: ContratoResponse
    honorarios: list[RelatorioHonorario]
    clientes_extras: list[ClienteResponse]


# -- Inadimplentes --

class InadimplenteRow(BaseModel):
    parcela_id: int
    vencimento: str
    valor: str
    nota_fiscal: str
    honorario_id: int
    tipo: str
    hipotese: str
    contrato_id: int
    ctt_n: str
    cliente_id: int
    cliente_nome: str
