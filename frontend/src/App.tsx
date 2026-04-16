import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppShell } from './layouts/AppShell'
import { CadastroCliente } from './pages/CadastroCliente'
import { CadastroContrato } from './pages/CadastroContrato'
import { GestaoPagamentos } from './pages/GestaoPagamentos'
import { Relatorio } from './pages/Relatorio'
import { Inadimplentes } from './pages/Inadimplentes'

export default function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/clientes" element={<CadastroCliente />} />
          <Route path="/contratos" element={<CadastroContrato />} />
          <Route path="/pagamentos" element={<GestaoPagamentos />} />
          <Route path="/relatorio" element={<Relatorio />} />
          <Route path="/inadimplentes" element={<Inadimplentes />} />
          <Route path="*" element={<Navigate to="/clientes" replace />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}
