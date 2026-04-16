import { api } from './client'
import type { Contrato, Cliente } from '../types'

export const contratosApi = {
  list: (params: { cliente_nome?: string; numero?: string } = {}) => {
    const sp = new URLSearchParams()
    if (params.cliente_nome) sp.set('cliente_nome', params.cliente_nome)
    if (params.numero) sp.set('numero', params.numero)
    const qs = sp.toString()
    return api.get<Contrato[]>(`/contratos${qs ? `?${qs}` : ''}`)
  },
  get: (id: number) => api.get<Contrato>(`/contratos/${id}`),
  create: (data: Omit<Contrato, 'id' | 'created_at' | 'cliente_nome'>) => api.post<Contrato>('/contratos', data),
  update: (id: number, data: { descricao: string; tipo: string; advogado: string; observacoes: string; data_assinatura: string; status: string; arquivo_path: string }) =>
    api.put<Contrato>(`/contratos/${id}`, data),
  nextCttN: () => api.get<{ ctt_n: string }>('/contratos/next-ctt-n'),
  getClientes: (id: number) => api.get<Cliente[]>(`/contratos/${id}/clientes`),
  setClientes: (id: number, cliente_ids: number[]) => api.put<{ ok: boolean }>(`/contratos/${id}/clientes`, { cliente_ids }),
  uploadPdf: (id: number, file: File) => api.upload<{ arquivo_path: string }>(`/contratos/${id}/pdf`, file),
  removePdf: (id: number) => api.del<{ ok: boolean }>(`/contratos/${id}/pdf`),
}
