export function formatDateTime(value?: string | null) {
  if (!value) {
    return '--'
  }
  const normalized = value.replace('T', ' ')
  return normalized.length >= 19 ? normalized.slice(0, 19) : normalized
}

export function formatCurrency(value?: string | number | null) {
  if (value == null || value === '') {
    return '--'
  }
  const amount = typeof value === 'number' ? value : Number(value)
  if (Number.isNaN(amount)) {
    return String(value)
  }
  return `¥${amount.toFixed(2)}`
}

export function maskText(value?: string | null) {
  if (!value) {
    return '--'
  }
  if (value.length <= 4) {
    return `${value.slice(0, 1)}***`
  }
  return `${value.slice(0, 2)}********${value.slice(-2)}`
}

export function maskPhone(value?: string | null) {
  if (!value) {
    return '--'
  }
  if (value.length < 7) {
    return value
  }
  return `${value.slice(0, 3)}****${value.slice(-4)}`
}

export function maskIdCard(value?: string | null) {
  return maskText(value)
}
