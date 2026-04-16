import { useState, useEffect, useCallback } from 'react'
import { clientesApi } from '../../api/clientes'
import { Card, Button, Input, TextArea, SearchInput, DataTable, SectionHeader } from '../../design-system/components'
import type { Column } from '../../design-system/components'
import type { Cliente } from '../../types'
import { useDebounce } from '../../hooks/useDebounce'
import styles from './CadastroCliente.module.css'

const EMPTY: Omit<Cliente, 'id' | 'created_at'> = {
  nome: '', cpf_cnpj: '', telefone: '', email: '',
  cep: '', logradouro: '', numero: '', complemento: '', cidade: '', estado: '',
  nome_representante: '', observacoes: '',
}

export function CadastroCliente() {
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search)
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [form, setForm] = useState(EMPTY)
  const [saving, setSaving] = useState(false)

  const loadList = useCallback(async () => {
    const data = await clientesApi.list(debouncedSearch)
    setClientes(data)
  }, [debouncedSearch])

  useEffect(() => { loadList() }, [loadList])

  const handleSelect = async (c: Cliente) => {
    setSelectedId(c.id)
    const full = await clientesApi.get(c.id)
    setForm({
      nome: full.nome, cpf_cnpj: full.cpf_cnpj, telefone: full.telefone,
      email: full.email, cep: full.cep, logradouro: full.logradouro,
      numero: full.numero, complemento: full.complemento, cidade: full.cidade,
      estado: full.estado, nome_representante: full.nome_representante,
      observacoes: full.observacoes,
    })
  }

  const handleNew = () => {
    setSelectedId(null)
    setForm(EMPTY)
  }

  const handleCancel = () => {
    setSelectedId(null)
    setForm(EMPTY)
  }

  const handleSave = async () => {
    if (!form.nome.trim()) return
    setSaving(true)
    try {
      if (selectedId) {
        await clientesApi.update(selectedId, form)
      } else {
        const created = await clientesApi.create(form)
        setSelectedId(created.id)
      }
      await loadList()
    } finally {
      setSaving(false)
    }
  }

  const field = (key: keyof typeof form, label: string) => (
    <Input
      label={label}
      value={form[key]}
      onChange={e => setForm(prev => ({ ...prev, [key]: e.target.value }))}
    />
  )

  const columns: Column<Cliente>[] = [
    { key: 'nome', header: 'Nome' },
    { key: 'cpf_cnpj', header: 'CPF/CNPJ', width: '140px' },
  ]

  return (
    <div>
      <h1 className={styles.pageTitle}>Cadastro de Clientes</h1>
      <div className={styles.page}>
        <div className={styles.listPanel}>
          <div className={styles.listHeader}>
            <SearchInput
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Buscar cliente..."
              style={{ flex: 1 }}
            />
            <Button size="sm" onClick={handleNew}>+ Novo</Button>
          </div>
          <Card flush className={styles.listScroll}>
            <DataTable
              columns={columns}
              data={clientes}
              rowKey={r => r.id}
              selectedKey={selectedId}
              onRowClick={handleSelect}
            />
          </Card>
        </div>

        <Card className={styles.formPanel}>
          <div className={styles.section}>
            <SectionHeader text="Dados Principais" />
            <div className={styles.formGrid}>
              <div className={styles.fullWidth}>{field('nome', 'Nome')}</div>
              {field('cpf_cnpj', 'CPF / CNPJ')}
              {field('telefone', 'Telefone')}
              {field('email', 'E-mail')}
            </div>
          </div>

          <div className={styles.section}>
            <SectionHeader text="Endereco" />
            <div className={styles.formGrid}>
              {field('cep', 'CEP')}
              <div className={styles.fullWidth}>{field('logradouro', 'Logradouro')}</div>
              {field('numero', 'Numero')}
              {field('complemento', 'Complemento')}
              {field('cidade', 'Cidade')}
              {field('estado', 'Estado')}
            </div>
          </div>

          <div className={styles.section}>
            <SectionHeader text="Representante Legal (PJ)" />
            <div className={styles.formGrid}>
              <div className={styles.fullWidth}>{field('nome_representante', 'Nome do Representante')}</div>
            </div>
          </div>

          <div className={styles.section}>
            <SectionHeader text="Observacoes" />
            <TextArea
              value={form.observacoes}
              onChange={e => setForm(prev => ({ ...prev, observacoes: e.target.value }))}
              rows={4}
            />
          </div>

          <div className={styles.actions}>
            <Button variant="secondary" onClick={handleCancel}>Cancelar</Button>
            <Button onClick={handleSave} disabled={saving || !form.nome.trim()}>
              {saving ? 'Salvando...' : 'Salvar Cadastro'}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}
