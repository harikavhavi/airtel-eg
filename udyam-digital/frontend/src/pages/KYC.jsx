import { useState } from 'react'
import axios from 'axios'
import { Upload, CheckCircle, AlertTriangle, Search, ShieldCheck } from 'lucide-react'

const STEPS = ['Consent', 'GSTIN Lookup', 'Udyam Lookup', 'Upload Documents', 'Done']

export default function KYC() {
  const [step, setStep] = useState(0)
  const [consents, setConsents] = useState({ kyc: false, order: false, marketing: false })
  const [gstin, setGstin] = useState('')
  const [udyam, setUdyam] = useState('')
  const [gstinResult, setGstinResult] = useState(null)
  const [udyamResult, setUdyamResult] = useState(null)
  const [signatoryName, setSignatoryName] = useState('')
  const [docResults, setDocResults] = useState({})
  const [uploading, setUploading] = useState({})

  const canProceedConsent = consents.kyc && consents.order

  const lookupGstin = async () => {
    if (!gstin.trim()) return
    try {
      const { data } = await axios.get(`/kyc/gstin/${gstin.trim()}`)
      setGstinResult(data)
    } catch { setGstinResult({ status: 'error', message: 'Lookup failed' }) }
  }

  const lookupUdyam = async () => {
    if (!udyam.trim()) return
    try {
      const { data } = await axios.get(`/kyc/udyam/${udyam.trim()}`)
      setUdyamResult(data)
    } catch { setUdyamResult({ status: 'error', message: 'Lookup failed' }) }
  }

  const uploadDoc = async (docType, file) => {
    setUploading(u => ({ ...u, [docType]: true }))
    const fd = new FormData()
    fd.append('doc_type', docType)
    fd.append('gstin_entered', gstin)
    fd.append('udyam_entered', udyam)
    fd.append('signatory_name_entered', signatoryName)
    fd.append('file', file)
    try {
      const { data } = await axios.post('/kyc/extract_document', fd)
      setDocResults(r => ({ ...r, [docType]: data }))
    } catch {
      setDocResults(r => ({ ...r, [docType]: { status: 'error', flags: ['Upload failed'] } }))
    } finally {
      setUploading(u => ({ ...u, [docType]: false }))
    }
  }

  const DOC_TYPES = [
    { key: 'gstin_certificate', label: 'GST Certificate' },
    { key: 'udyam_certificate', label: 'Udyam Certificate' },
    { key: 'signatory_id',      label: 'Signatory ID (Aadhaar / PAN)' },
    { key: 'address_proof',     label: 'Address Proof (≤90 days old)' },
  ]

  const allDocsUploaded = DOC_TYPES.every(d => docResults[d.key])
  const anyFlagged = Object.values(docResults).some(r => r.status === 'flagged')

  return (
    <div className="flex flex-col gap-5">
      {/* Progress steps */}
      <div className="airtel-card">
        <div className="flex items-center justify-between">
          {STEPS.map((s, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
                i < step ? 'step-done' : i === step ? 'step-active' : 'step-pending'
              }`}>
                {i < step ? '✓' : i + 1}
              </div>
              <span className={`text-xs hidden sm:block font-medium ${i === step ? 'text-red-600' : 'text-gray-400'}`}>
                {s}
              </span>
              {i < STEPS.length - 1 && <div className="flex-1 h-px bg-gray-200 mx-2 w-8 hidden sm:block" />}
            </div>
          ))}
        </div>
      </div>

      {/* Step 0 — Consent */}
      {step === 0 && (
        <div className="airtel-card">
          <div className="flex items-center gap-2 mb-4">
            <ShieldCheck className="text-red-500" size={20} />
            <h2 className="text-lg font-bold text-gray-800">Before we begin</h2>
          </div>
          <p className="text-sm text-gray-500 mb-5">
            We need your consent for each purpose below (DPDP Act 2023). You can withdraw optional
            consent at any time from your account settings.
          </p>

          {[
            { key: 'kyc', required: true,  label: 'Identity & KYC verification (required)', desc: 'GSTIN, Udyam, signatory ID and address proof — used solely to verify your business and activate services.' },
            { key: 'order', required: true,  label: 'Order & service management (required)', desc: 'Your contact details for installation updates and support.' },
            { key: 'marketing', required: false, label: 'Marketing communications (optional)', desc: 'Occasional product offers via SMS/WhatsApp.' },
          ].map(({ key, required, label, desc }) => (
            <label key={key} className="flex gap-3 mb-4 cursor-pointer">
              <input
                type="checkbox"
                checked={consents[key]}
                onChange={e => setConsents(c => ({ ...c, [key]: e.target.checked }))}
                className="mt-1 w-4 h-4 accent-red-600 flex-shrink-0"
              />
              <div>
                <p className="text-sm font-semibold text-gray-800">{label}</p>
                <p className="text-xs text-gray-500">{desc}</p>
              </div>
            </label>
          ))}

          <div className="bg-blue-50 border border-blue-100 rounded-xl px-4 py-3 text-xs text-blue-700 mb-5">
            📌 Aadhaar images are not retained after verification — only a masked number is stored.<br/>
            📌 OCR runs locally; no document image is sent to any external service.<br/>
            📌 Right to access, correct or erase: <strong>privacy@accel.in</strong>
          </div>

          <button
            onClick={() => setStep(1)}
            disabled={!canProceedConsent}
            className="airtel-btn w-full"
          >
            Continue →
          </button>
        </div>
      )}

      {/* Step 1 — GSTIN Lookup */}
      {step === 1 && (
        <div className="airtel-card">
          <h2 className="text-lg font-bold text-gray-800 mb-4">Verify your GSTIN</h2>
          <div className="flex gap-3 mb-4">
            <input
              value={gstin}
              onChange={e => setGstin(e.target.value.toUpperCase())}
              placeholder="Enter 15-character GSTIN"
              className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm font-mono uppercase tracking-widest"
              maxLength={15}
            />
            <button onClick={lookupGstin} className="airtel-btn flex items-center gap-2">
              <Search size={15}/> Verify
            </button>
          </div>
          {gstinResult && (
            <div className={`rounded-xl p-4 text-sm ${gstinResult.status === 'active' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              {gstinResult.status === 'active' ? (
                <>
                  <p className="font-semibold text-green-800 flex items-center gap-2"><CheckCircle size={15}/> GSTIN Active</p>
                  <p className="text-green-700 mt-1"><strong>{gstinResult.legal_name}</strong></p>
                  <p className="text-green-600 text-xs mt-1">{gstinResult.address}</p>
                </>
              ) : (
                <p className="text-red-700 font-medium">{gstinResult.message}</p>
              )}
            </div>
          )}
          <div className="flex gap-3 mt-5">
            <button onClick={() => setStep(0)} className="px-5 py-2.5 border border-gray-200 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50">← Back</button>
            <button onClick={() => setStep(2)} className="airtel-btn flex-1">
              {gstinResult?.status === 'active' ? 'Verified — Continue →' : 'Skip (no GSTIN) →'}
            </button>
          </div>
        </div>
      )}

      {/* Step 2 — Udyam Lookup */}
      {step === 2 && (
        <div className="airtel-card">
          <h2 className="text-lg font-bold text-gray-800 mb-4">Verify Udyam Registration</h2>
          <div className="flex gap-3 mb-4">
            <input
              value={udyam}
              onChange={e => setUdyam(e.target.value.toUpperCase())}
              placeholder="UDYAM-XX-00-XXXXXXX"
              className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm font-mono uppercase tracking-widest"
            />
            <button onClick={lookupUdyam} className="airtel-btn flex items-center gap-2">
              <Search size={15}/> Verify
            </button>
          </div>
          {udyamResult && (
            <div className={`rounded-xl p-4 text-sm ${udyamResult.status === 'found' ? 'bg-green-50 border border-green-200' : 'bg-amber-50 border border-amber-200'}`}>
              {udyamResult.status === 'found' ? (
                <>
                  <p className="font-semibold text-green-800 flex items-center gap-2"><CheckCircle size={15}/> Udyam Found</p>
                  <p className="text-green-700 mt-1"><strong>{udyamResult.enterprise_name}</strong> — {udyamResult.enterprise_type}</p>
                  <p className="text-green-600 text-xs mt-1">{udyamResult.city}, {udyamResult.state}</p>
                </>
              ) : (
                <p className="text-amber-700">{udyamResult.message}</p>
              )}
            </div>
          )}
          <div className="flex gap-3 mt-5">
            <button onClick={() => setStep(1)} className="px-5 py-2.5 border border-gray-200 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50">← Back</button>
            <button onClick={() => setStep(3)} className="airtel-btn flex-1">Continue →</button>
          </div>
        </div>
      )}

      {/* Step 3 — Document Upload */}
      {step === 3 && (
        <div className="airtel-card">
          <h2 className="text-lg font-bold text-gray-800 mb-1">Upload KYC Documents</h2>
          <p className="text-xs text-gray-400 mb-4">All processing is done locally. No images are sent to external services.</p>

          <div className="mb-4">
            <label className="block text-xs text-gray-500 mb-1">Authorised Signatory Full Name</label>
            <input
              value={signatoryName}
              onChange={e => setSignatoryName(e.target.value)}
              placeholder="As on the ID document"
              className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm"
            />
          </div>

          <div className="space-y-4">
            {DOC_TYPES.map(({ key, label }) => {
              const result = docResults[key]
              const busy = uploading[key]
              return (
                <div key={key} className="border border-gray-100 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-gray-700">{label}</p>
                    {result && (
                      result.status === 'ok'
                        ? <CheckCircle size={16} className="text-green-500"/>
                        : <AlertTriangle size={16} className="text-amber-500"/>
                    )}
                  </div>
                  <label className={`flex items-center gap-2 cursor-pointer px-4 py-2 rounded-lg text-sm font-medium border transition-colors w-fit ${busy ? 'opacity-50' : 'hover:bg-gray-50 border-gray-200'}`}>
                    <Upload size={14}/>
                    {busy ? 'Processing…' : result ? 'Re-upload' : 'Choose File'}
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      disabled={busy}
                      onChange={e => e.target.files[0] && uploadDoc(key, e.target.files[0])}
                    />
                  </label>
                  {result?.flags?.length > 0 && (
                    <div className="mt-3 space-y-1">
                      {result.flags.map((flag, i) => (
                        <p key={i} className="text-xs text-amber-700 bg-amber-50 px-3 py-1.5 rounded-lg">{flag}</p>
                      ))}
                    </div>
                  )}
                  {result?.status === 'ok' && (
                    <p className="text-xs text-green-600 mt-2">✓ Document verified successfully</p>
                  )}
                  {result?.extracted_fields?.masked_aadhaar && (
                    <p className="text-xs text-gray-400 mt-1">ID: {result.extracted_fields.masked_aadhaar}</p>
                  )}
                </div>
              )
            })}
          </div>

          <div className="flex gap-3 mt-5">
            <button onClick={() => setStep(2)} className="px-5 py-2.5 border border-gray-200 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50">← Back</button>
            <button
              onClick={() => setStep(4)}
              disabled={!allDocsUploaded}
              className="airtel-btn flex-1"
            >
              {anyFlagged ? 'Submit for Manual Review →' : 'Complete KYC →'}
            </button>
          </div>
        </div>
      )}

      {/* Step 4 — Done */}
      {step === 4 && (
        <div className="airtel-card text-center py-10">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle size={40} className="text-green-500"/>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">KYC Complete! 🎉</h2>
          <p className="text-gray-500 mb-6">
            {anyFlagged
              ? 'Your documents have been submitted for manual review. Our team will contact you within 4 business hours.'
              : 'All documents verified. Your order is being processed!'}
          </p>
          <a href="/tracker" className="airtel-btn inline-block">Track My Order →</a>
        </div>
      )}
    </div>
  )
}

