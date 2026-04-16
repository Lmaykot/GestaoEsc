import { useState, useEffect, useCallback } from 'react'
import { Modal, Button, Input } from '../../design-system/components'
import { honorariosApi } from '../../api/honorarios'
import { TIPO_ORDER, TIPO_LABELS } from '../../types'
import styles from './HonorariosDialog.module.css'

interface Row {
  hipotese: string
  valor: string
}

type Sections = Record<string, Row[]>

interface HonorariosDialogProps {
  open: boolean
  contratoId: number | null
  onClose: () => void
}

const emptyRow = (): Row => ({ hipotese: '', valor: '' })

const emptySections = (): Sections =>
  Object.fromEntries(TIPO_ORDER.map(t => [t, [emptyRow(), emptyRow()]]))

export function HonorariosDialog({ open, contratoId, onClose }: HonorariosDialogProps) {
  const [sections, setSections] = useState<Sections>(emptySections())
  const [saving, setSaving] = useState(false)

  const load = useCallback(async () => {
    if (!contratoId) return
    const honorarios = await honorariosApi.getByContrato(contratoId)
    const s = emptySections()
    for (const h of honorarios) {
      if (s[h.tipo]) {
        s[h.tipo].push({ hipotese: h.hipotese, valor: h.valor })
      }
    }
    for (const tipo of TIPO_ORDER) {
      s[tipo] = s[tipo].filter(r => r.hipotese || r.valor)
      if (s[tipo].length === 0) s[tipo] = [emptyRow(), emptyRow()]
    }
    setSections(s)
  }, [contratoId])

  useEffect(() => {
    if (open) load()
  }, [open, load])

  const updateRow = (tipo: string, idx: number, field: keyof Row, value: string) => {
    setSections(prev => ({
      ...prev,
      [tipo]: prev[tipo].map((r, i) => i === idx ? { ...r, [field]: value } : r),
    }))
  }

  const addRow = (tipo: string) => {
    setSections(prev => ({ ...prev, [tipo]: [...prev[tipo], emptyRow()] }))
  }

  const removeRow = (tipo: string, idx: number) => {
    setSections(prev => ({
      ...prev,
      [tipo]: prev[tipo].filter((_, i) => i !== idx),
    }))
  }

  const handleSave = async () => {
    if (!contratoId) return
    setSaving(true)
    try {
      const rows: { tipo: string; hipotese: string; valor: string; ordem: number }[] = []
      for (const tipo of TIPO_ORDER) {
        sections[tipo].forEach((r, i) => {
          if (r.hipotese.trim() || r.valor.trim()) {
            rows.push({ tipo, hipotese: r.hipotese, valor: r.valor, ordem: i })
          }
        })
      }
      await honorariosApi.replace(contratoId, rows)
      onClose()
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Cadastro de Honorários"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>Cancelar</Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? 'Salvando...' : 'Salvar Honorários'}
          </Button>
        </>
      }
    >
      {TIPO_ORDER.map(tipo => {
        const isMensal = tipo === 'mensais'
        return (
          <div key={tipo} className={styles.section}>
            <div className={styles.sectionTitle}>{TIPO_LABELS[tipo]}</div>
            <div className={styles.tableHeader}>
              <span className={styles.tableHeaderLabel}>
                {isMensal ? 'Vencimento Inicial' : 'Hipótese de Incidência'}
              </span>
              <span className={styles.tableHeaderLabel}>
                {isMensal ? 'Valor Mensal' : 'Valor'}
              </span>
              <span style={{ width: 32 }} />
            </div>
            <div className={styles.rowsContainer}>
              {sections[tipo]?.map((row, idx) => (
                <div key={idx} className={styles.row}>
                  <Input
                    type={isMensal ? 'date' : 'text'}
                    value={row.hipotese}
                    onChange={e => updateRow(tipo, idx, 'hipotese', e.target.value)}
                    placeholder={isMensal ? '' : 'Hipótese...'}
                  />
                  <Input
                    value={row.valor}
                    onChange={e => updateRow(tipo, idx, 'valor', e.target.value)}
                    placeholder="R$ 0,00"
                  />
                  <button className={styles.removeBtn} onClick={() => removeRow(tipo, idx)}>
                    &times;
                  </button>
                </div>
              ))}
            </div>
            <Button size="sm" variant="ghost" className={styles.addBtn} onClick={() => addRow(tipo)}>
              + Adicionar
            </Button>
          </div>
        )
      })}
    </Modal>
  )
}
