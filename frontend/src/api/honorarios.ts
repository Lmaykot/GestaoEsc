import { api } from './client'
import type { Honorario, HonorarioSearchResult, Relatorio } from '../types'

export const honorariosApi = {
  getByContrato: (contratoId: number) => api.get<Honorario[]>(`/contratos/${contratoId}/honorarios`),
  replace: (contratoId: number, honorarios: { tipo: string; hipotese: string; valor: string; ordem: number }[]) =>
    api.put<{ ok: boolean }>(`/contratos/${contratoId}/honorarios`, { honorarios }),
  search: (q = '') => api.get<HonorarioSearchResult[]>(`/honorarios/search?q=${encodeURIComponent(q)}`),
  get: (id: number) => api.get<Honorario>(`/honorarios/${id}`),
  getRelatorio: (contratoId: number) => api.get<Relatorio>(`/relatorio/${contratoId}`),
}
