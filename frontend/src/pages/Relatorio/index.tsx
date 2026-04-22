import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { contratosApi } from '../../api/contratos'
import { honorariosApi } from '../../api/honorarios'
import { Card, SearchInput, DataTable, SectionHeader, StatusChip } from '../../design-system/components'
import type { Column } from '../../design-system/components'
import type { Contrato, Relatorio as RelatorioType, RelatorioHonorario } from '../../types'
import { TIPO_ORDER, TIPO_LABELS } from '../../types'
import { useDebounce } from '../../hooks/useDebounce'
import styles from './Relatorio.module.css'

const DESCRICAO_LIMIT = 160

function DescricaoBlock({ descricao }: { descricao: string }) {
  const [expanded, setExpanded] = useState(false)
  const isLong = descricao.length > DESCRICAO_LIMIT
  const shown = expanded || !isLong ? descricao : `${descricao.slice(0, DESCRICAO_LIMIT).trim()}…`
  return (
    <div className={styles.descricaoValue}>
      {shown}
      {isLong && (
        <button
          className={styles.readMoreBtn}
          onClick={() => setExpanded(v => !v)}
          type="button"
        >
          {expanded ? 'Mostrar menos' : 'Leia mais'}
        </button>
      )}
    </div>
  )
}

export function Relatorio() {
  const navigate = useNavigate()
  const [contratos, setContratos] = useState<Contrato[]>([])
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search)
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [relatorio, setRelatorio] = useState<RelatorioType | null>(null)
  const [mobileShowDetail, setMobileShowDetail] = useState(false)

  const loadList = useCallback(async () => {
    const [byCliente, byNumero] = await Promise.all([
      contratosApi.list({ cliente_nome: debouncedSearch }),
      debouncedSearch
        ? contratosApi.list({ numero: debouncedSearch })
        : Promise.resolve([] as Contrato[]),
    ])
    const seen = new Set<number>()
    const merged: Contrato[] = []
    for (const c of [...byCliente, ...byNumero]) {
      if (!seen.has(c.id)) {
        seen.add(c.id)
        merged.push(c)
      }
    }
    setContratos(merged)
  }, [debouncedSearch])

  useEffect(() => { loadList() }, [loadList])

  const handleSelect = async (c: Contrato) => {
    setSelectedId(c.id)
    const data = await honorariosApi.getRelatorio(c.id)
    setRelatorio(data)
    setMobileShowDetail(true)
  }

  const handleMobileBack = () => {
    setMobileShowDetail(false)
    setSelectedId(null)
    setRelatorio(null)
  }

  const handleGerir = (honorarioId: number) => {
    navigate(`/pagamentos?honorario_id=${honorarioId}`)
  }

  const groupedHonorarios = relatorio
    ? TIPO_ORDER
        .map(tipo => ({
          tipo,
          items: relatorio.honorarios.filter(h => h.tipo === tipo),
        }))
        .filter(g => g.items.length > 0)
    : []

  const getParcelamentoLabel = (h: RelatorioHonorario) => {
    if (h.total_parcelas === 0) return 'Não definido'
    if (h.total_parcelas === 1) return 'À vista'
    return `${h.total_parcelas} parcelas`
  }

  const getQuitacaoClass = (status: string) => {
    if (status === 'Quitado') return styles.quitacaoQuitado
    if (status === 'Pendente') return styles.quitacaoPendente
    return styles.quitacaoParcial
  }

  const columns: Column<Contrato>[] = [
    { key: 'ctt_n', header: 'CTT-N', width: '120px' },
    { key: 'cliente_nome', header: 'Cliente' },
  ]

  return (
    <div>
      <h1 className={styles.pageTitle}>Relatório de Gestão</h1>
      <div className={styles.page}>
        <div className={`${styles.listPanel} ${mobileShowDetail ? styles.mobileHidden : ''}`}>
          <div className={styles.searchFields}>
            <SearchInput
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Buscar por cliente ou contrato..."
            />
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

        <Card className={`${styles.detailPanel} ${mobileShowDetail ? styles.mobileVisible : ''}`}>
          {mobileShowDetail && (
            <button className={styles.mobileBackBtn} onClick={handleMobileBack}>
              ← Voltar
            </button>
          )}
          {!relatorio ? (
            <div className={styles.emptyDetail}>Selecione um contrato na lista</div>

          ) : (
            <>
              <div className={styles.reportHeader}>
                <div>
                  <div className={styles.reportClientName}>{relatorio.contrato.cliente_nome}</div>
                  <div className={styles.reportCttN}>{relatorio.contrato.ctt_n}</div>
                </div>
                <StatusChip status={relatorio.contrato.status} />
              </div>

              <div className={styles.reportMeta}>
                <div>
                  <div className={styles.metaLabel}>Tipo</div>
                  <div className={styles.metaValue}>{relatorio.contrato.tipo || '-'}</div>
                </div>
                <div>
                  <div className={styles.metaLabel}>Advogado</div>
                  <div className={styles.metaValue}>{relatorio.contrato.advogado || '-'}</div>
                </div>
                <div style={{ gridColumn: '1 / -1' }}>
                  <div className={styles.metaLabel}>Descrição</div>
                  <DescricaoBlock descricao={relatorio.contrato.descricao || '-'} />
                </div>
                {relatorio.contrato.observacoes && (
                  <div style={{ gridColumn: '1 / -1' }}>
                    <div className={styles.metaLabel}>Observações</div>
                    <div className={styles.metaValue}>{relatorio.contrato.observacoes}</div>
                  </div>
                )}
                {relatorio.contrato.arquivo_path && selectedId && (
                  <div>
                    <div className={styles.metaLabel}>Documento</div>
                    <a
                      href={`/api/contratos/${selectedId}/pdf`}
                      download={relatorio.contrato.arquivo_path}
                      className={styles.pdfLink}
                    >
                      ⬇ Baixar PDF
                    </a>
                  </div>
                )}
              </div>

              {groupedHonorarios.map(group => (
                <div key={group.tipo} className={styles.honorarioSection}>
                  <SectionHeader text={TIPO_LABELS[group.tipo]} />
                  <table className={styles.honorarioTable}>
                    <colgroup>
                      <col className={styles.colHipotese} />
                      <col className={styles.colValor} />
                      <col className={styles.colGerir} />
                      <col className={styles.colParcelamento} />
                      <col className={styles.colQuitacao} />
                    </colgroup>
                    <thead>
                      <tr>
                        <th>Hipótese</th>
                        <th>Valor</th>
                        <th></th>
                        <th>Parcelamento</th>
                        <th>Quitação</th>
                      </tr>
                    </thead>
                    <tbody>
                      {group.items.map(h => (
                        <tr key={h.id}>
                          <td>{h.hipotese || '-'}</td>
                          <td>R$ {h.valor}</td>
                          <td>
                            <span className={styles.gerirLink} onClick={() => handleGerir(h.id)}>
                              Gerir
                            </span>
                          </td>
                          <td>{getParcelamentoLabel(h)}</td>
                          <td>
                            <span className={`${styles.quitacao} ${getQuitacaoClass(h.status_quitacao)}`}>
                              {h.status_quitacao}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}

              {groupedHonorarios.length === 0 && (
                <div className={styles.emptyDetail}>Nenhum honorário cadastrado</div>
              )}
            </>
          )}
        </Card>
      </div>
    </div>
  )
}
