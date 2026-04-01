import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import QueryInput from '../components/QueryInput/QueryInput'
import ResponsePanel from '../components/ResponsePanel/ResponsePanel'
import { UploadPanel } from '../components/UploadPanel/UploadPanel'
import Sidebar from '../components/Sidebar/Sidebar'
import { submitQuery } from '../api/research'
import { useMutation, useQueryClient } from '@tanstack/react-query'

export default function QueryPage() {
  const [hasUploaded, setHasUploaded] = useState(false)
  const [hasQueried, setHasQueried] = useState(false)
  const [activePdf, setActivePdf] = useState<string | null>(null)
  const [selectedDocs, setSelectedDocs] = useState<string[]>([])
  const queryClient = useQueryClient()
  const answerRef = useRef<HTMLDivElement>(null)

  // GAP 9: Check for existing docs on mount to bypass hero upload screen
  useEffect(() => {
    if (!hasUploaded) {
      import('../api/research').then(({ fetchDocuments }) => {
        fetchDocuments()
          .then(data => {
            if (data.documents && data.documents.length > 0) {
              setHasUploaded(true)
            }
          })
          .catch(err => console.error("Failed to check existing docs:", err))
      })
    }
  }, [])

  const handleToggleDoc = (filename: string) => {
    setSelectedDocs(prev =>
      prev.includes(filename) ? prev.filter(f => f !== filename) : [...prev, filename]
    )
  }

  // GAP 9: Instantly invalidate document list cache after a successful upload
  const handleUploadSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['documents'] })
    setHasUploaded(true)
  }

  const { data, mutate, isPending, error } = useMutation({
    mutationFn: (query: string) => submitQuery({
      query,
      files: selectedDocs.length > 0 ? selectedDocs : undefined
    }),
    onMutate: () => {
      setHasQueried(true)
    }
  })

  useEffect(() => {
    if (hasQueried && isPending) {
      setTimeout(() => {
        answerRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 150)
    }
  }, [hasQueried, isPending])

  const leftColumnWidth = activePdf ? 'xl:w-[45%]' : 'xl:w-[350px]'

  return (
    <div className="w-full mx-auto min-h-screen flex flex-col items-center justify-start p-4 lg:px-8 relative lg:pt-8 bg-background">
      <div className="w-full max-w-[2400px] h-full flex flex-col xl:flex-row gap-8 xl:gap-12 items-start justify-center transition-all duration-700">

        {/* LEFT COLUMN: Sidebar + PDF Viewer */}
        <AnimatePresence mode="popLayout">
          {hasUploaded && (
            <motion.div
              layout
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, type: 'spring', bounce: 0.2 }}
              className={`w-full shrink-0 flex flex-col gap-6 transition-[width] duration-700 ease-in-out ${leftColumnWidth} sticky top-8`}
            >
              <AnimatePresence mode="sync">
                {!activePdf && (
                  <motion.div layoutId="upload-card">
                    <UploadPanel onUploadSuccess={handleUploadSuccess} />
                  </motion.div>
                )}
              </AnimatePresence>

              <motion.div
                layout
                className="rounded-2xl bg-[#1c1c1e] border border-zinc-800/80 p-5 shadow-2xl flex flex-col min-h-[400px] max-h-[calc(100vh-4rem)] relative"
              >
                <div className={`${activePdf ? 'max-h-[15vh]' : ''} overflow-y-auto mb-4 border-b border-zinc-800/80 pb-4 custom-scrollbar`}>
                  <Sidebar
                    activePdf={activePdf}
                    onSelectPdf={setActivePdf}
                    selectedFiles={selectedDocs}
                    onToggleFile={handleToggleDoc}
                    onTriggerUpload={() => setHasUploaded(false)}
                  />
                </div>

                <AnimatePresence>
                  {activePdf && (
                    <motion.div
                      key="pdf-viewer"
                      initial={{ opacity: 0, scale: 0.98 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="w-full flex-1 flex flex-col rounded-xl overflow-hidden border border-zinc-800 shadow-inner bg-zinc-900 min-h-[500px] relative"
                    >
                      <button
                        onClick={() => setActivePdf(null)}
                        className="absolute top-3 right-3 p-1.5 bg-black/60 hover:bg-black/90 backdrop-blur-md rounded-lg text-zinc-400 hover:text-white transition-all z-10 border border-zinc-700/50 shadow-xl"
                        title="Close PDF Viewer"
                      >
                        <X className="w-5 h-5" />
                      </button>

                      {/* GAP 10: Use relative /api URL instead of hardcoded localhost:8000 */}
                      <iframe
                        src={`/api/documents/view/${encodeURIComponent(activePdf)}#toolbar=0&navpanes=0`}
                        className="w-full flex-1 h-full"
                        title={activePdf}
                      />
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* RIGHT COLUMN: Ask + Answer */}
        <motion.div
          layout
          className={`flex flex-col gap-8 transition-all duration-700 ease-in-out flex-1 min-w-[300px] w-full ${!hasUploaded ? 'max-w-4xl mx-auto items-center mt-12' : ''}`}
        >
          <AnimatePresence mode="sync">
            {!hasUploaded && (
              <motion.div layoutId="upload-card" className="w-full z-10 relative">
                <UploadPanel onUploadSuccess={handleUploadSuccess} />
              </motion.div>
            )}
          </AnimatePresence>

          <motion.div
            layoutId="query-card"
            className={`w-full z-50 ${hasUploaded && hasQueried ? 'sticky top-4' : ''} ${hasUploaded && !hasQueried ? 'mt-[15vh] max-w-4xl mx-auto' : ''}`}
            transition={{ type: 'spring', bounce: 0.2, duration: 0.8 }}
          >
            {!hasQueried && (
              <div className="mb-6 px-4 text-center">
                <h2 className="text-4xl font-bold tracking-tight text-white mb-4 bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">Ask a Question</h2>
                <p className="text-zinc-400 text-lg">
                  Search the active knowledge base for answers grounded in your documents.
                </p>
              </div>
            )}

            <div className={`bg-[#1c1c1e] p-2 rounded-2xl shadow-2xl relative ${hasQueried ? 'border-2 border-indigo-500/30' : 'border border-zinc-800 backdrop-blur-md'}`}>
              {hasQueried && (
                <div className="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-2 px-3 pt-3 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
                    Active Research Thread
                  </div>
                  <div className="text-[10px] text-zinc-500 tracking-wider">
                    {selectedDocs.length > 0 ? `FILTERING ${selectedDocs.length} DOCS` : 'ALL DOCS'}
                  </div>
                </div>
              )}
              <QueryInput onSubmit={mutate} isLoading={isPending} />
            </div>

            {error && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-4 mt-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 shadow-xl">
                Error: {(error as any).message}
              </motion.div>
            )}
          </motion.div>

          <AnimatePresence mode="wait">
            {hasQueried && (isPending || data) && (
              <motion.div
                ref={answerRef}
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, type: 'spring', duration: 0.8 }}
                className="w-full bg-[#18181b] border border-zinc-800/80 rounded-2xl p-6 lg:p-10 shadow-xl scroll-mt-32 mb-32"
              >
                <ResponsePanel data={data} isLoading={isPending} />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

      </div>
    </div>
  )
}
