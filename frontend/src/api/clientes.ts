import { api } from './client'
import type { Cliente } from '../types'

export const clientesApi = {
  list: (q = '') => api.get<Cliente[]>(`/clientes${q ? `?q=${encodeURIComponent(q)}` : ''}`),
  get: (id: number) => api.get<Cliente>(`/clientes/${id}`),
  create: (data: Omit<Cliente, 'id' | 'created_at'>) => api.post<Cliente>('/clientes', data),
  update: (id: number, data: Omit<Cliente, 'id' | 'created_at'>) => api.put<Cliente>(`/clientes/${id}`, data),
}
