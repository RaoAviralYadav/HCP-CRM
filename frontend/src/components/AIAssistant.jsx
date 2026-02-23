import React, { useState, useRef, useEffect } from 'react'
import { useDispatch } from 'react-redux'
import axios from 'axios'
import { setFormFromAI } from '../store/interactionSlice'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const QUICK_PROMPTS = [
  "Met Dr. Smith today, discussed Product X efficacy. Sentiment was positive. Shared brochures.",
  "Had a call with Dr. Patel. He was negative about the new drug. Distributed 5 samples.",
  "Meeting with Dr. Williams about oncology trial. Neutral sentiment. Follow up next week.",
]

export default function AIAssistant() {
  const dispatch = useDispatch()
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "👋 Hello! I'm your AI assistant. Describe your HCP interaction in natural language and I'll fill the form for you automatically.\n\nTry: *\"Today I met Dr. Smith and discussed Product X efficacy. The sentiment was positive and I shared brochures.\"*",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text) => {
    const userText = (text || input).trim()
    if (!userText || loading) return

    const userMsg = { role: 'user', content: userText }
    const updatedMessages = [...messages, userMsg]
    setMessages(updatedMessages)
    setInput('')
    setLoading(true)

    try {
      // Build conversation history (excluding the initial greeting)
      const history = updatedMessages
        .slice(1) // skip initial greeting
        .slice(0, -1) // skip current user message
        .map(m => ({ role: m.role, content: m.content }))

      const res = await axios.post(`${API_URL}/api/chat`, {
        message: userText,
        conversation_history: history,
      })

      const { response, form_data } = res.data

      if (form_data) {
        dispatch(setFormFromAI(form_data))
      }

      setMessages(prev => [...prev, { role: 'assistant', content: response }])
    } catch (err) {
      console.error(err)
      const errMsg = err.response?.data?.detail || 'Connection error. Is the backend running?'
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `⚠️ Error: ${errMsg}`,
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const renderContent = (text) => {
    // Simple markdown-like rendering for bold and italic
    return text
      .split('\n')
      .map((line, i) => {
        const html = line
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
        return <p key={i} dangerouslySetInnerHTML={{ __html: html }} />
      })
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-header-icon">✦</div>
        <div>
          <h2 className="panel-title">AI Assistant</h2>
          <p className="chat-subtitle">Log interaction via chat</p>
        </div>
        <div className={`status-dot ${loading ? 'thinking' : 'ready'}`}></div>
      </div>

      <div className="messages-area">
        {messages.map((msg, i) => (
          <div key={i} className={`message message-${msg.role}`}>
            {msg.role === 'assistant' && (
              <div className="avatar">✦</div>
            )}
            <div className="bubble">
              {renderContent(msg.content)}
            </div>
            {msg.role === 'user' && (
              <div className="avatar user-avatar">You</div>
            )}
          </div>
        ))}

        {loading && (
          <div className="message message-assistant">
            <div className="avatar">✦</div>
            <div className="bubble thinking-bubble">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {messages.length <= 1 && (
        <div className="quick-prompts">
          <p className="quick-label">Try these examples:</p>
          {QUICK_PROMPTS.map((p, i) => (
            <button key={i} className="quick-btn" onClick={() => sendMessage(p)}>
              {p}
            </button>
          ))}
        </div>
      )}

      <div className="chat-input-area">
        <textarea
          ref={textareaRef}
          className="chat-input"
          placeholder="Describe interaction... (Enter to send, Shift+Enter for new line)"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
          disabled={loading}
        />
        <button
          className={`send-btn ${loading ? 'disabled' : ''}`}
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
        >
          {loading ? '⏳' : '✦ Log'}
        </button>
      </div>
    </div>
  )
}