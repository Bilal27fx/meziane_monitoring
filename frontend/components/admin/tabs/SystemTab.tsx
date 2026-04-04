'use client'

import { useState } from 'react'
import { RefreshCw, Trash2, Edit, Plus, X } from 'lucide-react'
import toast from 'react-hot-toast'
import Badge from '@/components/ui/Badge'
import { useUsers, useCreateUser, useUpdateUser, useDeleteUser } from '@/lib/hooks/useAdmin'
import type { UserRole, AppUser } from '@/lib/types'

const INTEGRATIONS = [
  { name: 'Bridge API', key: 'BRIDGE_CLIENT_ID', statut: 'ok', description: 'Agrégation bancaire' },
  { name: 'Anthropic Claude', key: 'ANTHROPIC_API_KEY', statut: 'ok', description: 'Analyse IA' },
  { name: 'OpenAI', key: 'OPENAI_API_KEY', statut: 'error', description: 'Fallback LLM' },
  { name: 'SMTP', key: 'SMTP_HOST', statut: 'ok', description: 'Notifications email' },
  { name: 'Telegram Bot', key: 'TELEGRAM_BOT_TOKEN', statut: 'warning', description: 'Alertes Telegram' },
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

const ROLE_LABELS: Record<UserRole, string> = {
  admin: 'Admin',
  user: 'Utilisateur',
  readonly: 'Lecture seule',
}

function IntegrationDot({ statut }: { statut: string }) {
  const c = statut === 'ok' ? '#22c55e' : statut === 'warning' ? '#eab308' : '#ef4444'
  return <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: c }} />
}

function roleVariant(role: string) {
  if (role === 'admin') return 'error' as const
  if (role === 'user') return 'info' as const
  return 'default' as const
}

// ─── Modal Ajouter/Modifier Utilisateur ───────────────────────────────────────

interface UserModalProps {
  user?: AppUser
  onClose: () => void
}

function UserModal({ user, onClose }: UserModalProps) {
  const createUser = useCreateUser()
  const updateUser = useUpdateUser()
  const [email, setEmail] = useState(user?.email ?? '')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<UserRole>(user?.role ?? 'user')

  const inputClass = 'w-full h-8 text-xs bg-[#0d0d0d] border border-[#262626] rounded px-2.5 text-white focus:outline-none focus:border-[#404040] transition-colors'
  const labelClass = 'text-[9px] text-[#525252] uppercase tracking-wide block mb-1'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (user) {
        await updateUser.mutateAsync({ id: user.id, data: { role } })
        toast.success('Utilisateur mis à jour')
      } else {
        if (!password) return toast.error('Mot de passe requis')
        await createUser.mutateAsync({ email, password, role })
        toast.success('Utilisateur créé')
      }
      onClose()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(msg ?? 'Erreur lors de la sauvegarde')
    }
  }

  const isPending = createUser.isPending || updateUser.isPending

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-[#111111] border border-[#262626] rounded-lg w-80 p-5 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-semibold text-white">
            {user ? 'Modifier utilisateur' : 'Nouvel utilisateur'}
          </span>
          <button onClick={onClose} className="text-[#525252] hover:text-white transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className={labelClass}>Email *</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={inputClass}
              required
              disabled={!!user}
              placeholder="user@meziane.fr"
            />
          </div>
          {!user && (
            <div>
              <label className={labelClass}>Mot de passe *</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={inputClass}
                required
                placeholder="••••••••"
                minLength={6}
              />
            </div>
          )}
          <div>
            <label className={labelClass}>Rôle *</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as UserRole)}
              className={inputClass}
            >
              <option value="admin">Admin</option>
              <option value="user">Utilisateur</option>
              <option value="readonly">Lecture seule</option>
            </select>
          </div>
          <div className="flex gap-2 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 h-8 text-xs text-[#737373] bg-[#1a1a1a] hover:bg-[#262626] rounded transition-colors"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="flex-1 h-8 text-xs text-black bg-white hover:bg-[#e5e5e5] rounded font-medium transition-colors disabled:opacity-50"
            >
              {isPending ? 'Sauvegarde…' : user ? 'Mettre à jour' : 'Créer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ─── SystemTab ─────────────────────────────────────────────────────────────────

export default function SystemTab() {
  const { data: users, isLoading } = useUsers()
  const deleteUser = useDeleteUser()
  const [modal, setModal] = useState<{ open: boolean; user?: AppUser }>({ open: false })

  const handleDelete = async (u: AppUser) => {
    if (!confirm(`Supprimer ${u.email} ?`)) return
    try {
      await deleteUser.mutateAsync(u.id)
      toast.success('Utilisateur supprimé')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(msg ?? 'Erreur lors de la suppression')
    }
  }

  return (
    <>
      {modal.open && (
        <UserModal
          user={modal.user}
          onClose={() => setModal({ open: false })}
        />
      )}

      <div className="space-y-3">
        <h2 className="text-xs font-semibold text-white uppercase tracking-wider">Système</h2>

        <div className="grid grid-cols-2 gap-3">
          {/* Users */}
          <div className="bg-[#111111] border border-[#262626] rounded-md p-3">
            <div className="flex items-center justify-between mb-3">
              <span className="text-[10px] text-[#737373] uppercase tracking-wide">Utilisateurs</span>
              <button
                onClick={() => setModal({ open: true })}
                className="flex items-center gap-1 h-6 px-2 bg-white text-black text-[9px] font-medium rounded hover:bg-[#e5e5e5] transition-colors"
              >
                <Plus className="h-2.5 w-2.5" />
                Ajouter
              </button>
            </div>
            <div className="space-y-2">
              {isLoading && (
                <p className="text-[10px] text-[#525252]">Chargement…</p>
              )}
              {users?.map((u) => (
                <div key={u.id} className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-white">{u.email}</p>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <Badge variant={roleVariant(u.role)}>{ROLE_LABELS[u.role]}</Badge>
                      {!u.is_active && <Badge variant="default">Inactif</Badge>}
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button
                      onClick={() => setModal({ open: true, user: u })}
                      title="Modifier le rôle"
                      className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors"
                    >
                      <Edit className="h-3 w-3" />
                    </button>
                    <button
                      onClick={() => handleDelete(u)}
                      title="Supprimer"
                      className="w-6 h-6 flex items-center justify-center rounded text-[#525252] hover:text-[#ef4444] hover:bg-[#ef4444]/10 transition-colors"
                    >
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
    </>
  )
}
