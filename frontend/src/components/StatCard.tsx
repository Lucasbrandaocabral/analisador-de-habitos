interface Props {
  label: string
  value: string | number
  sub?: string
  color?: string
}

export function StatCard({ label, value, sub, color = '#3b82f6' }: Props) {
  return (
    <div className="bg-slate-800 rounded-2xl p-5 flex flex-col gap-1 border border-slate-700/50">
      <span className="text-xs text-slate-400 uppercase tracking-widest">{label}</span>
      <span className="text-3xl font-bold" style={{ color }}>{value}</span>
      {sub && <span className="text-xs text-slate-500">{sub}</span>}
    </div>
  )
}
