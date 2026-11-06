import { useState } from 'react'
import axios from 'axios'
import { CheckCircle, AlertCircle, ShoppingCart } from 'lucide-react'

const CORE_PIDS = new Set(['P01','P02','P03','P04','P05','P06','P07','P08'])

export default function Quote() {
  const [form, setForm] = useState({
    city_tier: '1',
    has_gstin: true,
    employee_count: 10,
    num_sites: 1,
    segment: 'prof',
  })

  const PRESET_BUNDLES = {
    micro: [
      { product_id: 'P01', quantity: 1 },
      { product_id: 'P07', quantity: 1 },
      { product_id: 'P18', quantity: 1 },
    ],
    prof: [
      { product_id: 'P02', quantity: 1 },
      { product_id: 'P08', quantity: 2 },
      { product_id: 'P16', quantity: 5 },
      { product_id: 'P20', quantity: 5 },
      { product_id: 'P22', quantity: 1 },
      { product_id: 'P12', quantity: 2 },
    ],
    multi: [
      { product_id: 'P02', quantity: 3 },
      { product_id: 'P09', quantity: 3 },
      { product_id: 'P08', quantity: 4 },
      { product_id: 'P23', quantity: 6 },
      { product_id: 'P16', quantity: 10 },
    ],
    mfg: [
      { product_id: 'P05', quantity: 1 },
      { product_id: 'P08', quantity: 5 },
      { product_id: 'P21', quantity: 1 },
      { product_id: 'P20', quantity: 10 },
    ],
  }

  const [quote, setQuote] = useState(null)
  const [disabled, setDisabled] = useState(new Set())
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState([])
  const [orderCreated, setOrderCreated] = useState(null)

  const fetchQuote = async () => {
    setLoading(true)
    setErrors([])
    try {
      const items = PRESET_BUNDLES[form.segment] || PRESET_BUNDLES['prof']
      const { data } = await axios.post('/quote/generate', {
        items,
        city_tier: form.city_tier,
        has_gstin: form.has_gstin,
        employee_count: parseInt(form.employee_count),
        num_sites: parseInt(form.num_sites),
        segment: form.segment,
      })
      setQuote(data)
      setDisabled(new Set())
      setErrors(data.errors || [])
    } catch (e) {
      setErrors(['Failed to generate quote. Is the backend running?'])
    } finally {
      setLoading(false)
    }
  }

  const toggleItem = (pid) => {
    if (CORE_PIDS.has(pid)) return // cannot remove core products
    setDisabled(prev => {
      const next = new Set(prev)
      next.has(pid) ? next.delete(pid) : next.add(pid)
      return next
    })
  }

  const activeItems = quote?.line_items?.filter(i => !disabled.has(i.product_id)) || []
  const totalMonthly = activeItems.reduce((s, i) => s + i.monthly_inr, 0)
  const totalSetup = activeItems.reduce((s, i) => s + i.setup_inr, 0)

  const createOrder = async () => {
    try {
      const { data } = await axios.post('/tracker/create', {
        business_name: 'My Business',
        max_install_days: Math.max(...activeItems.map(i => i.install_days), 1),
        total_monthly_inr: totalMonthly,
        segment: form.segment,
      })
      setOrderCreated(data.order_id)
    } catch (e) {
      alert('Could not create order. Is backend running?')
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <div className="airtel-card">
        <h2 className="text-lg font-bold text-gray-800 mb-4">Configure Your Quote</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Segment</label>
            <select
              value={form.segment}
              onChange={e => setForm(f => ({ ...f, segment: e.target.value }))}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            >
              <option value="micro">Micro retail & services</option>
              <option value="prof">Professional offices</option>
              <option value="multi">Multi-site businesses</option>
              <option value="mfg">Small manufacturers</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">City Tier</label>
            <select
              value={form.city_tier}
              onChange={e => setForm(f => ({ ...f, city_tier: e.target.value }))}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            >
              <option value="1">Tier 1</option>
              <option value="2">Tier 2</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Employees</label>
            <input
              type="number"
              value={form.employee_count}
              onChange={e => setForm(f => ({ ...f, employee_count: e.target.value }))}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Sites</label>
            <input
              type="number"
              value={form.num_sites}
              onChange={e => setForm(f => ({ ...f, num_sites: e.target.value }))}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div className="flex items-end">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={form.has_gstin}
                onChange={e => setForm(f => ({ ...f, has_gstin: e.target.checked }))}
                className="w-4 h-4 accent-red-600"
              />
              <span className="text-sm text-gray-700">Has GSTIN</span>
            </label>
          </div>
          <div className="flex items-end">
            <button onClick={fetchQuote} disabled={loading} className="airtel-btn w-full">
              {loading ? 'Generating…' : 'Generate Quote'}
            </button>
          </div>
        </div>
      </div>

      {errors.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 space-y-1">
          {errors.map((e, i) => (
            <p key={i} className="text-sm text-amber-700 flex items-center gap-2">
              <AlertCircle size={14} /> {e}
            </p>
          ))}
        </div>
      )}

      {quote && activeItems.length > 0 && (
        <div className="airtel-card">
          <h3 className="font-bold text-gray-800 mb-1">Your Personalised Bundle</h3>
          <p className="text-xs text-gray-400 mb-4">
            Toggle optional add-ons on/off. Core connectivity products are always included.
          </p>

          <div className="divide-y divide-gray-50">
            {quote.line_items.map(item => {
              const isCore = CORE_PIDS.has(item.product_id)
              const isOff = disabled.has(item.product_id)
              return (
                <div
                  key={item.product_id}
                  className={`flex items-center justify-between py-3 transition-opacity ${isOff ? 'opacity-40' : ''}`}
                >
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => toggleItem(item.product_id)}
                      disabled={isCore}
                      className={`w-10 h-6 rounded-full transition-colors flex items-center px-1 ${
                        !isOff ? 'bg-red-500' : 'bg-gray-200'
                      } ${isCore ? 'cursor-default' : 'cursor-pointer'}`}
                    >
                      <span
                        className={`w-4 h-4 bg-white rounded-full shadow transition-transform ${
                          !isOff ? 'translate-x-4' : ''
                        }`}
                      />
                    </button>
                    <div>
                      <p className="text-sm font-medium text-gray-800">
                        {item.product_name}
                        {item.quantity > 1 && (
                          <span className="text-gray-400 font-normal"> ×{item.quantity}</span>
                        )}
                        {isCore && (
                          <span className="ml-2 text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded-full">
                            Core
                          </span>
                        )}
                      </p>
                      <p className="text-xs text-gray-400">{item.category} · {item.unit}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-gray-900">
                      ₹{item.monthly_inr.toLocaleString('en-IN')}/mo
                    </p>
                    {item.setup_inr > 0 && (
                      <p className="text-xs text-gray-400">
                        +₹{item.setup_inr.toLocaleString('en-IN')} setup
                      </p>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          <div className="border-t pt-4 mt-2">
            <div className="flex justify-between items-start mb-1">
              <div>
                <p className="text-2xl font-bold text-red-600">
                  ₹{totalMonthly.toLocaleString('en-IN')}<span className="text-base font-normal text-gray-400">/month</span>
                </p>
                {totalSetup > 0 && (
                  <p className="text-sm text-gray-500">
                    + ₹{totalSetup.toLocaleString('en-IN')} one-time setup fee
                  </p>
                )}
                <p className="text-xs text-gray-400 mt-1">{quote.activation_note}</p>
              </div>
              <div className="text-right text-sm text-gray-500">
                <p>{quote.max_contract_months}-month contract</p>
              </div>
            </div>
            {orderCreated ? (
              <div className="mt-4 bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-3">
                <CheckCircle className="text-green-500" size={20} />
                <div>
                  <p className="font-semibold text-green-800">Order Created!</p>
                  <p className="text-sm text-green-600">
                    Order ID: <strong>{orderCreated}</strong> — go to the Tracker tab to follow progress.
                  </p>
                </div>
              </div>
            ) : (
              <button onClick={createOrder} className="airtel-btn mt-4 w-full flex items-center justify-center gap-2">
                <ShoppingCart size={16} /> Accept & Proceed to KYC
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

