import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../api/client'
import { Card } from '../../design-system/components'
import type { InadimplenteRow } from '../../types'
import { TIPO_LABELS } from '../../types'
import styles from './Inadimplentes.module.css'

export function Inadimplentes() {
  const navigate = useNavigate()
  const [rows, setRows] = useState<InadimplenteRow[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<InadimplenteRow[]>('/relatorio/inadimplentes')
      .then(setRows)
      .finally(() => setLoading(false))
  }, [])

  const formatDate = (d: string) => {
    if (!d) return '-'
    const [y, m, day] = d.split('-')
    return `${day}/${m}/${y}`
  }

  const handleGerir = (honorarioId: number) => {
    navigate(`/pagamentos?honorario_id=${honorarioId}`)
  }

  return (
    <div>
      <h1 className={styles.pageTitle}>Inadimplentes</h1>

      {/* Desktop: tabela */}
      <Card className={styles.card}>
        {loading ? (
          <div className={styles.empty}>Carregando...</div>
        ) : rows.length === 0 ? (
          <div className={styles.empty}>Nenhuma parcela em atraso encontrada.</div>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>CTT-N</th>
                <th>Cliente</th>
                <th>Tipo de Honorário</th>
                <th>Hipótese</th>
                <th>Vencimento</th>
                <th>Nota Fiscal</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {rows.map(r => (
                <tr key={r.parcela_id}>
                  <td className={styles.cttN}>{r.ctt_n}</td>
                  <td>{r.cliente_nome}</td>
                  <td>{TIPO_LABELS[r.tipo] || r.tipo}</td>
                  <td className={styles.hipotese}>{r.hipotese || '-'}</td>
                  <td className={styles.vencimento}>{formatDate(r.vencimento)}</td>
                  <td>{r.nota_fiscal || '—'}</td>
                  <td>
                    <span
                      className={styles.gerirLink}
                      onClick={() => handleGerir(r.honorario_id)}
                    >
                      Gerir
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      {/* Mobile: cards */}
      {loading ? (
        <div className={`${styles.mobileList}`}>
          <div className={styles.empty}>Carregando...</div>
        </div>
      ) : rows.length === 0 ? (
        <div className={styles.mobileList}>
          <div className={styles.empty}>Nenhuma parcela em atraso.</div>
        </div>
      ) : (
        <div className={styles.mobileList}>
          {rows.map(r => (
            <div key={r.parcela_id} className={styles.mobileCard}>
              <div className={styles.mobileCardHeader}>
                <span className={styles.mobileCttN}>{r.ctt_n}</span>
                <span className={styles.mobileVencimento}>{formatDate(r.vencimento)}</span>
              </div>
              <div className={styles.mobileCliente}>{r.cliente_nome}</div>
              <div className={styles.mobileTipo}>{TIPO_LABELS[r.tipo] || r.tipo}</div>
              {r.hipotese && (
                <div className={styles.mobileHipotese}>{r.hipotese}</div>
              )}
              <button
                className={styles.mobileGerirBtn}
                onClick={() => handleGerir(r.honorario_id)}
              >
                Gerir pagamento →
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
