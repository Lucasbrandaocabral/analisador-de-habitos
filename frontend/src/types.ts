export interface TopSite {
  domain: string
  visits: number
}

export interface StatsResponse {
  total_accesses: number
  top_sites: TopSite[]
  time_by_category_minutes: Record<string, number>
  accesses_by_category: Record<string, number>
  days_analyzed: number
}

export interface ProductivityBreakdown {
  visits: number
  contribution: number
}

export interface ProductivityResponse {
  score: number
  label: string
  message: string
  breakdown: Record<string, ProductivityBreakdown>
}

export interface LogEntry {
  id: number
  url: string
  title: string
  domain: string
  visited_at: string
  category: string
  source: string
}

export interface CollectResult {
  inserted: number
  skipped: number
  source: string
}
