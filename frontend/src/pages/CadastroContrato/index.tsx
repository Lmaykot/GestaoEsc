import { useState, useEffect, useCallback, useRef } from 'react'
import { contratosApi } from '../../api/contratos'
import { clientesApi } from '../../api/clientes'
import { Card, Button, Input, TextArea, Select, SearchInput, DataTable, SectionHeader, StatusChip } from '../../design-system/components'
import type { Column } from '../../design-system/components'
import { HonorariosDialog } from '../HonorariosDialog/HonorariosDialog'
import type { Contrato, Cliente } from '../../types'
import { CONTRATO_TIPOS, CONTRATO_STATUS } from '../../types'
import { useDebounce } from '../../hooks/useDebounce'
import styles from './CadastroContrato.module.css'

const EMPTY_FORM = {
  ctt_n: '', descricao: '', tipo: 'Contencioso', advogado: '',
  observacoes: '', data_assinatura: '', status: 'Ativo', arquivo_path: '',
}

export function CadastroContrato() {
  const [contratos, setContratos] = useState<Contrato[]>([])
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search)
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [clienteId, setClienteId] = useState<number | null>(null)
  const [clienteNome, setClienteNome] = useState('')
  const [clienteResults, setClienteResults] = useState<Cliente[]>([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [extraClientes, setExtraClientes] = useState<Cliente[]>([])
  const [saving, setSaving] = useState(false)
  const [pdfError, setPdfError] = useState('')
  const [honorariosOpen, setHonorariosOpen] = useState(false)
  const [honorariosContratoId, setHonorariosContratoId] = useState<number | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const loadList = useCallback(async () => {
    const data = await contratosApi.list({ cliente_nome: debouncedSearch })
    setContratos(data)
  }, [debouncedSearch])

  useEffect(() => { loadList() }, [loadList])

  const handleSelect = async (c: Contrato) => {
    setSelectedId(c.id)
    const full = await contratosApi.get(c.id)
    setForm({
      ctt_n: full.ctt_n, descricao: full.descricao, tipo: full.tipo,
      advogado: full.advogado, observacoes: full.observacoes,
      data_assinatura: full.data_assinatura, status: full.status,
      arquivo_path: full.arquivo_path,
    })
    setClienteId(full.cliente_id)
    setClienteNome(full.cliente_nome)
    const extras = await contratosApi.getClientes(c.id)
    setExtraClientes(extras)
  }

  const handleNew = async () => {
    setSelectedId(null)
    const { ctt_n } = await contratosApi.nextCttN()
    setForm({ ...EMPTY_FORM, ctt_n })
    setClienteId(null)
    setClienteNome('')
    setExtraClientes([])
  }

  const handleCancel = () => {
    setSelectedId(null)
    setForm(EMPTY_FORM)
    setClienteId(null)
    setClienteNome('')
    setExtraClientes([])
  }

  const searchClientes = async (q: string) => {
    setClienteNome(q)
    if (q.length < 2) { setClienteResults([]); setShowDropdown(false); return }
    const results = await clientesApi.list(q)
    setClienteResults(results)
    setShowDropdown(true)
  }

  const pickCliente = (c: Cliente) => {
    setClienteId(c.id)
    setClienteNome(c.nome)
    setShowDropdown(false)
  }

  const addExtraCliente = async () => {
    const q = prompt('Nome do cliente adicional:')
    if (!q) return
    const results = await clientesApi.list(q)
    if (results.length > 0) {
      const c = results[0]
      if (!extraClientes.find(e => e.id === c.id) && c.id !== clienteId) {
        setExtraClientes(prev => [...prev, c])
      }
    }
  }

  const removeExtraCliente = (id: number) => {
    setExtraClientes(prev => prev.filter(c => c.id !== id))
  }

  const handleSave = async (advance = false) => {
    if (!form.ctt_n.trim() || !clienteId) return
    setSaving(true)
    try {
      let contratoId = selectedId
      if (selectedId) {
        await contratosApi.update(selectedId, {
          descricao: form.descricao, tipo: form.tipo, advogado: form.advogado,
          observacoes: form.observacoes, data_assinatura: form.data_assinatura,
          status: form.status, arquivo_path: form.arquivo_path,
        })
      } else {
        const created = await contratosApi.create({
          cliente_id: clienteId, ...form,
        })
        contratoId = created.id
        setSelectedId(created.id)
      }
      if (contratoId) {
        await contratosApi.setClientes(contratoId, extraClientes.map(c => c.id))
      }
      await loadList()
      if (advance && contratoId) {
        setHonorariosContratoId(contratoId)
        setHonorariosOpen(true)
      }
    } finally {
      setSaving(false)
    }
  }

  const handlePdfUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !selectedId) return
    setPdfError('')
    try {
      const result = await contratosApi.uploadPdf(selectedId, file)
      setForm(prev => ({ ...prev, arquivo_path: result.arquivo_path }))
    } catch (err) {
      setPdfError('Erro ao fazer upload do PDF. Tente novamente.')
    } finally {
      e.target.value = ''
    }
  }

  const handlePdfRemove = async () => {
    if (!selectedId) return
    await contratosApi.removePdf(selectedId)
    setForm(prev => ({ ...prev, arquivo_path: '' }))
  }

  const columns: Column<Contrato>[] = [
    { key: 'ctt_n', header: 'CTT-N', width: '120px' },
    { key: 'cliente_nome', header: 'Cliente' },
    { key: 'status', header: 'Status', width: '100px', render: (r) => <StatusChip status={r.status} /> },
  ]

  return (
    <div>
      <h1 className={styles.pageTitle}>Cadastro de Contratos</h1>
      <div className={styles.page}>
        <div className={styles.listPanel}>
          <div className={styles.listHeader}>
            <SearchInput
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Buscar contrato..."
              style={{ flex: 1 }}
            />
            <Button size="sm" onClick={handleNew}>+ Novo</Button>
          </div>
          <Card flush className={styles.listScroll}>
            <DataTable
              columns={columns}
              data={contratos}
              rowKey={r => r.id}
              selectedKey={selectedId}
              onRowClick={handleSelect}
            />
          </Card>
        </div>

        <Card className={styles.formPanel}>
          <div className={styles.section}>
            <SectionHeader text="Dados do Contrato" />
            <div className={styles.formGrid}>
              <Input label="CTT-N" value={form.ctt_n} readOnly />
              <Input
                label="Data de Assinatura"
                type="date"
                value={form.data_assinatura}
                onChange={e => setForm(prev => ({ ...prev, data_assinatura: e.target.value }))}
              />
              <Select
                label="Tipo"
                value={form.tipo}
                onChange={e => setForm(prev => ({ ...prev, tipo: e.target.value }))}
                options={CONTRATO_TIPOS.map(t => ({ value: t, label: t }))}
              />
              <div>
                <div className={styles.statusLabel}>Status</div>
                <div className={styles.statusGroup}>
                  {CONTRATO_STATUS.map(s => (
                    <label key={s} className={styles.statusOption}>
                      <input
                        type="radio" name="status" value={s}
                        checked={form.status === s}
                        onChange={() => setForm(prev => ({ ...prev, status: s }))}
                      />
                      <StatusChip status={s} />
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className={styles.section}>
            <SectionHeader text="Partes" />
            <div className={styles.clientePickerWrapper}>
              <Input
                label="Cliente Principal"
                value={clienteNome}
                onChange={e => searchClientes(e.target.value)}
                onFocus={() => clienteResults.length > 0 && setShowDropdown(true)}
                onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
                placeholder="Digite para buscar..."
              />
              {showDropdown && clienteResults.length > 0 && (
                <div className={styles.dropdown}>
                  {clienteResults.map(c => (
                    <div key={c.id} className={styles.dropdownItem} onMouseDown={() => pickCliente(c)}>
                      {c.nome} {c.cpf_cnpj && `- ${c.cpf_cnpj}`}
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div style={{ marginTop: 'var(--space-3)' }}>
              <Button size="sm" variant="ghost" onClick={addExtraCliente}>+ Adicionar cliente</Button>
              {extraClientes.length > 0 && (
                <div className={styles.chipList}>
                  {extraClientes.map(c => (
                    <span key={c.id} className={styles.extraChip}>
                      {c.nome}
                      <span className={styles.extraChipRemove} onClick={() => removeExtraCliente(c.id)}>&times;</span>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className={styles.section}>
            <SectionHeader text="Advogado" />
            <Input
              value={form.advogado}
              onChange={e => setForm(prev => ({ ...prev, advogado: e.target.value }))}
              placeholder="Nome do advogado responsável"
            />
          </div>

          <div className={styles.section}>
            <SectionHeader text="Objeto e Observações" />
            <TextArea
              label="Descrição"
              value={form.descricao}
              onChange={e => setForm(prev => ({ ...prev, descricao: e.target.value }))}
              rows={3}
            />
            <TextArea
              label="Observações"
              value={form.observacoes}
              onChange={e => setForm(prev => ({ ...prev, observacoes: e.target.value }))}
              rows={3}
              wrapperClassName={styles.fullWidth}
              style={{ marginTop: 'var(--space-4)' }}
            />
          </div>

          <div className={styles.section}>
            <SectionHeader text="Documento do Contrato" />
            <div className={styles.pdfRow}>
              {form.arquivo_path ? (
                <>
                  <span className={styles.pdfName}>{form.arquivo_path}</span>
                  {selectedId && (
                    <a
                      href={`/api/contratos/${selectedId}/pdf`}
                      download={form.arquivo_path}
                      className={styles.pdfDownloadLink}
                    >
                      Baixar PDF
                    </a>
                  )}
                  <Button size="sm" variant="ghost" onClick={handlePdfRemove}>Remover</Button>
                </>
              ) : (
                <>
                  <input type="file" accept=".pdf" ref={fileInputRef} style={{ display: 'none' }} onChange={handlePdfUpload} />
                  <Button size="sm" variant="secondary" onClick={() => fileInputRef.current?.click()} disabled={!selectedId}>
                    Anexar PDF
                  </Button>
                  {!selectedId && <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-on-surface-muted)' }}>Salve o contrato primeiro</span>}
                </>
              )}
            </div>
            {pdfError && <div style={{ color: 'var(--color-danger, red)', fontSize: 'var(--text-xs)', marginTop: 'var(--space-2)' }}>{pdfError}</div>}
          </div>

          <div className={styles.actions}>
            <Button variant="secondary" onClick={handleCancel}>Cancelar</Button>
            <Button variant="secondary" onClick={() => handleSave(false)} disabled={saving || !clienteId}>
              Salvar
            </Button>
            <Button onClick={() => handleSave(true)} disabled={saving || !clienteId}>
              {saving ? 'Salvando...' : 'Salvar e Avançar'}
            </Button>
          </div>
        </Card>
      </div>

      <HonorariosDialog
        open={honorariosOpen}
        contratoId={honorariosContratoId}
        onClose={() => setHonorariosOpen(false)}
      />
    </div>
  )
}
