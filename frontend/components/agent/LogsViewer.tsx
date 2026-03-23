'use client'

import { useEffect, useRef, useState } from 'react'
import { useLogs } from '@/lib/hooks/useAgent'
import { cn } from '@/lib/utils/cn'

type LogLevel = 'INFO' | 'DEBUG' | 'WARN' | 'ERROR'

interface LogLine {
  time: string
  level: string
  module: string
  message: string
}

function levelColor(level: string): string {
  const map: Record<string, string> = {
    INFO: 'text-[#737373]',
    DEBUG: 'text-[#525252]',
    WARN: 'text-[#eab308]',
    ERROR: 'text-[#ef4444]',
  }
  return map[level] ?? 'text-[#737373]'
}

function levelBadge(level: string): string {
  const map: Record<string, string> = {
    INFO: 'text-[#3b82f6]',
    DEBUG: 'text-[#525252]',
    WARN: 'text-[#eab308]',
    ERROR: 'text-[#ef4444]',
  }
  return map[level] ?? 'text-[#737373]'
}

export default function LogsViewer() {
  const { data: logs = [] } = useLogs()
  const [autoScroll, setAutoScroll] = useState(true)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, autoScroll])

  return (
    <div className="bg-[#0d0d0d] border border-[#262626] rounded-md flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-[#262626]">
        <span className="text-[10px] text-[#737373] uppercase tracking-wide">Logs système</span>
        <div className="flex items-center gap-2">
          <span className="text-[9px] text-[#525252]">{logs.length} lignes</span>
          <button
            onClick={() => setAutoScroll((v) => !v)}
            className={cn(
              'flex items-center gap-1 px-2 py-0.5 rounded text-[9px] transition-colors',
              autoScroll
                ? 'bg-[#22c55e]/20 text-[#22c55e] border border-[#22c55e]/30'
                : 'bg-[#262626] text-[#525252]'
            )}
          >
            {autoScroll ? '⏸ Auto-scroll' : '▶ Auto-scroll'}
          </button>
        </div>
      </div>

      {/* Log content */}
      <div className="flex-1 overflow-y-auto p-3 space-y-0.5 font-mono">
        {logs.map((line: LogLine, i) => (
          <div key={i} className={cn('flex items-start gap-2 text-[10px] hover:bg-[#111111] rounded px-1 py-0.5 group', levelColor(line.level))}>
            <span className="text-[#404040] flex-shrink-0 tabular-nums">{line.time}</span>
            <span className={cn('w-12 flex-shrink-0 font-semibold', levelBadge(line.level))}>
              {line.level}
            </span>
            <span className="text-[#404040] flex-shrink-0 min-w-0 max-w-32 truncate">[{line.module}]</span>
            <span className="flex-1 break-all">{line.message}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
