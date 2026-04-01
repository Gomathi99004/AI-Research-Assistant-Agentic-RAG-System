import React, { useState } from 'react'
import { SendIcon, Loader2 } from 'lucide-react'

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export default function QueryInput({ onSubmit, isLoading }: QueryInputProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim() && !isLoading) {
      onSubmit(query.trim())
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative group">
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="How does the system mitigate hallucinations?"
        className="w-full min-h-[120px] p-4 pr-16 bg-zinc-900/50 border border-zinc-800 focus:border-blue-500/50 rounded-xl resize-none outline-none transition-all placeholder:text-zinc-600 text-zinc-100 shadow-inner block"
        maxLength={2000}
        disabled={isLoading}
      />
      <div className="absolute right-3 bottom-3 flex items-center gap-2">
        <span className="text-xs text-zinc-500 select-none">
          {query.length}/2000
        </span>
        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          className="p-2 rounded-lg bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors z-10"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <SendIcon className="w-5 h-5" />}
        </button>
      </div>
    </form>
  )
}
