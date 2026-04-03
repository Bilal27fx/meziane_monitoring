'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import Sidebar from '@/components/layout/Sidebar'
import Header from '@/components/layout/Header'
import { tokenStore } from '@/lib/api/client'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 20_000,
    },
  },
})

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  useEffect(() => {
    if (!tokenStore.getAccessToken() && !tokenStore.getRefreshToken()) {
      router.push('/login')
    }
  }, [router])

  return (
    <QueryClientProvider client={queryClient}>
      <div className="h-screen bg-[#0a0a0a] overflow-hidden">
        <Sidebar />
        <Header />
        <main className="pl-12 pt-14 h-full overflow-y-auto">
          {children}
        </main>
      </div>
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: '#111111',
            border: '1px solid #262626',
            color: '#fff',
            fontSize: '12px',
          },
        }}
      />
    </QueryClientProvider>
  )
}
