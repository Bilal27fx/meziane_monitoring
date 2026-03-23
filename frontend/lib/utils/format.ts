export function formatCurrency(value: number): string {
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M€`
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(0)}K€`
  }
  return `${value.toLocaleString('fr-FR')}€`
}

export function formatCurrencyFull(value: number): string {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

export function formatDate(d: string | Date): string {
  return new Date(d).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
  })
}

export function formatDateLong(d: string | Date): string {
  return new Date(d).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
}

export function formatPercent(v: number): string {
  return `${v > 0 ? '+' : ''}${v.toFixed(1)}%`
}

export function formatPercentRaw(v: number): string {
  return `${v.toFixed(2)}%`
}

export function formatNumber(v: number): string {
  return v.toLocaleString('fr-FR')
}

export function formatMonthYear(d: string | Date): string {
  return new Date(d).toLocaleDateString('fr-FR', {
    month: 'short',
    year: 'numeric',
  })
}
