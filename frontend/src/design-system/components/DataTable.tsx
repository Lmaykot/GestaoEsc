import { ReactNode } from 'react'
import styles from './DataTable.module.css'

interface Column<T> {
  key: string
  header: string
  render?: (row: T) => ReactNode
  width?: string
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  onRowClick?: (row: T) => void
  selectedId?: number | null
  idKey?: string
  emptyMessage?: string
  className?: string
}

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  onRowClick,
  selectedId,
  idKey = 'id',
  emptyMessage = 'Nenhum registro encontrado',
  className = '',
}: DataTableProps<T>) {
  return (
    <div className={`${styles.wrapper} ${className}`}>
      <table className={styles.table}>
        <thead>
          <tr>
            {columns.map(col => (
              <th key={col.key} style={col.width ? { width: col.width } : undefined}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className={styles.empty}>
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr
                key={(row[idKey] as number) ?? i}
                className={[
                  onRowClick ? styles.clickable : '',
                  selectedId != null && row[idKey] === selectedId ? styles.selected : '',
                ].filter(Boolean).join(' ')}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map(col => (
                  <td key={col.key}>
                    {col.render ? col.render(row) : String(row[col.key] ?? '')}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
