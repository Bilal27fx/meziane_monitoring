import { cn } from '@/lib/utils/cn'

interface SkeletonProps {
  className?: string
}

export default function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn('bg-[#262626]/50 animate-pulse rounded', className)}
    />
  )
}
