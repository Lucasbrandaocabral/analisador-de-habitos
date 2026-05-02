import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from 'recharts'

interface Props {
  score: number
  label: string
  message: string
}

const scoreColor = (s: number) => {
  if (s >= 80) return '#22c55e'
  if (s >= 65) return '#86efac'
  if (s >= 45) return '#facc15'
  if (s >= 30) return '#fb923c'
  return '#ef4444'
}

export function ScoreGauge({ score, label, message }: Props) {
  const color = scoreColor(score)
  const data = [{ value: score, fill: color }]

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-48 h-48">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="50%"
            innerRadius="70%"
            outerRadius="100%"
            startAngle={210}
            endAngle={-30}
            data={data}
          >
            <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
            <RadialBar
              dataKey="value"
              cornerRadius={10}
              background={{ fill: '#1e293b' }}
            />
          </RadialBarChart>
        </ResponsiveContainer>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold" style={{ color }}>{score}</span>
          <span className="text-xs text-slate-400 mt-1">/100</span>
        </div>
      </div>

      <div className="text-center">
        <p className="text-lg font-semibold" style={{ color }}>{label}</p>
        <p className="text-xs text-slate-400 mt-1 max-w-[200px] leading-relaxed">{message}</p>
      </div>
    </div>
  )
}
