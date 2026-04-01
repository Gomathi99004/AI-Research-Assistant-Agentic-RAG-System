import { useState } from 'react'
import { ResearchResponse } from '../../types/research'
import ConfidenceBadge from '../ConfidenceBadge/ConfidenceBadge'
import SourceCard from '../SourceCard/SourceCard'
import { Loader2, LayoutList, AlignLeft, SplitSquareHorizontal, CheckCircle2 } from 'lucide-react'

interface Props {
  data?: ResearchResponse;
  isLoading: boolean;
}

export default function ResponsePanel({ data, isLoading }: Props) {
  const [activeTab, setActiveTab] = useState<'summary' | 'points' | 'comparison'>('summary')

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4 animate-in fade-in duration-500">
        <div className="relative">
          <div className="absolute inset-0 bg-blue-500 blur-xl opacity-20 rounded-full animate-pulse blur-3xl"></div>
          <div className="p-4 bg-zinc-800/50 rounded-2xl relative">
            <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
          </div>
        </div>
        <div className="text-zinc-400 font-medium text-sm flex items-center gap-2">
          <span>Synthesizing knowledge</span>
          <span className="flex gap-1">
            <span className="animate-bounce delay-75">.</span>
            <span className="animate-bounce delay-150">.</span>
            <span className="animate-bounce delay-300">.</span>
          </span>
        </div>
      </div>
    )
  }

  if (!data) return null;

  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Header Info */}
      <div className="flex items-center justify-between pb-4 border-b border-border/50">
        <div className="flex items-center gap-4">
          <ConfidenceBadge confidence={data.confidence} />
        </div>
        <div className="text-xs font-mono text-zinc-500">
          {(data.latency_ms / 1000).toFixed(2)}s runtime
        </div>
      </div>

      {data.low_confidence && (
        <div className="bg-amber-500/10 border border-amber-500/20 text-amber-500 text-sm p-4 rounded-xl flex items-start gap-3">
          <div className="mt-0.5"><CheckCircle2 className="w-4 h-4" /></div>
          <p>
            The system struggled to confidently ground this answer using the available documents.
            Please verify the claims independently.
          </p>
        </div>
      )}

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 flex flex-col gap-6">
          <div className="flex items-center gap-2 border-b border-border pb-px">
            <TabButton 
              active={activeTab === 'summary'} 
              onClick={() => setActiveTab('summary')}
              icon={<AlignLeft className="w-4 h-4" />}
            >
              Summary
            </TabButton>
            <TabButton 
              active={activeTab === 'points'} 
              onClick={() => setActiveTab('points')}
              icon={<LayoutList className="w-4 h-4" />}
            >
              Key Points
            </TabButton>
            {data.comparison && (
              <TabButton 
                active={activeTab === 'comparison'} 
                onClick={() => setActiveTab('comparison')}
                icon={<SplitSquareHorizontal className="w-4 h-4" />}
              >
                Comparison
              </TabButton>
            )}
          </div>

          <div className="min-h-[200px]">
            {activeTab === 'summary' && (
              <div className="text-zinc-300 leading-relaxed text-[15px] animate-in fade-in">
                {data.summary}
              </div>
            )}
            {activeTab === 'points' && (
              <ul className="space-y-4 animate-in fade-in">
                {data.key_points.map((point, i) => (
                  <li key={i} className="flex items-start gap-3 group">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center text-xs font-bold border border-blue-500/20 group-hover:scale-110 transition-transform">
                      {i + 1}
                    </span>
                    <span className="text-zinc-300 pt-0.5 leading-relaxed text-[15px]">{point}</span>
                  </li>
                ))}
              </ul>
            )}
            {activeTab === 'comparison' && data.comparison && (
              <div className="text-zinc-300 leading-relaxed text-[15px] whitespace-pre-wrap font-mono text-sm bg-black/50 p-4 rounded-xl border border-zinc-800 animate-in fade-in">
                {data.comparison}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Sources */}
        <div className="flex flex-col gap-4">
          <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-widest flex items-center gap-2">
            Sources Referenced
            <span className="bg-zinc-800 text-zinc-300 rounded-full px-2 py-0.5 text-[10px]">
              {data.sources.length}
            </span>
          </h3>
          <div className="flex flex-col gap-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
            {data.sources.map((source, i) => (
              <SourceCard key={i} source={source} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function TabButton({ children, active, onClick, icon }: any) {
  return (
    <button
      onClick={onClick}
      className={`pb-3 px-1 text-sm font-medium transition-all relative flex items-center gap-2
        ${active ? 'text-blue-400' : 'text-zinc-500 hover:text-zinc-300'}
      `}
    >
      {icon}
      {children}
      {active && (
        <span className="absolute bottom-[-1px] left-0 right-0 h-0.5 bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)] rounded-t-full"></span>
      )}
    </button>
  )
}
