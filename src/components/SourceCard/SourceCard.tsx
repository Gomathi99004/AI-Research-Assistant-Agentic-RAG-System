import { FileTextIcon } from 'lucide-react'
import { SourceRef } from '../../types/research'

interface Props {
  source: SourceRef;
}

export default function SourceCard({ source }: Props) {
  return (
    <div className="group flex items-start gap-3 p-4 rounded-xl relative bg-zinc-950 border border-zinc-800 transition-all hover:bg-zinc-900 overflow-hidden">
      <div className="absolute top-0 left-0 w-1 h-full bg-zinc-800 group-hover:bg-blue-500 transition-colors" />
      
      <div className="p-2 rounded-lg bg-zinc-800/50 text-blue-400 group-hover:scale-110 group-hover:bg-blue-500/20 transition-all duration-300">
        <FileTextIcon className="w-5 h-5" />
      </div>
      
      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-semibold text-zinc-200 truncate pr-4">
          {source.title}
        </h4>
        <div className="flex items-center gap-3 mt-1.5 opacity-80">
          <div className="flex items-center gap-1.5">
            <div className="text-[10px] tracking-wider uppercase font-semibold text-zinc-500">
              Chunk
            </div>
            <code className="text-xs bg-black px-1.5 py-0.5 rounded text-zinc-400 font-mono">
              {source.chunk_id.substring(0, 8)}
            </code>
          </div>
          <div className="h-3 w-px bg-zinc-800"></div>
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] tracking-wider uppercase font-semibold text-zinc-500">
              Match
            </span>
            <span className="text-xs text-blue-400 font-medium">
              {(source.relevance_score * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
