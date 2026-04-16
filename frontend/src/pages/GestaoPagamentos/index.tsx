import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { honorariosApi } from '../../api/honorarios'
import { parcelasApi } from '../../api/parcelas'
import { Card, Button, Input, SearchInput, SectionHeader } from '../../design-system/components'
import type { HonorarioSearchResult } from '../../types'
import { useDebounce } from '../../hooks/useDebounce'
import { TIPO_LABELS } from '../../types'
import styles from './GestaoPagamentos.module.css'

interface ParcelaForm {
  num: number
  valor: string
  vencimento: string
  nota_fiscal: string
  data_pagamento: string
}

interface TreeContract {
  contrato_id: number
  ctt_n: string
  cliente_nome: string
  honorarios: HonorarioSearchResult[]
}

export function GestaoPagamentos() {
  const [searchParams] = useSearchParams()
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search)
  const [tree, setTree] = useState<TreeContract[]>([])
  const [expanded, setExpanded] = useState<Set<number>>(new Set())
  const [selectedHId, setSelectedHId] = useState<number | null>(null)
  const [selectedInfo, setSelectedInfo] = useState<HonorarioSearchResult | null>(null)
  const [parcelas, setParcelas] = useState<ParcelaForm[]>([])
  const [saving, setSaving] = useState(false)

  const buildTree = (results: HonorarioSearchResult[]): TreeContract[] => {
    const map = new Map<number, TreeContract>()
    for (const r of results) {
      if (!map.has(r.contrato_id)) {
        map.set(r.contrato_id, {
          contrato_id: r.contrato_id, ctt_n: r.ctt_n,
          cliente_nome: r.cliente_nome, honorarios: [],
        })
      }
      map.get(r.contrato_id)!.honorarios.push(r)
    }
    return Array.from(map.values())
  }

  const loadTree = useCallback(async () => {
    const results = await honorariosApi.search(debouncedSearch)
    setTree(buildTree(results))
  }, [debouncedSearch])

  useEffect(() => { loadTree() }, [loadTree])

  useEffect(() => {
    const hid = searchParams.get('honorario_id')
    if (hid) {
      const id = parseInt(hid)
      loadHonorario(id)
    }
  }, [searchParams])

  const loadHonorario = async (hid: number) => {
    setSelectedHId(hid)
    const h = await honorariosApi.get(hid)
    const results = await honorariosApi.search('')
    const info = results.find(r => r.honorario_id === hid)
    setSelectedInfo(info || { honorario_id: hid, tipo: h.tipo, hipotese: h.hipotese, valor: h.valor, contrato_id: h.contrato_id, ctt_n: '', cliente_nome: '' })
    const parcelasData = await parcelasApi.get(hid)
    setParcelas(parcelasData.map(p => ({
      num: p.num_parcela, valor: p.valor, vencimento: p.vencimento,
      nota_fiscal: p.nota_fiscal, data_pagamento: p.data_pagamento,
    })))
    setExpanded(prev => {
      const next = new Set(prev)
      if (info) next.add(info.contrato_id)
      return next
    })
  }

  const toggleExpand = (id: number) => {
    setExpanded(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id); else next.add(id)
      return next
    })
  }

  const addParcela = () => {
    setParcelas(prev => [...prev, { num: prev.length + 1, valor: '', vencimento: '', nota_fiscal: '', data_pagamento: '' }])
  }

  const removeParcela = (idx: number) => {
    setParcelas(prev => prev.filter((_, i) => i !== idx).map((p, i) => ({ ...p, num: i + 1 })))
  }

  const updateParcela = (idx: number, field: keyof ParcelaForm, value: string) => {
    setParcelas(prev => prev.map((p, i) => i === idx ? { ...p, [field]: value } : p))
  }

  const handleSave = async () => {
    if (!selectedHId) return
    setSaving(true)
    try {
      await parcelasApi.save(selectedHId, parcelas)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <h1 className={styles.pageTitle}>Gestão de Pagamentos</h1>
      <div className={styles.page}>
        <div className={styles.treePanel}>
          <SearchInput
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Buscar por cliente ou contrato..."
          />
          <Card flush className={styles.treeScroll}>
            {tree.map(c => (
              <div key={c.contrato_id} className={styles.contractNode}>
                <div className={styles.contractHeader} onClick={() => toggleExpand(c.contrato_id)}>
                  <span className={`${styles.chevron} ${expanded.has(c.contrato_id) ? styles.chevronOpen : ''}`}>&#x25B6;</span>
                  {c.ctt_n} &mdash; {c.cliente_nome}
                </div>
                {expanded.has(c.contrato_id) && c.honorarios.map(h => (
                  <div
                    key={h.honorario_id}
                    className={`${styles.honorarioItem} ${selectedHId === h.honorario_id ? styles.selected : ''}`}
                    onClick={() => loadHonorario(h.honorario_id)}
                  >
                    {TIPO_LABELS[h.tipo] || h.tipo} &middot; R$ {h.valor} {h.hipotese && `| ${h.hipotese}`}
                  </div>
                ))}
              </div>
            ))}
            {tree.length === 0 && (
              <div className={styles.emptyDetail}>Nenhum honorário encontrado</div>
            )}
          </Card>
        </div>

        <Card className={styles.detailPanel}>
          {!selectedInfo ? (
            <div className={styles.emptyDetail}>Selecione um honorário na lista</div>
          ) : (
            <>
              <SectionHeader text="Informações" />
              <div className={styles.infoGrid}>
                <div>
                  <div className={styles.infoLabel}>Cliente</div>
                  <div className={styles.infoValue}>{selectedInfo.cliente_nome}</div>
                </div>
                <div>
                  <div className={styles.infoLabel}>CTT-N</div>
                  <div className={styles.infoValue}>{selectedInfo.ctt_n}</div>
                </div>
                <div>
                  <div className={styles.infoLabel}>Tipo</div>
                  <div className={styles.infoValue}>{TIPO_LABELS[selectedInfo.tipo] || selectedInfo.tipo}</div>
                </div>
                <div>
                  <div className={styles.infoLabel}>Hipótese</div>
                  <div className={styles.infoValue}>{selectedInfo.hipotese || '-'}</div>
                </div>
                <div>
                  <div className={styles.infoLabel}>Valor</div>
                  <div className={styles.infoValue}>R$ {selectedInfo.valor}</div>
                </div>
              </div>

              <SectionHeader text="Parcelas" />
              <div className={styles.parcelaHeader}>
                <span className={styles.parcelaHeaderLabel}>#</span>
                <span className={styles.parcelaHeaderLabel}>Valor</span>
                <span className={styles.parcelaHeaderLabel}>Vencimento</span>
                <span className={styles.parcelaHeaderLabel}>Nota Fiscal</span>
                <span className={styles.parcelaHeaderLabel}>Pagamento</span>
                <span style={{ width: 32 }} />
              </div>
              <div className={styles.parcelasTable}>
                {parcelas.map((p, idx) => (
                  <div key={idx} className={styles.parcelaRow}>
                    <span className={styles.parcelaNum}>{p.num}</span>
                    <Input value={p.valor} onChange={e => updateParcela(idx, 'valor', e.target.value)} placeholder="R$ 0,00" />
                    <Input type="date" value={p.vencimento} onChange={e => updateParcela(idx, 'vencimento', e.target.value)} />
                    <Input value={p.nota_fiscal} onChange={e => updateParcela(idx, 'nota_fiscal', e.target.value)} placeholder="NF" />
                    <Input type="date" value={p.data_pagamento} onChange={e => updateParcela(idx, 'data_pagamento', e.target.value)} />
                    <button className={styles.removeBtn} onClick={() => removeParcela(idx)}>&times;</button>
                  </div>
                ))}
              </div>

              <div className={styles.parcelaActions}>
                <Button size="sm" variant="ghost" onClick={addParcela}>+ Adicionar Parcela</Button>
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? 'Salvando...' : 'Salvar Parcelas'}
                </Button>
              </div>
            </>
          )}
        </Card>
      </div>
    </div>
  )
}
