import QueryInput from '../components/QueryInput/QueryInput'
import ResponsePanel from '../components/ResponsePanel/ResponsePanel'
import { UploadPanel } from '../components/UploadPanel/UploadPanel'
import { submitQuery } from '../api/research'
import { useMutation } from '@tanstack/react-query'

export default function QueryPage() {
  const { data, mutate, isPending, error } = useMutation({
    mutationFn: (query: string) => submitQuery({ query })
  })

  return (
    <div className="flex flex-col gap-8 max-w-4xl mx-auto">
      <UploadPanel />
      
      <section className="flex flex-col gap-4">
        <h2 className="text-3xl font-bold tracking-tight text-white">Ask a Question</h2>
        <p className="text-muted-foreground text-zinc-400">
          Search the knowledge base for answers grounded in PDF context.
        </p>
        <QueryInput onSubmit={mutate} isLoading={isPending} />
        {error && (
          <div className="p-4 rounded-md bg-red-500/10 border border-red-500/20 text-red-500">
            An error occurred: {error.message}
          </div>
        )}
      </section>

      {(isPending || data) && (
        <section className="bg-zinc-900 border border-border rounded-xl p-6 shadow-xl relative overflow-hidden">
          <ResponsePanel data={data} isLoading={isPending} />
        </section>
      )}
    </div>
  )
}
