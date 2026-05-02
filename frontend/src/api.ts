import type { StatsResponse, ProductivityResponse, LogEntry, CollectResult } from './types'

const BASE = '/api'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export const api = {
  stats: (days = 7) => get<StatsResponse>(`/stats?days_back=${days}`),
  productivity: (days = 7) => get<ProductivityResponse>(`/productivity?days_back=${days}`),
  logs: (days = 7, limit = 50) => get<LogEntry[]>(`/logs?days_back=${days}&limit=${limit}`),
  collect: () =>
    fetch(`${BASE}/logs/collect`, { method: 'POST' }).then((r) => r.json() as Promise<CollectResult>),
}
