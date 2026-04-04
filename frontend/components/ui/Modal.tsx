'use client'

import * as Dialog from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils/cn'

type ModalSize = 'sm' | 'md' | 'lg'
type ModalPosition = 'center' | 'lower'

interface ModalProps {
  open: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  size?: ModalSize
  position?: ModalPosition
}

const sizeStyles: Record<ModalSize, string> = {
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
}

const positionStyles: Record<ModalPosition, string> = {
  center: 'top-1/2 -translate-y-1/2',
  lower: 'top-[56%] -translate-y-1/2',
}

export default function Modal({
  open,
  onClose,
  title,
  children,
  size = 'md',
  position = 'center',
}: ModalProps) {
  return (
    <Dialog.Root open={open} onOpenChange={(v) => !v && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm" />
        <Dialog.Content
          className={cn(
            'fixed left-1/2 z-50 -translate-x-1/2',
            'w-[calc(100vw-24px)] bg-[#111111] border border-[#262626] rounded-lg shadow-2xl',
            'max-h-[78vh] overflow-hidden',
            'focus:outline-none',
            sizeStyles[size],
            positionStyles[position]
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#262626] bg-[#111111]">
            <Dialog.Title className="text-sm font-semibold text-white">
              {title}
            </Dialog.Title>
            <button
              onClick={onClose}
              aria-label="Fermer la fenêtre"
              className="flex items-center justify-center w-8 h-8 rounded border border-[#262626] text-[#a3a3a3] hover:text-white hover:bg-[#262626] transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Body */}
          <div className="p-4 overflow-y-auto max-h-[calc(78vh-64px)]">
            {children}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
