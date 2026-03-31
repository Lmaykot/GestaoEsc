import { HTMLAttributes, ReactNode } from 'react'
import styles from './Card.module.css'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean
  compact?: boolean
  flush?: boolean
  children: ReactNode
}

export function Card({ hoverable, compact, flush, className = '', children, ...props }: CardProps) {
  const classes = [
    styles.card,
    hoverable ? styles.hoverable : '',
    compact ? styles.compact : '',
    flush ? styles.flush : '',
    className,
  ].filter(Boolean).join(' ')

  return <div className={classes} {...props}>{children}</div>
}
