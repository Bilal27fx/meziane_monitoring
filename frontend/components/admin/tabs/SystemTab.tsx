'use client'

import { RefreshCw, Trash2, Edit, Plus, CheckCircle, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import Badge from '@/components/ui/Badge'

const USERS = [
  { id: 1, email: 'admin@meziane.fr', role: 'admin', is_active: true },
  { id: 2, email: 'agent@meziane.fr', role: 'agent', is_active: true },
  { id: 3, email: 'viewer@meziane.fr', role: 'viewer', is_active: false },
]

const INTEGRATIONS = [
  { name: 'Bridge API', key: 'BRIDGE_CLIENT_ID', statut: 'ok', description: 'Agrégation bancaire' },
  { name: 'Anthropic Claude', key: 'ANTHROPIC_API_KEY', statut: 'ok', description: 'Analyse IA' },
  { name: 'OpenAI', key: 'OPENAI_API_KEY', statut: 'error', description: 'Fallback LLM' },
  { name: 'SMTP', key: 'SMTP_HOST', statut: 'ok', description: 'Notifications email' },
  { name: 'Twilio', key: 'TWILIO_SID', statut: 'warning', description: 'SMS alertes' },
]

const ENV_VARS = [
  { key: 'ALLOWED_ORIGINS', value: 'http://localhost:3000', sensitive: false },
  { key: 'ENVIRONMENT', value: 'development', sensitive: false },
  { key: 'SECRET_KEY', value: '••••••••••••••••••••••••••••••••', sensitive: true },
]

const INFRA = [
  { name: 'PostgreSQL', version: '15.3', statut: 'ok', detail: '3 tables, 142 rows' },
  { name: 'Redis', version: '7.0', statut: 'ok', detail: '0 keys cached' },
  { name: 'MinIO', version: '2024-01', statut: 'ok', detail: '0 documents' },
  { name: 'Celery', version: '5.3', statut: 'ok', detail: '4 tasks registered' },
]

function IntegrationDot({ statut }: { statut: string }) {
  const c = statut === 'ok' ? '#22c55e' : statut === 'warning' ? '#eab308' : '#ef4444'
  return <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: c }} />
}

export default function SystemTab() {
  const roleVariant = (role: string) => {
    if (role === 'admin') return 'error' as const
    if (role === 'agent') return 'info' as const
    return 'default' as const
  }

  return (
    <div className="space-y-3">
      <h2 className="text-xs font-semibold text-white uppercase tracking-wider">Système</h2>

      <div className="grid grid-cols-2 gap-3">
        {/* Users */}
        <div className="bg-[#111111] border border-[#262626] rounded-md p-3">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] text-[#737373] uppercase tracking-wide">Utilisateurs</span>
            <button className="flex items-center gap-1 h-6 px-2 bg-white text-black text-[9px] font-medium rounded hover:bg-[#e5e5e5] transition-colors">
              <Plus className="h-2.5 w-2.5" />
              Ajouter
            </button>
          </div>
          <div className="space-y-2">
            {USERS.map((u) => (
              <div key={u.id} className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-white">{u.email}</p>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <Badge variant={roleVariant(u.role)}>{u.role}</Badge>
                    {!u.is_active && <Badge variant="default">Inactif</Badge>}
                  </div>
                </div>
                <div className="flex gap-1">
                  <button className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors">
                    <Edit className="h-3 w-3" />
                  </button>
                  <button className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#ef4444] hover:bg-[#ef4444]/10 transition-colors">
                    <Trash2 className="h-3 w-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Integrations */}
        <div className="bg-[#111111] border border-[#262626] rounded-md p-3">
          <span className="text-[10px] text-[#737373] uppercase tracking-wide block mb-3">Intégrations</span>
          <div className="space-y-2">
            {INTEGRATIONS.map((integ) => (
              <div key={integ.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <IntegrationDot statut={integ.statut} />
                  <div>
                    <p className="text-xs text-white">{integ.name}</p>
                    <p className="text-[9px] text-[#525252]">{integ.description}</p>
                  </div>
                </div>
                <button
                  onClick={() => toast.success(`Test ${integ.name} — OK`)}
                  className="h-6 px-2 text-[9px] text-[#737373] bg-[#1a1a1a] hover:bg-[#262626] rounded transition-colors"
                >
                  Test
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Env vars */}
        <div className="bg-[#111111] border border-[#262626] rounded-md p-3">
          <span className="text-[10px] text-[#737373] uppercase tracking-wide block mb-3">Variables d'environnement</span>
          <div className="space-y-2">
            {ENV_VARS.map((v) => (
              <div key={v.key} className="flex items-center justify-between">
                <div>
                  <p className="text-[9px] font-mono text-[#a3a3a3]">{v.key}</p>
                  <p className="text-[10px] font-mono text-[#525252]">{v.value}</p>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => toast.success(`${v.key} modifié`)} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors">
                    <Edit className="h-3 w-3" />
                  </button>
                  {v.sensitive && (
                    <button onClick={() => toast.success(`${v.key} régénéré`)} className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#eab308] hover:bg-[#eab308]/10 transition-colors">
                      <RefreshCw className="h-3 w-3" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Infrastructure */}
        <div className="bg-[#111111] border border-[#262626] rounded-md p-3">
          <span className="text-[10px] text-[#737373] uppercase tracking-wide block mb-3">Infrastructure</span>
          <div className="space-y-2">
            {INFRA.map((svc) => (
              <div key={svc.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <IntegrationDot statut={svc.statut} />
                  <div>
                    <p className="text-xs text-white">{svc.name} <span className="text-[9px] text-[#525252]">v{svc.version}</span></p>
                    <p className="text-[9px] text-[#525252]">{svc.detail}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="flex gap-2 mt-4 pt-3 border-t border-[#262626]">
            <button onClick={() => toast.success('Cache Redis vidé')} className="flex items-center gap-1 h-6 px-2 text-[9px] text-[#737373] bg-[#1a1a1a] hover:bg-[#262626] rounded transition-colors">
              <Trash2 className="h-2.5 w-2.5" />
              Vider cache Redis
            </button>
            <button onClick={() => toast.success('Index relancé')} className="flex items-center gap-1 h-6 px-2 text-[9px] text-[#737373] bg-[#1a1a1a] hover:bg-[#262626] rounded transition-colors">
              <RefreshCw className="h-2.5 w-2.5" />
              Relancer index
            </button>
          </div>
        </div>
      </div>

      {/* Export buttons */}
      <div className="flex gap-2">
        {['CSV', 'JSON'].map((fmt) => (
          <button
            key={fmt}
            onClick={() => toast.success(`Export ${fmt} en cours...`)}
            className="h-7 px-3 text-xs text-[#737373] bg-[#111111] border border-[#262626] rounded hover:bg-[#1a1a1a] transition-colors"
          >
            Exporter {fmt}
          </button>
        ))}
      </div>
    </div>
  )
}
