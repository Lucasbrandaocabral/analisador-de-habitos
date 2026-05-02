import type { LogEntry } from '../types'

const CATEGORY_COLORS: Record<string, string> = {
  trabalho: 'text-blue-400 bg-blue-400/10',
  estudo: 'text-emerald-400 bg-emerald-400/10',
  redes_sociais: 'text-amber-400 bg-amber-400/10',
  entretenimento: 'text-red-400 bg-red-400/10',
  noticias: 'text-violet-400 bg-violet-400/10',
  outros: 'text-slate-400 bg-slate-400/10',
}

const CATEGORY_LABELS: Record<string, string> = {
  trabalho: 'Trabalho',
  estudo: 'Estudo',
  redes_sociais: 'Redes Sociais',
  entretenimento: 'Entretenimento',
  noticias: 'Notícias',
  outros: 'Outros',
}

interface Props {
  logs: LogEntry[]
}

function formatTime(iso: string) {
  const d = new Date(iso)
  return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })
}

export function RecentLogs({ logs }: Props) {
  return (
    <div className="flex flex-col divide-y divide-slate-700/50">
      {logs.slice(0, 15).map((log) => (
        <div key={log.id} className="flex items-center gap-3 py-3 hover:bg-slate-800/40 px-2 rounded-lg transition-colors">
          <img
            src={`https://www.google.com/s2/favicons?domain=${log.domain}&sz=32`}
            alt=""
            className="w-5 h-5 rounded flex-shrink-0"
            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
          />
          <div className="flex-1 min-w-0">
            <p className="text-sm text-slate-200 truncate">{log.title || log.domain}</p>
            <p className="text-xs text-slate-500 truncate">{log.domain}</p>
          </div>
          <div className="flex flex-col items-end gap-1 flex-shrink-0">
            <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${CATEGORY_COLORS[log.category] ?? CATEGORY_COLORS.outros}`}>
              {CATEGORY_LABELS[log.category] ?? log.category}
            </span>
            <span className="text-[10px] text-slate-500">
              {formatDate(log.visited_at)} {formatTime(log.visited_at)}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
