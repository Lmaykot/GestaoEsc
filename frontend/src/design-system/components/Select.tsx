import { SelectHTMLAttributes } from 'react'
import styles from './Select.module.css'

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  options: { value: string; label: string }[]
  wrapperClassName?: string
}

export function Select({ label, options, wrapperClassName = '', className = '', ...props }: SelectProps) {
  return (
    <div className={`${styles.wrapper} ${wrapperClassName}`}>
      {label && <label className={styles.label}>{label}</label>}
      <select className={`${styles.select} ${className}`} {...props}>
        {options.map(o => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  )
}
