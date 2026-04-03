'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { tokenStore } from '@/lib/api/client'
import AdminTabs from '@/components/admin/AdminTabs'

export default function AdminPage() {
  const router = useRouter()

  useEffect(() => {
    const role = tokenStore.getRole()
    if (role !== null && role !== 'admin') {
      router.replace('/dashboard')
    }
  }, [router])

  return (
    <div className="h-[calc(100vh-56px)] flex flex-col overflow-hidden">
      <AdminTabs />
    </div>
  )
}
