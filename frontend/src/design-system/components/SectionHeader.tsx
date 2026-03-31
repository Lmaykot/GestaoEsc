import styles from './SectionHeader.module.css'

interface SectionHeaderProps {
  title: string
  icon?: string
  className?: string
}

export function SectionHeader({ title, icon, className = '' }: SectionHeaderProps) {
  return (
    <div className={`${styles.header} ${className}`}>
      {icon && <span className={styles.icon}>{icon}</span>}
      <h3 className={styles.title}>{title}</h3>
      <div className={styles.line} />
    </div>
  )
}
