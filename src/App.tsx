import QueryPage from './pages/QueryPage'

function App() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border/40 bg-zinc-950/50 backdrop-blur sticky top-0 z-50">
        <div className="w-full px-6 lg:px-12 h-16 flex items-center">
          <h1 className="text-xl font-semibold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
            AI Research Assistant
          </h1>
        </div>
      </header>
      
      <main className="w-full">
        <QueryPage />
      </main>
    </div>
  )
}

export default App
