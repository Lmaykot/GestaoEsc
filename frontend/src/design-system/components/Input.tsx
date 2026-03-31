import { InputHTMLAttributes, TextareaHTMLAttributes } from 'react'
import styles from './Input.module.css'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  wrapperClassName?: string
}

export function Input({ label, wrapperClassName = '', className = '', ...props }: InputProps) {
  return (
    <div className={`${styles.wrapper} ${wrapperClassName}`}>
      {label && <label className={styles.label}>{label}</label>}
      <input className={`${styles.input} ${className}`} {...props} />
    </div>
  )
}

interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  wrapperClassName?: string
}

export function TextArea({ label, wrapperClassName = '', className = '', ...props }: TextAreaProps) {
  return (
    <div className={`${styles.wrapper} ${wrapperClassName}`}>
      {label && <label className={styles.label}>{label}</label>}
      <textarea className={`${styles.input} ${styles.textarea} ${className}`} {...props} />
    </div>
  )
}
