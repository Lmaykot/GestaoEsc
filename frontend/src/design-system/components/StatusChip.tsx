import styles from './StatusChip.module.css'

interface StatusChipProps {
  status: string
  className?: string
}

const STATUS_MAP: Record<string, string> = {
  'Ativo': 'ativo',
  'Encerrado': 'encerrado',
  'Quitado': 'quitado',
  'Pendente': 'pendente',
}

export function StatusChip({ status, className = '' }: StatusChipProps) {
  const variant = STATUS_MAP[status] || 'default'
  return (
    <span className={`${styles.chip} ${styles[variant]} ${className}`}>
      {status}
    </span>
  )
}
