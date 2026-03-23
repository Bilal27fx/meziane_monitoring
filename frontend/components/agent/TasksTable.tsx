'use client'

import { Play } from 'lucide-react'
import { useTasks, useLaunchTask } from '@/lib/hooks/useAgent'
import { formatDate } from '@/lib/utils/format'
import toast from 'react-hot-toast'
import type { CeleryTask } from '@/lib/types'

function StatusDot({ statut }: { statut: CeleryTask['statut'] }) {
  const styles: Record<CeleryTask['statut'], { dot: string; label: string; text: string }> = {
    ok: { dot: 'bg-[#22c55e]', label: 'OK', text: 'text-[#22c55e]' },
    warning: { dot: 'bg-[#eab308]', label: 'Avertissement', text: 'text-[#eab308]' },
    error: { dot: 'bg-[#ef4444]', label: 'Erreur', text: 'text-[#ef4444]' },
    running: { dot: 'bg-[#3b82f6] animate-pulse', label: 'En cours', text: 'text-[#3b82f6]' },
    pending: { dot: 'bg-[#737373]', label: 'En attente', text: 'text-[#737373]' },
  }
  const s = styles[statut]
  return (
    <div className="flex items-center gap-1.5">
      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${s.dot}`} />
      <span className={`text-xs ${s.text}`}>{s.label}</span>
    </div>
  )
}

export default function TasksTable() {
  const { data: tasks = [], isLoading } = useTasks()
  const launchTask = useLaunchTask()

  const handleLaunch = async (taskId: string, name: string) => {
    try {
      await launchTask.mutateAsync(taskId)
      toast.success(`Tâche "${name}" lancée`)
    } catch {
      toast.error('Erreur lors du lancement')
    }
  }

  // Aggregate stats
  const stats = tasks.reduce(
    (acc, t) => ({
      total: acc.total + (t.tasks_24h ?? 0),
      succes: acc.succes + (t.succes ?? 0),
      erreurs: acc.erreurs + (t.erreurs ?? 0),
      en_attente: acc.en_attente + (t.en_attente ?? 0),
    }),
    { total: 0, succes: 0, erreurs: 0, en_attente: 0 }
  )

  return (
    <div className="space-y-4">
      {/* Table */}
      <div className="bg-[#111111] border border-[#262626] rounded-md overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[#262626]">
              {['Tâche', 'Statut', 'Dernière exec', 'Prochaine', 'Actions'].map((h) => (
                <th key={h} className="px-3 py-2 text-left text-[9px] text-[#525252] uppercase tracking-wider">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading
              ? Array.from({ length: 4 }).map((_, i) => (
                  <tr key={i} className="border-b border-[#262626]/50">
                    {Array.from({ length: 5 }).map((_, j) => (
                      <td key={j} className="px-3 py-3">
                        <div className="h-3 bg-[#262626]/50 rounded animate-pulse" />
                      </td>
                    ))}
                  </tr>
                ))
              : tasks.map((task) => (
                  <tr
                    key={task.id}
                    className="border-b border-[#262626]/50 hover:bg-[#1a1a1a] transition-colors"
                  >
                    <td className="px-3 py-3">
                      <span className="text-xs font-mono text-white">{task.name}</span>
                    </td>
                    <td className="px-3 py-3">
                      <StatusDot statut={task.statut} />
                    </td>
                    <td className="px-3 py-3">
                      <span className="text-xs font-mono text-[#a3a3a3]">
                        {task.derniere_exec ? formatDate(task.derniere_exec) : '—'}
                      </span>
                    </td>
                    <td className="px-3 py-3">
                      <span className="text-xs font-mono text-[#525252]">
                        {task.prochaine_exec ? formatDate(task.prochaine_exec) : '—'}
                      </span>
                    </td>
                    <td className="px-3 py-3">
                      <button
                        onClick={() => handleLaunch(task.id, task.name)}
                        disabled={launchTask.isPending || task.statut === 'running'}
                        className="flex items-center gap-1 px-2 py-1 text-[10px] text-white bg-[#262626] hover:bg-[#404040] rounded transition-colors disabled:opacity-40"
                      >
                        <Play className="h-2.5 w-2.5" />
                        Lancer
                      </button>
                    </td>
                  </tr>
                ))}
          </tbody>
        </table>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-4 gap-2">
        {[
          { label: 'Tasks / 24h', value: stats.total, color: 'text-white' },
          { label: 'Succès', value: stats.succes, color: 'text-[#22c55e]' },
          { label: 'Erreurs', value: stats.erreurs, color: 'text-[#ef4444]' },
          { label: 'En attente', value: stats.en_attente, color: 'text-[#eab308]' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-[#111111] border border-[#262626] rounded-md p-3 text-center">
            <p className="text-[10px] text-[#737373] uppercase tracking-wide">{label}</p>
            <p className={`text-xl font-mono font-semibold tabular-nums mt-1 ${color}`}>{value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
