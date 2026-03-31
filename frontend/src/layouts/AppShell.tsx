import { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import styles from './AppShell.module.css'

const NAV_ITEMS = [
  { to: '/clientes', icon: '\u{1F465}', label: 'Clientes' },
  { to: '/contratos', icon: '\u{1F4C4}', label: 'Contratos' },
  { to: '/pagamentos', icon: '\u{1F4B3}', label: 'Pagamentos' },
  { to: '/relatorio', icon: '\u{1F4CA}', label: 'Relatorio' },
]

interface AppShellProps {
  children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.logo}>
          <div className={styles.logoTitle}>GestaoEsc</div>
          <div className={styles.logoSub}>Gestao de Contratos</div>
        </div>
        <nav className={styles.nav}>
          {NAV_ITEMS.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `${styles.navLink} ${isActive ? styles.active : ''}`
              }
            >
              <span className={styles.navIcon}>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className={styles.content}>
        {children}
      </main>
    </div>
  )
}
