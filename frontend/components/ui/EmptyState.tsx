import { Inbox } from 'lucide-react'
import { cn } from '@/lib/utils/cn'

interface EmptyStateProps {
  title?: string
  description?: string
  icon?: React.ElementType
  action?: React.ReactNode
  className?: string
}

export default function EmptyState({
  title = 'Aucune donnée',
  description = 'Il n\'y a rien à afficher pour le moment.',
  icon: Icon = Inbox,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-8 px-4 text-center', className)}>
      <Icon className="h-8 w-8 text-[#404040] mb-3" />
      <p className="text-sm text-white font-medium mb-1">{title}</p>
      <p className="text-xs text-[#737373] max-w-xs">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
