'use client'

// import { useState } from 'react'

interface SeasonSelectorProps {
  onSeasonChange: (season: string) => void
  currentSeason: string
}

export default function SeasonSelector({ onSeasonChange, currentSeason }: SeasonSelectorProps) {
  const seasons = [
    { value: '2025', label: '2024-25' },
    { value: '2024', label: '2023-24' },
    { value: '2023', label: '2022-23' },
    { value: '2022', label: '2021-22' }
  ]

  return (
    <div className="relative">
      <select 
        className="appearance-none bg-white border border-gray-300 rounded-md px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-8"
        value={currentSeason}
        onChange={(e) => onSeasonChange(e.target.value)}
      >
        {seasons.map((season) => (
          <option key={season.value} value={season.value}>
            {season.label}
          </option>
        ))}
      </select>
      <svg 
        className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </div>
  )
}