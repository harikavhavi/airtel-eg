import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { Send, Bot, User, Loader2 } from 'lucide-react'

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिंदी (Hindi)' },
  { code: 'te', label: 'తెలుగు (Telugu)' },
]

const SESSION_ID = 'session-' + Math.random().toString(36).slice(2)

export default function Advisor() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "👋 Namaste! I'm Digi Saathi, your Accel Business advisor. I'll help you find the perfect bundle for your business in just a few questions. What kind of business do you run?",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [language, setLanguage] = useState('en')
  const [bundle, setBundle] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async () => {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: userMsg }])
    setLoading(true)

    try {
      const { data } = await axios.post('/advisor/chat', {
        session_id: SESSION_ID,
        message: userMsg,
        language,
      })
      setMessages(prev => [...prev, { role: 'assistant', text: data.reply }])
      if (data.bundle) setBundle(data.bundle)
    } catch (e) {
      const errText = e.response?.data?.detail || e.message || '⚠️ Connection error. Please check backend.'
      setMessages(prev => [
        ...prev,
        { role: 'assistant', text: `⚠️ ${errText}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Language selector */}
      <div className="airtel-card flex items-center gap-3">
        <span className="text-sm text-gray-500 font-medium">Language:</span>
        {LANGUAGES.map(l => (
          <button
            key={l.code}
            onClick={() => setLanguage(l.code)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              language === l.code
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {l.label}
          </button>
        ))}
      </div>

      {/* Chat window */}
      <div className="airtel-card flex flex-col h-[480px]">
        <div className="flex-1 overflow-y-auto space-y-4 pr-1">
          {messages.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  m.role === 'assistant' ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'
                }`}
              >
                {m.role === 'assistant' ? <Bot size={16} /> : <User size={16} />}
              </div>
              <div
                className={`max-w-[78%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                  m.role === 'assistant'
                    ? 'bg-gray-50 text-gray-800 rounded-tl-none'
                    : 'bg-red-600 text-white rounded-tr-none'
                }`}
              >
                {m.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center">
                <Bot size={16} />
              </div>
              <div className="bg-gray-50 rounded-2xl rounded-tl-none px-4 py-3">
                <Loader2 size={16} className="animate-spin text-red-500" />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="flex gap-2 mt-4 pt-4 border-t border-gray-100">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && send()}
            placeholder="Type your reply..."
            className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
          />
          <button onClick={send} disabled={!input.trim() || loading} className="airtel-btn px-4 py-2.5">
            <Send size={16} />
          </button>
        </div>
      </div>

      {/* Bundle preview (shown when advisor completes profile) */}
      {bundle && (
        <div className="airtel-card border-l-4 border-red-500">
          <h3 className="font-bold text-gray-800 mb-3 text-base">
            📦 Recommended Bundle
            <span className="ml-2 text-xs font-normal text-gray-400 uppercase tracking-wide">
              {bundle.segment} · Tier {bundle.city_tier}
            </span>
          </h3>
          <div className="space-y-2 mb-4">
            {bundle.line_items.map(item => (
              <div key={item.product_id} className="flex justify-between text-sm">
                <span className="text-gray-700">{item.product_name}</span>
                <span className="font-medium text-gray-900">
                  ₹{item.price_per_unit_inr.toLocaleString('en-IN')}/mo
                </span>
              </div>
            ))}
          </div>
          <div className="flex justify-between items-center border-t pt-3">
            <div>
              <p className="text-lg font-bold text-red-600">
                ₹{bundle.total_monthly_inr.toLocaleString('en-IN')}/month
              </p>
              {bundle.total_setup_inr > 0 && (
                <p className="text-xs text-gray-500">
                  + ₹{bundle.total_setup_inr.toLocaleString('en-IN')} one-time setup
                </p>
              )}
              <p className="text-xs text-gray-400 mt-1">{bundle.activation_note}</p>
            </div>
            <a
              href={`/quote?bundle=${encodeURIComponent(JSON.stringify(bundle))}`}
              className="airtel-btn text-sm"
            >
              View Full Quote →
            </a>
          </div>
          {bundle.no_gstin_tip && (
            <div className="mt-3 bg-amber-50 border border-amber-200 rounded-xl px-4 py-2 text-xs text-amber-700">
              💡 {bundle.no_gstin_tip}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

