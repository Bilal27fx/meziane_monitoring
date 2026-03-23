'use client'

import * as Dialog from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils/cn'

type ModalSize = 'sm' | 'md' | 'lg'

interface ModalProps {
  open: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  size?: ModalSize
}

const sizeStyles: Record<ModalSize, string> = {
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
}

export default function Modal({ open, onClose, title, children, size = 'md' }: ModalProps) {
  return (
    <Dialog.Root open={open} onOpenChange={(v) => !v && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm" />
        <Dialog.Content
          className={cn(
            'fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2',
            'w-full bg-[#111111] border border-[#262626] rounded-lg shadow-2xl',
            'focus:outline-none',
            sizeStyles[size]
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#262626]">
            <Dialog.Title className="text-sm font-semibold text-white">
              {title}
            </Dialog.Title>
            <button
              onClick={onClose}
              className="flex items-center justify-center w-6 h-6 rounded text-[#525252] hover:text-white hover:bg-[#262626] transition-colors"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>

          {/* Body */}
          <div className="p-4">
            {children}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
