import React from 'react'
import ComplaintForm from './components/ComplaintForm.jsx'
import AIAssistantPanel from './components/AIAssistantPanel.jsx'

export default function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>Log Customer Complaint</h1>
          <p className="subtitle">API &amp; FDF Quality Assurance Module</p>
        </div>
      </header>
      <main className="app-grid">
        <ComplaintForm />
        <AIAssistantPanel />
      </main>
    </div>
  )
}
