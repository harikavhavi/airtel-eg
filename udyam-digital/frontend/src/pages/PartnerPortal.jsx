import { useState, useEffect } from 'react'
import axios from 'axios'
import { TrendingUp, Phone, Users, RefreshCw } from 'lucide-react'

const PRIORITY_COLOR = {
  HIGH: 'bg-red-100 text-red-700',
  MEDIUM: 'bg-amber-100 text-amber-700',
  LOW: 'bg-gray-100 text-gray-500',
}

export default function PartnerPortal() {
  const [leads, setLeads] = useState([])
  const [loading, setLoading] = useState(false)
  const [filter, setFilter] = useState('ALL')

  const fetchLeads = async () => {
    setLoading(true)
    try {
      const { data } = await axios.get('/propensity/leads?limit=100')
      setLeads(data)
    } catch { setLeads([]) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchLeads() }, [])

  const filtered = filter === 'ALL' ? leads : leads.filter(l => l.priority === filter)

  const stats = {
    total: leads.length,
    high: leads.filter(l => l.priority === 'HIGH').length,
    medium: leads.filter(l => l.priority === 'MEDIUM').length,
  }

  return (
    <div className="flex flex-col gap-5">
      {/* Header */}
      <div className="airtel-card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-gray-800">Partner Back-Office</h2>
            <p className="text-xs text-gray-400">Leads sorted by AI propensity score — call the high-priority ones first</p>
          </div>
          <button onClick={fetchLeads} disabled={loading} className="flex items-center gap-2 px-3 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''}/> Refresh
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Open Leads', value: stats.total, icon: Users, color: 'text-gray-700' },
            { label: 'High Priority', value: stats.high, icon: TrendingUp, color: 'text-red-600' },
            { label: 'Medium Priority', value: stats.medium, icon: Phone, color: 'text-amber-600' },
          ].map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="text-center">
              <Icon size={20} className={`mx-auto mb-1 ${color}`}/>
              <p className={`text-2xl font-bold ${color}`}>{value}</p>
              <p className="text-xs text-gray-400">{label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2">
        {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map(p => (
          <button
            key={p}
            onClick={() => setFilter(p)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter === p ? 'bg-red-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            {p}
          </button>
        ))}
      </div>

      {/* Lead cards */}
      {loading ? (
        <div className="airtel-card text-center py-10 text-gray-400">Loading leads…</div>
      ) : (
        <div className="space-y-3">
          {filtered.slice(0, 50).map(lead => (
            <div key={lead.lead_id} className="airtel-card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-semibold text-gray-800 text-sm">{lead.business_name}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${PRIORITY_COLOR[lead.priority]}`}>
                      {lead.priority}
                    </span>
                    <span className="text-xs text-gray-400">{lead.segment}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {lead.city}, {lead.state} · {lead.preferred_language} · {lead.contact_name}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Last stage: <strong>{lead.stage_reached}</strong>
                    {lead.drop_reason && <> · Dropped: {lead.drop_reason}</>}
                  </p>
                  {lead.products_of_interest && (
                    <p className="text-xs text-blue-600 mt-1">
                      Interested in: {lead.products_of_interest.split(';').join(', ')}
                    </p>
                  )}
                  {/* Top factors */}
                  <div className="flex gap-1.5 mt-2 flex-wrap">
                    {lead.top_factors.map((f, i) => (
                      <span key={i} className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">
                        {f}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="text-right flex-shrink-0">
                  <div className="w-14 h-14 rounded-full flex items-center justify-center border-4 border-gray-100 mb-1 mx-auto"
                    style={{
                      background: `conic-gradient(${lead.score >= 15 ? '#ef4444' : lead.score >= 7 ? '#f59e0b' : '#9ca3af'} ${lead.score * 3.6}deg, #f3f4f6 0deg)`
                    }}>
                    <span className="text-xs font-bold text-gray-800 bg-white rounded-full w-10 h-10 flex items-center justify-center">
                      {lead.score}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400">Score</p>
                  <div className="flex items-center gap-1 mt-2">
                    <span className="text-xs text-gray-400">
                      ₹{(lead.monthly_telecom_spend_inr || 0).toLocaleString('en-IN')}/mo spend
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

