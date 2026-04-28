import { Button } from '../../design-system/components/Button'
import { Card } from '../../design-system/components/Card'
import { useState } from 'react'
import styles from './Export.module.css'

interface ExportOption {
  id: string
  title: string
  description: string
  format: 'original' | 'xlsx'
}

const DATABASE_OPTIONS: ExportOption[] = [
  { id: 'db-sqlite', title: 'Banco SQLite', description: 'Exporta o banco de dados completo no formato SQLite (.db)', format: 'original' },
  { id: 'db-xlsx', title: 'Planilha Excel', description: 'Exporta os dados em formato Excel (.xlsx)', format: 'xlsx' },
]

const CONTRATOS_OPTIONS: ExportOption[] = [
  { id: 'contratos-zip', title: 'Arquivos ZIP', description: 'Baixa todos os arquivos de contrato compactados (.zip)', format: 'original' },
]

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function downloadFile(endpoint: string, filename: string) {
  const response = await fetch(`${API_BASE}${endpoint}`)
  if (!response.ok) {
    throw new Error('Erro ao baixar arquivo')
  }
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

export function Export() {
  const [loading, setLoading] = useState<string | null>(null)

  const handleExport = async (option: ExportOption) => {
    setLoading(option.id)
    try {
      if (option.id === 'db-sqlite') {
        await downloadFile('/api/export/db/sqlite', `gestao_contratos_${new Date().toISOString().split('T')[0]}.db`)
      } else if (option.id === 'db-xlsx') {
        await downloadFile('/api/export/db/xlsx', `gestao_contratos_${new Date().toISOString().split('T')[0]}.xlsx`)
      } else if (option.id === 'contratos-zip') {
        await downloadFile('/api/export/contratos/zip', `contratos_${new Date().toISOString().split('T')[0]}.zip`)
      }
    } catch (error) {
      console.error('Erro ao exportar:', error)
      alert('Erro ao exportar arquivo')
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Exportação</h1>
      <p className={styles.subtitle}>Exporte os dados do sistema em diferentes formatos</p>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Banco de Dados</h2>
        <p className={styles.sectionDescription}>Exporte todo o banco de dados do sistema</p>
        <div className={styles.grid}>
          {DATABASE_OPTIONS.map(option => (
            <Card key={option.id} className={styles.card}>
              <h3 className={styles.cardTitle}>{option.title}</h3>
              <p className={styles.cardDescription}>{option.description}</p>
              <Button
                onClick={() => handleExport(option)}
                disabled={loading === option.id}
              >
                {loading === option.id ? 'Baixando...' : 'Exportar'}
              </Button>
            </Card>
          ))}
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Arquivos de Contratos</h2>
        <p className={styles.sectionDescription}>Baixe os arquivos anexados aos contratos</p>
        <div className={styles.grid}>
          {CONTRATOS_OPTIONS.map(option => (
            <Card key={option.id} className={styles.card}>
              <h3 className={styles.cardTitle}>{option.title}</h3>
              <p className={styles.cardDescription}>{option.description}</p>
              <Button
                onClick={() => handleExport(option)}
                disabled={loading === option.id}
              >
                {loading === option.id ? 'Baixando...' : 'Exportar'}
              </Button>
            </Card>
          ))}
        </div>
      </section>
    </div>
  )
}