import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { ResearchResponse } from '../../types/research'
import ConfidenceBadge from '../ConfidenceBadge/ConfidenceBadge'
import SourceCard from '../SourceCard/SourceCard'
import { Loader2, LayoutList, AlignLeft, SplitSquareHorizontal, AlertTriangle } from 'lucide-react'

interface Props {
  data?: ResearchResponse;
  isLoading: boolean;
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

// GAP 1: Styled markdown renderer — maps markdown elements to our dark theme design tokens
const MarkdownComponents = {
  h3: ({ children }: any) => (
    <h3 className="text-base font-semibold text-zinc-100 mt-5 mb-2 border-b border-zinc-800 pb-1">{children}</h3>
  ),
  h2: ({ children }: any) => (
    <h2 className="text-lg font-bold text-zinc-100 mt-6 mb-2">{children}</h2>
  ),
  strong: ({ children }: any) => (
    <strong className="text-white font-semibold">{children}</strong>
  ),
  ul: ({ children }: any) => (
    <ul className="my-3 space-y-2 pl-2">{children}</ul>
  ),
  li: ({ children }: any) => (
    <li className="flex items-start gap-2 text-zinc-300 leading-relaxed">
      <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0"></span>
      <span>{children}</span>
    </li>
  ),
  ol: ({ children }: any) => (
    <ol className="my-3 space-y-2 pl-2 list-decimal list-inside">{children}</ol>
  ),
  p: ({ children }: any) => (
    <p className="text-zinc-300 leading-relaxed mb-3">{children}</p>
  ),
  code: ({ children }: any) => (
    <code className="bg-zinc-800 text-indigo-300 px-1.5 py-0.5 rounded text-[13px] font-mono">{children}</code>
  ),
  blockquote: ({ children }: any) => (
    <blockquote className="border-l-2 border-indigo-500 pl-4 italic text-zinc-400 my-3">{children}</blockquote>
  ),
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
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-border/50">
        <div className="flex items-center gap-4">
          <ConfidenceBadge confidence={data.confidence} />
        </div>
        <div className="text-xs font-mono text-zinc-500">
          {(data.latency_ms / 1000).toFixed(2)}s runtime
        </div>
      </div>

      {data.low_confidence && (
        <div className="bg-amber-500/10 border border-amber-500/20 text-amber-400 text-sm p-4 rounded-xl flex items-start gap-3">
          <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
          <p>
            The system had low confidence grounding this answer from the available documents.
            Please verify claims independently.
          </p>
        </div>
      )}

      {/* Tabs */}
      <div className="flex flex-col gap-6 w-full">
        <div className="flex items-center gap-2 border-b border-border pb-px overflow-x-auto custom-scrollbar">
          <TabButton active={activeTab === 'summary'} onClick={() => setActiveTab('summary')} icon={<AlignLeft className="w-4 h-4 shrink-0" />}>
            Summary
          </TabButton>
          <TabButton active={activeTab === 'points'} onClick={() => setActiveTab('points')} icon={<LayoutList className="w-4 h-4 shrink-0" />}>
            Key Points
          </TabButton>
          {data.comparison && (
            <TabButton active={activeTab === 'comparison'} onClick={() => setActiveTab('comparison')} icon={<SplitSquareHorizontal className="w-4 h-4 shrink-0" />}>
              Comparison
            </TabButton>
          )}
        </div>

        <div className="min-h-[200px]">
          {/* GAP 1 FIX: Render summary as Markdown instead of raw text */}
          {activeTab === 'summary' && (
            <div className="animate-in fade-in">
              <ReactMarkdown components={MarkdownComponents}>{data.summary}</ReactMarkdown>
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
            <div className="animate-in fade-in prose-sm">
              <ReactMarkdown components={MarkdownComponents}>{data.comparison}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Source chips footer */}
        {data.sources.length > 0 && (
          <div className="flex flex-wrap items-center gap-2 pt-4 mt-2 border-t border-zinc-800/80 w-full">
            <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mr-2 flex items-center gap-2">
              Sources
              <span className="bg-zinc-800 text-zinc-300 rounded-full px-2 py-0.5 text-[10px]">
                {data.sources.length}
              </span>
            </h3>
            <div className="flex flex-wrap gap-2">
              {data.sources.map((source, i) => (
                <SourceCard key={i} source={source} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
