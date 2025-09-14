import { Suspense } from 'react'
import RankingsSection from '@/components/RankingsSection'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'hussEyquation | NBA Player Rankings',
  description: 'Comprehensive NBA player rankings using the hussEyquation composite metric - averaging PER, Win Shares, WS/48, BPM, and VORP rankings.',
}

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-7">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl tracking-tight">
              huss<span className="text-blue-600">Eyquation</span> — NBA Player Impact Rankings
            </h1>
            <p className="mt-2 max-w-2xl mx-auto text-lg text-gray-600 leading-relaxed">
              One composite score for player impact. Lower is better.<br />
              Calculated from PER, Win Shares, WS/48, BPM, and VORP.
            </p>
            <p className="mt-3 text-sm text-gray-500">
              Updated daily • Season: <strong>2024–25</strong> • Source: Basketball-Reference
            </p>
          </div>
        </div>
      </header>

      {/* Rankings Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Suspense fallback={<div className="p-8 text-center">Loading rankings...</div>}>
          <RankingsSection />
        </Suspense>
      </section>

      {/* Methodology Preview */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-blue-50 rounded-lg p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            How hussEyquation Works
          </h3>
          <div className="grid md:grid-cols-2 gap-6 text-gray-700">
            <div>
              <h4 className="font-medium mb-2">The Formula</h4>
              <p className="text-sm">
                We rank each player in five advanced metrics, then average those ranks. 
                A player ranked 1st, 3rd, 5th, 2nd, and 4th would score (1+3+5+2+4)/5 = 3.0.
              </p>
            </div>
            <div>
              <h4 className="font-medium mb-2">Why It Works</h4>
              <p className="text-sm">
                This consensus approach rewards players who are consistently elite across 
                multiple areas rather than specialists in just one metric.
              </p>
            </div>
          </div>
          <div className="mt-4">
            <a 
              href="/about" 
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              Learn more about our methodology →
            </a>
          </div>
        </div>
      </section>
    </main>
  )
}
