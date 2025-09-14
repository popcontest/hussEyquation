'use client'

import { useState } from 'react'

export default function MethodologyModal() {
  const [isOpen, setIsOpen] = useState(false)

  const openModal = () => setIsOpen(true)
  const closeModal = () => setIsOpen(false)

  return (
    <>
      {/* Trigger Button */}
      <button
        onClick={openModal}
        className="px-3 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:ring-2 focus:ring-blue-600"
      >
        Methodology
      </button>

      {/* Modal */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-35 flex items-center justify-center z-50"
          onClick={closeModal}
        >
          <div 
            className="w-full max-w-3xl max-h-[88vh] overflow-auto bg-white rounded-xl p-6 m-4 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900">hussEyquation Methodology</h3>
              <button
                onClick={closeModal}
                className="text-gray-400 hover:text-gray-600 text-2xl font-light"
                aria-label="Close"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4 text-gray-700">
              <p>
                <strong>Score (lower is better):</strong> the average of a player's ranks across{' '}
                <em>PER, WS, WS/48, BPM, VORP</em> for the selected season.
              </p>
              
              <pre className="bg-gray-50 p-3 rounded text-sm font-mono">
                Score = mean(rank_PER, rank_WS, rank_WS48, rank_BPM, rank_VORP)
              </pre>

              <div>
                <h4 className="font-medium text-gray-900 mt-6 mb-2">Inputs & definitions</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>PER</strong> — pace-adjusted box-score efficiency (league avg ≈ 15).</li>
                  <li><strong>WS</strong> — wins contributed estimate.</li>
                  <li><strong>WS/48</strong> — WS per 48 minutes (league avg ≈ 0.100).</li>
                  <li><strong>BPM</strong> — per-100 possessions plus/minus (league avg ≈ 0).</li>
                  <li><strong>VORP</strong> — cumulative value vs replacement (BPM-based).</li>
                </ul>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mt-6 mb-2">Eligibility & hygiene</h4>
                <ul className="space-y-1 text-sm">
                  <li>Apply MIN/GP filters for meaningful comparisons; tiny samples can distort WS/48 and BPM.</li>
                  <li>Multi-team seasons are aggregated to player-season level.</li>
                  <li>Players missing any input metric are excluded from the composite.</li>
                  <li>Ties share a rank (competition ranking).</li>
                </ul>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mt-6 mb-2">Updates & source</h4>
                <p className="text-sm">Updated daily in season • Data: Basketball-Reference.</p>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mt-6 mb-2">Limitations</h4>
                <p className="text-sm">Box-score only; does not include on/off, role, opponent, or scheme adjustments.</p>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mt-6 mb-2">Versioning</h4>
                <p className="text-sm">v1.0 — simple average of ranks across five metrics.</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}