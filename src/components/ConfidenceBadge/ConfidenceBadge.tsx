import { ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react'

interface Props {
  confidence: number;
}

export default function ConfidenceBadge({ confidence }: Props) {
  let colorClass = ''
  let Icon = ShieldCheck
  let label = 'High Confidence'

  if (confidence >= 0.85) {
    colorClass = 'text-green-500 bg-green-500/10 border-green-500/20'
    Icon = ShieldCheck
    label = 'High Confidence'
  } else if (confidence >= 0.75) {
    colorClass = 'text-amber-500 bg-amber-500/10 border-amber-500/20'
    Icon = ShieldAlert
    label = 'Medium Confidence'
  } else {
    colorClass = 'text-red-500 bg-red-500/10 border-red-500/20'
    Icon = ShieldX
    label = 'Low Confidence'
  }

  return (
    <div className={`px-3 py-1.5 rounded-full border flex items-center gap-1.5 text-xs font-medium w-fit ${colorClass}`}>
      <Icon className="w-4 h-4" />
      <span>{label}</span>
      <span className="opacity-75 tracking-wider ml-1">
        {(confidence * 100).toFixed(0)}%
      </span>
    </div>
  )
}
