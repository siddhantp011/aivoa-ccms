import React, { useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { extractFromFile, extractFromText } from '../store/complaintSlice'
import { sendMessage } from '../store/chatSlice'

export default function AIAssistantPanel() {
  const dispatch = useDispatch()
  const fileInputRef = useRef(null)
  const [pastedText, setPastedText] = useState('')
  const [chatInput, setChatInput] = useState('')
  const [dragActive, setDragActive] = useState(false)

  const { status, progressMessage, id: complaintId } = useSelector((s) => s.complaint)
  const { messages, sending } = useSelector((s) => s.chat)

  const handleFile = (file) => {
    if (!file) return
    dispatch(extractFromFile(file))
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    handleFile(e.dataTransfer.files?.[0])
  }

  const handlePasteSubmit = () => {
    if (!pastedText.trim()) return
    dispatch(extractFromText(pastedText))
  }

  const handleChatSend = () => {
    if (!chatInput.trim() || !complaintId) return
    dispatch(sendMessage({ complaintId, message: chatInput }))
    setChatInput('')
  }

  const extracting = status === 'extracting'

  return (
    <section className="panel ai-panel">
      <div className="panel-header-row">
        <h2>✦ AI Complaint Intake Assistant</h2>
        <span className="beta-badge">BETA</span>
      </div>

      <div
        className={`dropzone ${dragActive ? 'active' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="dropzone-icon">⬆</div>
        <p>Drag &amp; drop complaint document here<br />or <span className="link">click to browse</span></p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt,.eml"
          hidden
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
      </div>

      <div className="or-divider">OR</div>

      <textarea
        className="paste-textarea"
        placeholder="Paste Complaint Text / Email"
        value={pastedText}
        onChange={(e) => setPastedText(e.target.value)}
      />
      <button className="btn btn-primary btn-block" onClick={handlePasteSubmit} disabled={extracting}>
        {extracting ? 'Extracting...' : 'Extract from Pasted Text'}
      </button>

      <p className="supported-formats">
        Supported formats: PDF, DOCX, TXT, EML · Max file size: 10MB
      </p>

      {extracting && (
        <div className="extraction-progress">
          <div className="progress-track indeterminate"><div className="progress-fill-anim" /></div>
          <p>{progressMessage}</p>
        </div>
      )}

      <div className="chat-section">
        <div className="chat-header">AI ASSISTANT</div>
        <div className="chat-messages">
          {messages.map((m, i) => (
            <div key={i} className={`chat-bubble ${m.role}`}>{m.text}</div>
          ))}
          {sending && <div className="chat-bubble assistant typing">Thinking...</div>}
        </div>
        <div className="chat-input-row">
          <input
            className="chat-input"
            placeholder={complaintId ? 'Ask me anything about this complaint...' : 'Extract a complaint first to chat about it'}
            value={chatInput}
            disabled={!complaintId}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleChatSend()}
          />
          <button className="btn-send" disabled={!complaintId} onClick={handleChatSend}>➤</button>
        </div>
        <p className="disclaimer">AI responses may contain errors. Please verify information.</p>
      </div>
    </section>
  )
}
