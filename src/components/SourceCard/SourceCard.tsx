import { FileTextIcon } from 'lucide-react'
import { SourceRef } from '../../types/research'

interface Props {
  source: SourceRef;
}

export default function SourceCard({ source }: Props) {
  return (
    <div className="group relative flex items-center justify-center p-2 px-3 rounded-lg bg-[#1c1c1e] hover:bg-indigo-500/10 border border-zinc-800 hover:border-indigo-500/30 transition-all cursor-pointer shadow-sm">
      <FileTextIcon className="w-3.5 h-3.5 text-indigo-400" />
      
      {/* Tooltip that only appears on hover */}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 w-max min-w-[200px] px-4 py-3 bg-zinc-900 border border-zinc-700 rounded-xl shadow-2xl opacity-0 scale-95 group-hover:opacity-100 group-hover:scale-100 transition-all pointer-events-none z-50 flex flex-col items-center">
        <span className="text-sm font-semibold text-zinc-100">{source.title}</span>
        <div className="flex items-center gap-2 mt-2 pt-2 border-t border-zinc-800 w-full justify-center">
          <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold bg-black px-1.5 py-0.5 rounded">
            Chunk: {source.chunk_id.substring(0, 6)}
          </span>
          <span className="text-xs text-indigo-400 font-medium bg-indigo-500/10 px-1.5 py-0.5 rounded">
            Match: {(source.relevance_score * 100).toFixed(1)}%
          </span>
        </div>
        
        {/* Triangle caret pointer */}
        <div className="absolute top-full left-1/2 -translate-x-1/2 border-[6px] border-transparent border-t-zinc-700"></div>
        <div className="absolute top-full left-1/2 -translate-x-1/2 border-[5px] border-transparent border-t-zinc-900 mb-[1px]"></div>
      </div>
    </div>
  )
}
