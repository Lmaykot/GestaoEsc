import { InputHTMLAttributes } from 'react'
import styles from './SearchInput.module.css'

interface SearchInputProps extends InputHTMLAttributes<HTMLInputElement> {
  wrapperClassName?: string
}

export function SearchInput({ wrapperClassName = '', className = '', ...props }: SearchInputProps) {
  return (
    <div className={`${styles.wrapper} ${wrapperClassName}`}>
      <span className={styles.icon}>&#x1F50D;</span>
      <input
        type="text"
        className={`${styles.input} ${className}`}
        placeholder="Buscar..."
        {...props}
      />
    </div>
  )
}
