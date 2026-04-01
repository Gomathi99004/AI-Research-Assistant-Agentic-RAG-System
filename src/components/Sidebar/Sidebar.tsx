import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { fetchDocuments, deleteDocument } from '../../api/research';
import { FileText, Loader2, Database, CheckSquare, Square, Trash2 } from 'lucide-react';
import { useState } from 'react';

interface SidebarProps {
  activePdf: string | null;
  onSelectPdf: (filename: string | null) => void;
  selectedFiles: string[];
  onToggleFile: (filename: string) => void;
  onTriggerUpload: () => void;
}

export default function Sidebar({ activePdf, onSelectPdf, selectedFiles, onToggleFile, onTriggerUpload }: SidebarProps) {
  const queryClient = useQueryClient();
  const [deletingFile, setDeletingFile] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: fetchDocuments,
    refetchInterval: 5000, 
  });

  const deleteMutation = useMutation({
    mutationFn: deleteDocument,
    onSuccess: (_data, filename) => {
      // If the deleted file was active, clear it
      if (activePdf === filename) onSelectPdf(null);
      // Optimistically refresh document list
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setDeletingFile(null);
    },
    onError: () => {
      setDeletingFile(null);
    }
  });

  const handleDelete = (e: React.MouseEvent, filename: string) => {
    e.stopPropagation();
    if (window.confirm(`Remove "${filename}" and all its indexed data?`)) {
      setDeletingFile(filename);
      deleteMutation.mutate(filename);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center p-4">
        <Loader2 className="w-5 h-5 animate-spin text-zinc-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-sm text-red-500/80 p-2">
        Failed to load documents
      </div>
    );
  }

  const docs = data?.documents || [];

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2 text-xs font-semibold text-zinc-500 uppercase tracking-widest">
          <Database className="w-3 h-3" />
          Indexed Documents
        </div>
        <div className="text-[10px] text-zinc-600 font-medium bg-zinc-900 px-2 py-0.5 rounded-full">
          {selectedFiles.length > 0 ? `${selectedFiles.length} Selected` : 'Global Search'}
        </div>
      </div>
      
      {docs.length === 0 ? (
        <div className="text-sm text-zinc-500 italic p-4 border border-dashed border-zinc-800 rounded-lg text-center flex flex-col items-center gap-3">
          No files uploaded yet.
          <button 
            onClick={onTriggerUpload}
            className="text-xs bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 px-3 py-1.5 rounded-md font-medium transition-colors border border-indigo-500/30"
          >
            Upload Now
          </button>
        </div>
      ) : (
        <ul className={`flex flex-col gap-2 max-h-[50vh] overflow-y-auto custom-scrollbar pr-2 mb-2 ${deleteMutation.isPending ? 'pointer-events-none' : ''}`}>
          {docs.map((doc: {title: string}, i: number) => {
            const isChecked = selectedFiles.includes(doc.title);
            const isActive = activePdf === doc.title;
            const isBeingDeleted = deletingFile === doc.title;
            
            return (
              <li 
                key={i}
                className={`flex items-center gap-2 text-sm p-2 rounded-lg border transition-all group ${
                  isBeingDeleted 
                  ? 'opacity-40 pointer-events-none'
                  : isActive 
                  ? 'bg-indigo-900/20 border-indigo-500/50 shadow-[0_0_15px_rgba(99,102,241,0.15)] ring-1 ring-indigo-500/20' 
                  : 'bg-zinc-900/50 border-zinc-800/50 hover:border-zinc-700 hover:bg-zinc-800/80'
                }`}
              >
                {/* Checkbox Isolation Button */}
                <button 
                  onClick={(e) => { e.stopPropagation(); onToggleFile(doc.title); }}
                  className="shrink-0 p-1 hover:bg-zinc-800 rounded text-zinc-500 hover:text-indigo-400 transition-colors focus:outline-none"
                >
                  {isChecked 
                    ? <CheckSquare className="w-[16px] h-[16px] text-indigo-500" /> 
                    : <Square className="w-[16px] h-[16px]" />
                  }
                </button>
                
                {/* Visualizer Trigger */}
                <div 
                  className="flex flex-1 items-center gap-2 overflow-hidden cursor-pointer min-w-0" 
                  onClick={() => onSelectPdf(isActive ? null : doc.title)}
                >
                  {isBeingDeleted 
                    ? <Loader2 className="w-4 h-4 shrink-0 animate-spin text-red-400" />
                    : <FileText className={`w-4 h-4 shrink-0 transition-colors ${isActive ? 'text-indigo-400' : 'text-zinc-500 group-hover:text-zinc-400'}`} />
                  }
                  <span className={`truncate leading-tight text-xs transition-colors ${
                    isActive ? 'text-indigo-50 font-medium' : 'text-zinc-400 group-hover:text-zinc-300'
                  }`}>
                    {doc.title}
                  </span>
                </div>

                {/* Delete Button — only visible on row hover */}
                <button
                  onClick={(e) => handleDelete(e, doc.title)}
                  title={`Remove ${doc.title}`}
                  className="shrink-0 p-1 rounded opacity-0 group-hover:opacity-100 transition-all hover:bg-red-500/10 text-zinc-600 hover:text-red-400 focus:outline-none"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </li>
            );
          })}
        </ul>
      )}
      
      {docs.length > 0 && (
        <button 
          onClick={onTriggerUpload}
          className="mt-1 w-full flex items-center justify-center gap-2 bg-zinc-900/80 hover:bg-indigo-500/10 border border-zinc-800 border-dashed hover:border-indigo-500/50 transition-all text-sm py-2 px-3 rounded-lg text-zinc-400 hover:text-indigo-400 font-medium group"
        >
          <span className="text-lg font-bold leading-none mb-0.5 group-hover:scale-110 transition-transform">+</span> 
          Upload New Document
        </button>
      )}
    </div>
  );
}
