import styles from './SectionHeader.module.css'

interface SectionHeaderProps {
  icon?: string
  text: string
  showLine?: boolean
}

export function SectionHeader({ icon, text, showLine = true }: SectionHeaderProps) {
  return (
    <div className={styles.header}>
      {icon && <span className={styles.icon}>{icon}</span>}
      <span className={styles.text}>{text}</span>
      {showLine && <div className={styles.line} />}
    </div>
  )
}
