'use client'

import { useState } from 'react'
import RankingsTableClient from './RankingsTableClient'
import SeasonSelector from './SeasonSelector'

export default function RankingsSection() {
  const [selectedSeason, setSelectedSeason] = useState('2025')

  const getSeasonName = (season: string) => {
    switch (season) {
      case '2025': return '2024-25'
      case '2024': return '2023-24'
      case '2023': return '2022-23'
      case '2022': return '2021-22'
      default: return '2024-25'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-semibold text-gray-900">
              {getSeasonName(selectedSeason)} Season Rankings
            </h2>
            <SeasonSelector 
              currentSeason={selectedSeason}
              onSeasonChange={setSelectedSeason}
            />
          </div>
        </div>
        <p className="mt-2 text-sm text-gray-600">
          Ranked by hussEyquation score (lower = better). Default view includes all players; adjust minutes/filters to refine.
        </p>
      </div>
      
      <RankingsTableClient selectedSeason={selectedSeason} />
    </div>
  )
}