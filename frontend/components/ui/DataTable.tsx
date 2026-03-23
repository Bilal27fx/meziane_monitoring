'use client'

import { ChevronLeft, ChevronRight } from 'lucide-react'
import Skeleton from './Skeleton'
import EmptyState from './EmptyState'
import { cn } from '@/lib/utils/cn'

export interface Column<T> {
  header: string
  accessor: keyof T | string
  render?: (row: T) => React.ReactNode
  className?: string
  headerClassName?: string
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  loading?: boolean
  emptyMessage?: string
  pagination?: {
    page: number
    totalPages: number
    total: number
    onPageChange: (page: number) => void
  }
  className?: string
  rowKey?: (row: T, index: number) => string | number
}

export default function DataTable<T extends object>({
  columns,
  data,
  loading = false,
  emptyMessage = 'Aucune donnée disponible',
  pagination,
  className,
  rowKey,
}: DataTableProps<T>) {
  const getCellValue = (row: T, accessor: string): React.ReactNode => {
    const keys = accessor.split('.')
    let value: unknown = row
    for (const key of keys) {
      value = (value as Record<string, unknown>)?.[key] ?? undefined
    }
    return value as React.ReactNode
  }

  return (
    <div className={cn('flex flex-col', className)}>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-[#262626]">
              {columns.map((col) => (
                <th
                  key={col.header}
                  className={cn(
                    'py-1.5 px-2 text-left text-[9px] text-[#525252] uppercase tracking-wider font-medium whitespace-nowrap',
                    col.headerClassName
                  )}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="border-b border-[#262626]/50">
                  {columns.map((col) => (
                    <td key={col.header} className="py-2 px-2">
                      <Skeleton className="h-3 w-full" />
                    </td>
                  ))}
                </tr>
              ))
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length}>
                  <EmptyState description={emptyMessage} className="py-6" />
                </td>
              </tr>
            ) : (
              data.map((row, index) => (
                <tr
                  key={rowKey ? rowKey(row, index) : index}
                  className="border-b border-[#262626]/50 hover:bg-[#1a1a1a] transition-colors"
                >
                  {columns.map((col) => (
                    <td
                      key={col.header}
                      className={cn('text-xs text-white py-2 px-2', col.className)}
                    >
                      {col.render ? col.render(row) : getCellValue(row, col.accessor as string)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {pagination && pagination.totalPages > 1 && (
        <div className="flex items-center justify-between pt-2 mt-2 border-t border-[#262626]">
          <span className="text-[10px] text-[#525252]">
            {pagination.total} résultat{pagination.total !== 1 ? 's' : ''}
          </span>
          <div className="flex items-center gap-1">
            <button
              onClick={() => pagination.onPageChange(pagination.page - 1)}
              disabled={pagination.page <= 1}
              className="flex items-center justify-center w-6 h-6 rounded text-[#525252] hover:text-white hover:bg-[#262626] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="h-3 w-3" />
            </button>
            <span className="text-[10px] text-[#737373] min-w-12 text-center">
              {pagination.page} / {pagination.totalPages}
            </span>
            <button
              onClick={() => pagination.onPageChange(pagination.page + 1)}
              disabled={pagination.page >= pagination.totalPages}
              className="flex items-center justify-center w-6 h-6 rounded text-[#525252] hover:text-white hover:bg-[#262626] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="h-3 w-3" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
