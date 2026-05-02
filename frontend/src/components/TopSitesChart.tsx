import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import type { TopSite } from '../types'

interface Props {
  sites: TopSite[]
}

const SOCIAL = ['instagram.com', 'twitter.com', 'x.com', 'facebook.com', 'tiktok.com', 'reddit.com']
const ENTERTAINMENT = ['youtube.com', 'netflix.com', 'twitch.tv', 'spotify.com']

const barColor = (domain: string) => {
  if (SOCIAL.some((s) => domain.includes(s))) return '#f59e0b'
  if (ENTERTAINMENT.some((s) => domain.includes(s))) return '#ef4444'
  return '#3b82f6'
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm">
      <p className="text-slate-200 font-medium">{label}</p>
      <p className="text-slate-400">{payload[0].value} visitas</p>
    </div>
  )
}

export function TopSitesChart({ sites }: Props) {
  const data = sites.slice(0, 10).map((s) => ({
    domain: s.domain.replace('www.', ''),
    visits: s.visits,
  }))

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
        <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis
          type="category"
          dataKey="domain"
          width={110}
          tick={{ fill: '#cbd5e1', fontSize: 12 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#1e293b' }} />
        <Bar dataKey="visits" radius={[0, 6, 6, 0]} maxBarSize={22}>
          {data.map((entry) => (
            <Cell key={entry.domain} fill={barColor(entry.domain)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
