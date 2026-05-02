import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { RefreshCw, Activity } from 'lucide-react'
import { api } from './api'
import { ScoreGauge } from './components/ScoreGauge'
import { CategoryPieChart } from './components/CategoryPieChart'
import { TopSitesChart } from './components/TopSitesChart'
import { StatCard } from './components/StatCard'
import { RecentLogs } from './components/RecentLogs'

const DAYS_OPTIONS = [1, 7, 14, 30]

const CATEGORY_PT: Record<string, string> = {
  trabalho: 'Trabalho', estudo: 'Estudo', redes_sociais: 'Redes Sociais',
  entretenimento: 'Entretenimento', noticias: 'Notícias', outros: 'Outros',
}

const CATEGORY_COLORS: Record<string, string> = {
  trabalho: '#3b82f6', estudo: '#10b981', redes_sociais: '#f59e0b',
  entretenimento: '#ef4444', noticias: '#8b5cf6', outros: '#64748b',
}

function Card({ title, children, className = '' }: { title: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-slate-800/60 border border-slate-700/50 rounded-2xl p-6 ${className}`}>
      <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">{title}</h2>
      {children}
    </div>
  )
}

function Spinner() {
  return (
    <div className="flex items-center justify-center h-40">
      <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

export default function App() {
  const [days, setDays] = useState(7)
  const client = useQueryClient()

  const stats = useQuery({ queryKey: ['stats', days], queryFn: () => api.stats(days) })
  const productivity = useQuery({ queryKey: ['productivity', days], queryFn: () => api.productivity(days) })
  const logs = useQuery({ queryKey: ['logs', days], queryFn: () => api.logs(days, 50) })

  const collect = useMutation({
    mutationFn: api.collect,
    onSuccess: () => client.invalidateQueries(),
  })

  const totalMinutes = stats.data
    ? Object.values(stats.data.time_by_category_minutes).reduce((a, b) => a + b, 0)
    : 0

  const topCategory = stats.data
    ? Object.entries(stats.data.time_by_category_minutes).sort((a, b) => b[1] - a[1])[0]?.[0] ?? '—'
    : '—'

  const totalVisits = productivity.data
    ? Object.values(productivity.data.breakdown).reduce((s, d) => s + d.visits, 0)
    : 1

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between sticky top-0 z-10 backdrop-blur bg-slate-900/80">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <Activity size={16} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-100 leading-none">Hábitos Digitais</h1>
            <p className="text-xs text-slate-500 mt-0.5">Análise de comportamento online</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex gap-1 bg-slate-800 rounded-xl p-1">
            {DAYS_OPTIONS.map((d) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
                  days === d ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {d === 1 ? 'Hoje' : `${d}d`}
              </button>
            ))}
          </div>

          <button
            onClick={() => collect.mutate()}
            disabled={collect.isPending}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-medium px-4 py-2 rounded-xl transition-colors disabled:opacity-50 cursor-pointer"
          >
            <RefreshCw size={13} className={collect.isPending ? 'animate-spin' : ''} />
            {collect.isPending
              ? 'Coletando...'
              : collect.isSuccess
              ? `+${(collect.data as any)?.inserted ?? 0} novos`
              : 'Atualizar'}
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 flex flex-col gap-6">
        {/* Stat cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            label="Total de acessos"
            value={stats.data?.total_accesses.toLocaleString('pt-BR') ?? '—'}
            sub={`últimos ${days} dia${days > 1 ? 's' : ''}`}
            color="#3b82f6"
          />
          <StatCard
            label="Tempo estimado"
            value={totalMinutes >= 60 ? `${Math.round(totalMinutes / 60)}h ${Math.round(totalMinutes % 60)}min` : `${Math.round(totalMinutes)}min`}
            sub="online no período"
            color="#10b981"
          />
          <StatCard
            label="Maior categoria"
            value={CATEGORY_PT[topCategory] ?? topCategory}
            sub="por tempo gasto"
            color="#f59e0b"
          />
          <StatCard
            label="Score"
            value={productivity.data ? `${productivity.data.score}/100` : '—'}
            sub={productivity.data?.label ?? ''}
            color={productivity.data ? (productivity.data.score >= 65 ? '#22c55e' : productivity.data.score >= 45 ? '#facc15' : '#ef4444') : '#64748b'}
          />
        </div>

        {/* Score + Pie */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card title="Score de Produtividade" className="flex flex-col items-center justify-center">
            {productivity.isLoading ? <Spinner /> : productivity.data ? (
              <ScoreGauge
                score={productivity.data.score}
                label={productivity.data.label}
                message={productivity.data.message}
              />
            ) : null}
          </Card>

          <Card title="Tempo por Categoria" className="md:col-span-2">
            {stats.isLoading ? <Spinner /> : stats.data ? (
              <CategoryPieChart data={stats.data.time_by_category_minutes} />
            ) : null}
          </Card>
        </div>

        {/* Top sites + breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card title="Top 10 Sites" className="md:col-span-2">
            {stats.isLoading ? <Spinner /> : stats.data ? (
              <TopSitesChart sites={stats.data.top_sites} />
            ) : null}
          </Card>

          <Card title="Breakdown por Categoria">
            {productivity.isLoading ? <Spinner /> : productivity.data ? (
              <div className="flex flex-col gap-4">
                {Object.entries(productivity.data.breakdown)
                  .sort((a, b) => b[1].visits - a[1].visits)
                  .map(([cat, data]) => {
                    const pct = Math.round((data.visits / totalVisits) * 100)
                    const color = CATEGORY_COLORS[cat] ?? '#64748b'
                    return (
                      <div key={cat}>
                        <div className="flex justify-between text-xs mb-1.5">
                          <span className="text-slate-300 font-medium">{CATEGORY_PT[cat] ?? cat}</span>
                          <span className="text-slate-500">{data.visits} visitas · {pct}%</span>
                        </div>
                        <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full"
                            style={{ width: `${pct}%`, backgroundColor: color }}
                          />
                        </div>
                      </div>
                    )
                  })}
              </div>
            ) : null}
          </Card>
        </div>

        {/* Recent logs */}
        <Card title="Histórico Recente">
          {logs.isLoading ? <Spinner /> : logs.data && logs.data.length > 0 ? (
            <RecentLogs logs={logs.data} />
          ) : (
            <p className="text-slate-500 text-sm text-center py-8">Nenhum registro para este período.</p>
          )}
        </Card>
      </main>
    </div>
  )
}
