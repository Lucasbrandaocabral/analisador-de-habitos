import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const CATEGORY_COLORS: Record<string, string> = {
  trabalho: '#3b82f6',
  estudo: '#10b981',
  redes_sociais: '#f59e0b',
  entretenimento: '#ef4444',
  noticias: '#8b5cf6',
  outros: '#64748b',
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
  data: Record<string, number>
}

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null
  const { name, value } = payload[0]
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm">
      <p className="text-slate-200 font-medium">{CATEGORY_LABELS[name] ?? name}</p>
      <p className="text-slate-400">{value.toFixed(0)} min</p>
    </div>
  )
}

export function CategoryPieChart({ data }: Props) {
  const chartData = Object.entries(data)
    .map(([key, value]) => ({ name: key, value }))
    .filter((d) => d.value > 0)
    .sort((a, b) => b.value - a.value)

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={65}
          outerRadius={100}
          paddingAngle={3}
          dataKey="value"
        >
          {chartData.map((entry) => (
            <Cell
              key={entry.name}
              fill={CATEGORY_COLORS[entry.name] ?? '#64748b'}
              stroke="transparent"
            />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend
          formatter={(value) => (
            <span className="text-slate-300 text-xs">{CATEGORY_LABELS[value] ?? value}</span>
          )}
          iconType="circle"
          iconSize={8}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
