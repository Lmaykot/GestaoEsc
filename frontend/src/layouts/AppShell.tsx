import { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { useTheme } from '../contexts/ThemeContext'
import styles from './AppShell.module.css'
import logoSrc from '../assets/Logo.svg'

const NAV_ITEMS = [
  { to: '/clientes', icon: '👥', label: 'Clientes' },
  { to: '/contratos', icon: '📄', label: 'Contratos' },
  { to: '/pagamentos', icon: '💳', label: 'Pagamentos' },
  { to: '/relatorio', icon: '📊', label: 'Relatório' },
  { to: '/inadimplentes', icon: '⚠️', label: 'Inadimplentes' },
]

const MOBILE_NAV_ITEMS = [
  { to: '/contratos', icon: '📄', label: 'Contratos' },
  { to: '/pagamentos', icon: '💳', label: 'Pagamentos' },
  { to: '/relatorio', icon: '📊', label: 'Relatório' },
  { to: '/inadimplentes', icon: '⚠️', label: 'Inadimpl.' },
]

interface AppShellProps {
  children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
  const { theme, toggleTheme } = useTheme()

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.logo}>
          <img src={logoSrc} alt="20%" className={styles.logoImg} />
          <div className={styles.logoSub}>Gestor de contratos advocatícios</div>
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
        <div className={styles.sidebarFooter}>
          <button
            className={styles.themeToggle}
            onClick={toggleTheme}
            aria-label="Alternar tema"
            title={theme === 'light' ? 'Ativar modo escuro' : 'Ativar modo claro'}
          >
            <span className={styles.themeIcon}>{theme === 'light' ? '🌙' : '☀️'}</span>
            <span>{theme === 'light' ? 'Modo escuro' : 'Modo claro'}</span>
          </button>
        </div>
      </aside>

      <header className={styles.mobileHeader}>
        <img src={logoSrc} alt="20%" className={styles.mobileLogoImg} />
        <button
          className={styles.mobileThemeToggle}
          onClick={toggleTheme}
          aria-label="Alternar tema"
        >
          {theme === 'light' ? '🌙' : '☀️'}
        </button>
      </header>

      <main className={styles.content}>
        {children}
      </main>

      <nav className={styles.bottomNav}>
        {MOBILE_NAV_ITEMS.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `${styles.bottomNavItem} ${isActive ? styles.bottomNavActive : ''}`
            }
          >
            <span className={styles.bottomNavIcon}>{item.icon}</span>
            <span className={styles.bottomNavLabel}>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
