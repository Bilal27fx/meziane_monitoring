'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import Sidebar from '@/components/layout/Sidebar'
import Header from '@/components/layout/Header'
import { tokenStore } from '@/lib/api/client'
import { ThemeProvider, useTheme } from '@/lib/context/ThemeContext'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 20_000,
    },
  },
})

function AppLayoutInner({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { theme } = useTheme()

  useEffect(() => {
    if (!tokenStore.getAccessToken() && !tokenStore.getRefreshToken()) {
      router.push('/login')
    }
  }, [router])

  const isDark = theme === 'dark'

  return (
    <QueryClientProvider client={queryClient}>
      <div className="h-screen overflow-hidden" style={{ backgroundColor: 'var(--t-bg-base)' }}>
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
            background: isDark ? '#111111' : '#ffffff',
            border: `1px solid ${isDark ? '#262626' : '#e0e0e0'}`,
            color: isDark ? '#fff' : '#111111',
            fontSize: '12px',
          },
        }}
      />
    </QueryClientProvider>
  )
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <AppLayoutInner>{children}</AppLayoutInner>
    </ThemeProvider>
  )
}
