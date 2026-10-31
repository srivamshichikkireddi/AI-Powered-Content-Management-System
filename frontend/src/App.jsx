import React, { useState, useEffect } from 'react'

export default function App() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
        return res.json()
      })
      .then(data => {
        setHealth(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/30">
            AI
          </div>
          <span className="font-semibold text-lg tracking-tight">AICMS Portal</span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
            Sprint-1 Scaffold (M1)
          </span>
        </div>
        <div className="flex items-center space-x-4 text-sm text-slate-400">
          <span>Role: <strong className="text-slate-200">System Admin</strong></span>
          <div className="h-4 w-px bg-slate-800"></div>
          <span className="flex items-center space-x-1.5">
            <span className={`w-2.5 h-2.5 rounded-full ${health?.status === 'healthy' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`}></span>
            <span className="text-xs uppercase tracking-wider">{health ? health.status : 'Connecting...'}</span>
          </span>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-6 md:p-10 space-y-8">
        {/* Hero Card */}
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/60 rounded-2xl p-8 shadow-xl">
          <h1 className="text-3xl font-bold text-white tracking-tight mb-2">
            AI-Powered Content Management System
          </h1>
          <p className="text-slate-400 max-w-2xl leading-relaxed">
            Scalable document ingestion, automated classification with all-MiniLM-L6-v2 embeddings,
            PostgreSQL pgvector cosine semantic search, and strict pre-disclosure authorization.
          </p>

          <div className="mt-6 flex flex-wrap gap-3">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium text-sm transition shadow-lg shadow-indigo-600/30 flex items-center space-x-2"
            >
              <span>Swagger API Docs</span>
              <span>&rarr;</span>
            </a>
            <a
              href="http://localhost:8000/health"
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg font-medium text-sm transition flex items-center space-x-2"
            >
              <span>Raw Health JSON</span>
            </a>
          </div>
        </div>

        {/* System Status Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="text-xs uppercase font-semibold tracking-wider text-slate-400">PostgreSQL + pgvector</div>
            <div className="text-2xl font-bold text-white flex items-center space-x-2">
              <span className={`w-3 h-3 rounded-full ${health?.database === 'connected' ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
              <span>{health?.database || 'Connecting...'}</span>
            </div>
            <div className="text-xs text-slate-500">Vector cosine distance search & ACID store</div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="text-xs uppercase font-semibold tracking-wider text-slate-400">Redis & Celery</div>
            <div className="text-2xl font-bold text-white flex items-center space-x-2">
              <span className={`w-3 h-3 rounded-full ${health?.redis === 'connected' ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
              <span>{health?.redis || 'Connecting...'}</span>
            </div>
            <div className="text-xs text-slate-500">Async ingestion, parsing & embedding pipeline</div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="text-xs uppercase font-semibold tracking-wider text-slate-400">Environment & Version</div>
            <div className="text-2xl font-bold text-white flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-indigo-500"></span>
              <span>v{health?.version || '1.0.0'}</span>
            </div>
            <div className="text-xs text-slate-500">Mode: {health?.environment || 'development'}</div>
          </div>
        </div>

        {/* Milestone Roadmap */}
        <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-white">Sprint Milestones & Active Gates</h2>
          <div className="space-y-3 text-sm">
            <div className="flex items-center justify-between p-3 rounded-lg bg-indigo-950/40 border border-indigo-800/40">
              <div className="flex items-center space-x-3">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                <span className="font-medium text-slate-200">M0: Project Planning & Specs Extraction</span>
              </div>
              <span className="text-xs px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 font-semibold">Done</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-indigo-950/60 border border-indigo-600/50">
              <div className="flex items-center space-x-3">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-400 animate-ping"></span>
                <span className="font-medium text-white">M1: Scaffolding, Docker Architecture & CI Setup</span>
              </div>
              <span className="text-xs px-2.5 py-1 rounded bg-indigo-500/30 text-indigo-300 font-semibold">In Progress</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/40 border border-slate-800/60 opacity-60">
              <div className="flex items-center space-x-3">
                <span className="w-2.5 h-2.5 rounded-full bg-slate-600"></span>
                <span className="font-medium text-slate-400">M2: User Authentication, Sessions & Account Lockout (SR-008)</span>
              </div>
              <span className="text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-400">Next</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-4 px-6 text-center text-xs text-slate-500">
        AICMS Software Engineering Mini-Project &bull; PES University &bull; 2026
      </footer>
    </div>
  )
}
