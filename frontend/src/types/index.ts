export interface Cliente {
  id: number
  nome: string
  cpf_cnpj: string
  telefone: string
  email: string
  cep: string
  logradouro: string
  numero: string
  complemento: string
  cidade: string
  estado: string
  nome_representante: string
  observacoes: string
  created_at?: string
}

export interface Contrato {
  id: number
  cliente_id: number
  ctt_n: string
  descricao: string
  tipo: string
  advogado: string
  observacoes: string
  data_assinatura: string
  status: string
  arquivo_path: string
  cliente_nome: string
  created_at?: string
}

export interface Honorario {
  id: number
  contrato_id: number
  tipo: string
  hipotese: string
  valor: string
  ordem: number
}

export interface HonorarioSearchResult {
  honorario_id: number
  tipo: string
  hipotese: string
  valor: string
  contrato_id: number
  ctt_n: string
  cliente_nome: string
}

export interface Parcela {
  id: number
  honorario_id: number
  num_parcela: number
  valor: string
  vencimento: string
  nota_fiscal: string
  data_pagamento: string
}

export interface RelatorioHonorario extends Honorario {
  parcelas: Parcela[]
  total_parcelas: number
  parcelas_pagas: number
  status_quitacao: string
}

export interface Relatorio {
  contrato: Contrato
  honorarios: RelatorioHonorario[]
  clientes_extras: Cliente[]
}

export type HonorarioTipo = 'inicial' | 'condicionado' | 'intermediario' | 'exito' | 'mensais'

export const TIPO_LABELS: Record<string, string> = {
  inicial: 'Honorários Iniciais',
  condicionado: 'Honorários Condicionados',
  intermediario: 'Honorários Intermediários',
  exito: 'Honorários de Êxito',
  mensais: 'Honorários Mensais',
}

export const TIPO_ORDER: HonorarioTipo[] = ['inicial', 'condicionado', 'intermediario', 'exito', 'mensais']

export const CONTRATO_TIPOS = ['Contencioso', 'Consultoria', 'Licenciamento', 'Misto']
export const CONTRATO_STATUS = ['Ativo', 'Encerrado', 'Quitado']

export interface InadimplenteRow {
  parcela_id: number
  vencimento: string
  valor: string
  nota_fiscal: string
  honorario_id: number
  tipo: string
  hipotese: string
  contrato_id: number
  ctt_n: string
  cliente_id: number
  cliente_nome: string
}
