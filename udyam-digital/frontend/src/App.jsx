import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Advisor from './pages/Advisor'
import Quote from './pages/Quote'
import KYC from './pages/KYC'
import Tracker from './pages/Tracker'
import PartnerPortal from './pages/PartnerPortal'
import { MessageSquare, FileText, ShieldCheck, Activity, Users } from 'lucide-react'

const NAV = [
  { path: '/',          label: 'Advisor',   Icon: MessageSquare },
  { path: '/quote',     label: 'Quote',     Icon: FileText      },
  { path: '/kyc',       label: 'KYC',       Icon: ShieldCheck   },
  { path: '/tracker',   label: 'Tracker',   Icon: Activity      },
  { path: '/partners',  label: 'Partners',  Icon: Users         },
]

export default function App() {
  const { pathname } = useLocation()

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-red-600 text-white shadow-lg">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight">Digi Saathi</h1>
            <p className="text-xs text-red-100">Accel Business — SMB Digital Onboarding</p>
          </div>
          <span className="text-xs bg-red-700 px-3 py-1 rounded-full">YTL Hackathon 2026</span>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 flex gap-1 overflow-x-auto">
          {NAV.map(({ path, label, Icon }) => (
            <Link
              key={path}
              to={path}
              className={`flex items-center gap-1.5 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                pathname === path
                  ? 'border-red-600 text-red-600'
                  : 'border-transparent text-gray-500 hover:text-gray-800'
              }`}
            >
              <Icon size={15} />
              {label}
            </Link>
          ))}
        </div>
      </nav>

      {/* Main content */}
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-6">
        <Routes>
          <Route path="/"         element={<Advisor />}       />
          <Route path="/quote"    element={<Quote />}         />
          <Route path="/kyc"      element={<KYC />}           />
          <Route path="/tracker"  element={<Tracker />}       />
          <Route path="/partners" element={<PartnerPortal />} />
        </Routes>
      </main>

      <footer className="text-center text-xs text-gray-400 py-4 border-t">
        © 2026 Accel Business · All data is synthetic · YTL Hackathon
      </footer>
    </div>
  )
}

