import { useState } from 'react'
import axios from 'axios'
import { Search, RefreshCw, CheckCircle } from 'lucide-react'

const STATES = [
  'ACCEPTED', 'KYC_SUBMITTED', 'KYC_VERIFIED',
  'ORDER_PLACED', 'INSTALLATION_SCHEDULED', 'TECH_VISIT_DONE', 'ACTIVATED'
]

const STATE_ICONS = {
  ACCEPTED: '📋', KYC_SUBMITTED: '📄', KYC_VERIFIED: '✅',
  ORDER_PLACED: '🔧', INSTALLATION_SCHEDULED: '📅',
  TECH_VISIT_DONE: '🛠️', ACTIVATED: '🎉'
}

export default function Tracker() {
  const [orderId, setOrderId] = useState('')
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [advancing, setAdvancing] = useState(false)

  const lookup = async (id) => {
    const oid = id || orderId
    if (!oid.trim()) return
    setLoading(true)
    try {
      const { data } = await axios.get(`/tracker/${oid.trim()}`)
      setStatus(data)
    } catch { setStatus(null) }
    finally { setLoading(false) }
  }

  const advance = async () => {
    if (!status) return
    setAdvancing(true)
    try {
      await axios.post(`/tracker/${status.order_id}/advance`)
      await lookup(status.order_id)
    } finally { setAdvancing(false) }
  }

  const currentIdx = status ? STATES.indexOf(status.current_state) : -1

  return (
    <div className="flex flex-col gap-5">
      <div className="airtel-card">
        <h2 className="text-lg font-bold text-gray-800 mb-4">Track Your Order</h2>
        <div className="flex gap-3">
          <input
            value={orderId}
            onChange={e => setOrderId(e.target.value.toUpperCase())}
            placeholder="e.g. ORD-A1B2C3D4"
            className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm font-mono"
          />
          <button onClick={() => lookup()} disabled={loading} className="airtel-btn flex items-center gap-2">
            <Search size={15}/> {loading ? 'Looking…' : 'Track'}
          </button>
        </div>
      </div>

      {status && (
        <>
          <div className="airtel-card">
            <div className="flex items-start justify-between mb-5">
              <div>
                <h3 className="font-bold text-gray-800 text-lg">{status.business_name || 'Your Order'}</h3>
                <p className="text-xs text-gray-400 font-mono mt-0.5">{status.order_id}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-400">Estimated activation</p>
                <p className="font-semibold text-gray-700">{status.estimated_activation}</p>
              </div>
            </div>

            {/* Progress bar */}
            <div className="mb-6">
              <div className="flex justify-between mb-2">
                <span className="text-xs text-gray-500">Progress</span>
                <span className="text-xs font-semibold text-red-600">{status.progress_pct}%</span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-red-500 to-red-400 rounded-full transition-all duration-500"
                  style={{ width: `${status.progress_pct}%` }}
                />
              </div>
            </div>

            {/* State timeline */}
            <div className="space-y-3">
              {STATES.map((s, i) => {
                const isDone = i < currentIdx
                const isCurrent = i === currentIdx
                const isPending = i > currentIdx
                return (
                  <div key={s} className={`flex items-center gap-4 p-3 rounded-xl transition-colors ${isCurrent ? 'bg-red-50 border border-red-100' : ''}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm flex-shrink-0 ${
                      isDone ? 'bg-green-100 text-green-600' : isCurrent ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-400'
                    }`}>
                      {isDone ? '✓' : STATE_ICONS[s]}
                    </div>
                    <div className="flex-1">
                      <p className={`text-sm font-medium ${isPending ? 'text-gray-400' : 'text-gray-800'}`}>
                        {s.replace(/_/g, ' ')}
                      </p>
                      {isCurrent && (
                        <p className="text-xs text-red-600 mt-0.5">{status.message}</p>
                      )}
                    </div>
                    {isDone && <CheckCircle size={15} className="text-green-500 flex-shrink-0"/>}
                  </div>
                )
              })}
            </div>

            {/* Demo: advance button */}
            {status.current_state !== 'ACTIVATED' && (
              <div className="mt-5 pt-4 border-t border-gray-100">
                <p className="text-xs text-gray-400 mb-2">🎬 Demo: simulate next status update</p>
                <button onClick={advance} disabled={advancing} className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
                  <RefreshCw size={14} className={advancing ? 'animate-spin' : ''}/> Advance to Next Step
                </button>
              </div>
            )}

            <div className="mt-4 pt-4 border-t text-xs text-gray-400">
              Need help? Call <strong className="text-gray-600">{status.support_number}</strong> — available 24×7
            </div>
          </div>
        </>
      )}

      {/* Demo: create a sample order */}
      <div className="airtel-card bg-gray-50">
        <p className="text-sm font-medium text-gray-600 mb-3">🎬 Demo: Create a sample order to track</p>
        <button
          onClick={async () => {
            const { data } = await axios.post('/tracker/create', {
              business_name: 'Balaji Dental Care LLP',
              max_install_days: 7,
              total_monthly_inr: 6216,
              segment: 'prof'
            })
            setOrderId(data.order_id)
            lookup(data.order_id)
          }}
          className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100"
        >
          Create Sample Order
        </button>
      </div>
    </div>
  )
}

