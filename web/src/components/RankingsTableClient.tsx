'use client'

import { useState, useEffect, useMemo } from 'react'
import { ChevronUpIcon, ChevronDownIcon } from '@heroicons/react/20/solid'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { Hero } from './Hero'
import { FilterBar } from './FilterBar'
import { RankingsFilters, defaultFilters, NumericCondition } from '@/types/filters'
import { evaluateNumeric } from '@/utils/predicate'
import { useDensityPreference } from '@/hooks/useDensityPreference'

type ColumnKey =
  | 'rank' | 'player' | 'team' | 'pos'
  | 'score' | 'per' | 'ws' | 'ws48' | 'bpm' | 'vorp'
  | 'gp' | 'min' | 'deltaLy' | 'trend'
  | 'qualified'
  | 'per_rank' | 'ws_rank' | 'ws48_rank' | 'bpm_rank' | 'vorp_rank'

type ColumnState = Record<ColumnKey, boolean>

const defaultColumns: ColumnState = {
  rank: true, player: true, team: true, pos: true,
  score: true, per: true, ws: false, ws48: true, bpm: true, vorp: true,
  gp: true, min: true, deltaLy: true, trend: false,
  qualified: false,
  per_rank: false, ws_rank: false, ws48_rank: false, bpm_rank: false, vorp_rank: false,
}

const columnLabels: Record<ColumnKey, string> = {
  rank: 'Rank', player: 'Player', team: 'Team', pos: 'Pos',
  score: 'Score', per: 'PER', ws: 'WS', ws48: 'WS/48', bpm: 'BPM', vorp: 'VORP',
  gp: 'GP', min: 'MIN', deltaLy: 'Δ vs LY', trend: 'Trend',
  qualified: 'Qualified',
  per_rank: 'PER Rank', ws_rank: 'WS Rank', ws48_rank: 'WS/48 Rank', bpm_rank: 'BPM Rank', vorp_rank: 'VORP Rank',
}

const columnTooltips: Record<ColumnKey, string> = {
  rank: 'Overall order by Score (lower is better)',
  player: 'Player name',
  team: 'Current season team (aggregated for multi-team seasons)',
  pos: 'Primary position',
  score: 'hussEyquation Score = average rank across PER, WS, WS/48, BPM, VORP (lower is better)',
  per: 'Player Efficiency Rating (pace-adjusted; league avg ≈ 15)',
  ws: 'Win Shares (estimate of wins contributed)',
  ws48: 'Win Shares per 48 minutes (league avg ≈ 0.100)',
  bpm: 'Box Plus/Minus per 100 possessions (league avg ≈ 0)',
  vorp: 'Value Over Replacement (BPM-based cumulative value)',
  gp: 'Games played',
  min: 'Total minutes',
  deltaLy: 'Change in rank vs last season (↓ rank number = improvement)',
  trend: 'Short-term movement; tooltip shows 1d/7d/14d deltas',
  qualified: 'Meets minutes/games threshold used by the model',
  per_rank: 'Rank in Player Efficiency Rating',
  ws_rank: 'Rank in Win Shares',
  ws48_rank: 'Rank in Win Shares per 48 minutes',
  bpm_rank: 'Rank in Box Plus/Minus',
  vorp_rank: 'Rank in Value Over Replacement',
}

// Column order for display
const columnOrder: ColumnKey[] = [
  'rank', 'player', 'team', 'pos', 'score', 'per', 'ws', 'ws48', 'bpm', 'vorp', 
  'gp', 'min', 'deltaLy', 'trend', 'qualified', 'per_rank', 'ws_rank', 'ws48_rank', 'bpm_rank', 'vorp_rank'
]

interface Player {
  rank: number
  player_id: number
  player_name: string
  team: string
  position: string
  huss_score: number
  per: number
  per_rank: number
  ws: number
  ws_rank: number
  ws48: number
  ws48_rank: number
  bpm: number
  bpm_rank: number
  vorp: number
  vorp_rank: number
  games: number
  minutes: number
  qualified: boolean
  trend_1d: number
  trend_7d: number
  trend_14d: number
  // Year-over-year comparison fields
  rank_change: number
  previous_rank: number
  trend_direction: 'UP' | 'DOWN' | 'SAME' | 'NEW'
}

interface RankingsResponse {
  players: Player[]
  total_count: number
  season: number
  last_updated: string
}

function TrendIndicator({ player }: { player: Player }) {
  const { rank_change, trend_direction } = player
  
  if (trend_direction === 'NEW') {
    return (
      <div className="flex items-center justify-center">
        <span className="text-xs font-medium px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full">NEW</span>
      </div>
    )
  } else if (rank_change > 0) {
    // Positive rank_change means they improved (moved up in rankings, lower number)
    return (
      <div className="flex items-center justify-center text-green-600">
        <ChevronUpIcon className="h-3 w-3" />
        <span className="text-xs font-semibold ml-1">+{rank_change}</span>
      </div>
    )
  } else if (rank_change < 0) {
    // Negative rank_change means they declined (moved down in rankings, higher number)
    return (
      <div className="flex items-center justify-center text-red-600">
        <ChevronDownIcon className="h-3 w-3" />
        <span className="text-xs font-semibold ml-1">{rank_change}</span>
      </div>
    )
  }
  return (
    <div className="flex items-center justify-center text-gray-400">
      <span className="text-xs">—</span>
    </div>
  )
}

function TrendCell({ trend7d, trend1d, trend14d }: { trend7d?: number; trend1d?: number; trend14d?: number }) {
  if (trend7d == null) return <span className="text-gray-400">—</span>
  
  const arrow = trend7d < 0 ? '▲' : trend7d > 0 ? '▼' : '—'
  const color = trend7d < 0 ? 'text-green-600' : trend7d > 0 ? 'text-red-600' : 'text-gray-400'
  const tip = `Score change: 1d ${trend1d?.toFixed(1) || 'N/A'}, 7d ${trend7d?.toFixed(1) || 'N/A'}, 14d ${trend14d?.toFixed(1) || 'N/A'}`
  
  return (
    <span title={tip} className={`text-xs font-medium ${color}`}>
      {arrow} {Math.abs(trend7d).toFixed(1)}
    </span>
  )
}

// Commented out unused component for now
/* function ColumnPicker({ value, onChange }: {
  value: ColumnState
  onChange: (next: ColumnState) => void
}) {
  const [isOpen, setIsOpen] = useState(false)
  
  const toggle = (key: ColumnKey) => {
    onChange({ ...value, [key]: !value[key] })
  }
  
  const coreColumns = ['rank', 'player', 'team', 'pos', 'score'] as ColumnKey[]
  const metricColumns = ['per', 'ws', 'ws48', 'bpm', 'vorp'] as ColumnKey[]
  const contextColumns = ['gp', 'min', 'deltaLy', 'trend', 'qualified'] as ColumnKey[]
  const rankColumns = ['per_rank', 'ws_rank', 'ws48_rank', 'bpm_rank', 'vorp_rank'] as ColumnKey[]
  
  return (
    <div className="relative inline-block">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-3 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:ring-2 focus:ring-blue-600"
      >
        Columns
      </button>
      
      {isOpen && (
        <div className="absolute top-full right-0 mt-1 bg-white border border-gray-200 rounded-md shadow-lg z-50 min-w-64 p-3">
          <div className="space-y-3">
            <div>
              <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">Core</h4>
              <div className="space-y-1">
                {coreColumns.map(key => (
                  <label key={key} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={value[key]}
                      onChange={() => toggle(key)}
                      disabled={key === 'rank' || key === 'player'}
                      className="h-3 w-3 text-blue-600 rounded"
                    />
                    <span className={key === 'rank' || key === 'player' ? 'text-gray-400' : ''}>
                      {columnLabels[key]}
                    </span>
                  </label>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">Metrics</h4>
              <div className="space-y-1">
                {metricColumns.map(key => (
                  <label key={key} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={value[key]}
                      onChange={() => toggle(key)}
                      className="h-3 w-3 text-blue-600 rounded"
                    />
                    {columnLabels[key]}
                  </label>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">Context</h4>
              <div className="space-y-1">
                {contextColumns.map(key => (
                  <label key={key} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={value[key]}
                      onChange={() => toggle(key)}
                      className="h-3 w-3 text-blue-600 rounded"
                    />
                    {columnLabels[key]}
                  </label>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">Ranks</h4>
              <div className="space-y-1">
                {rankColumns.map(key => (
                  <label key={key} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={value[key]}
                      onChange={() => toggle(key)}
                      className="h-3 w-3 text-blue-600 rounded"
                    />
                    {columnLabels[key]}
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
} */

interface RankingsTableClientProps {
  selectedSeason?: string
}

export default function RankingsTableClient({ selectedSeason = '2025' }: RankingsTableClientProps) {
  const [data, setData] = useState<RankingsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [columns, setColumns] = useState<ColumnState>(defaultColumns)
  const { density } = useDensityPreference('comfortable')
  
  // URL sync utilities for filters
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  
  const toQueryString = (filters: RankingsFilters) => {
    const sp = new URLSearchParams()
    const enc = (key: string, c?: NumericCondition) => {
      if (!c) return
      sp.set(`${key}_op`, c.op)
      if (c.value != null)  sp.set(`${key}_val`, String(c.value))
      if (c.value2 != null) sp.set(`${key}_val2`, String(c.value2))
    }
    Object.entries(filters).forEach(([k, v]) => {
      if (k === 'qualifiedOnly') return
      enc(k, v as NumericCondition | undefined)
    })
    if (filters.qualifiedOnly === false) sp.set('qualified', 'false')
    return sp.toString()
  }
  
  const fromQueryString = (sp: URLSearchParams): RankingsFilters => {
    const dec = (key: string): NumericCondition | undefined => {
      const op = sp.get(`${key}_op`) as ComparisonOperator | null
      if (!op) return undefined
      const val  = sp.get(`${key}_val`)
      const val2 = sp.get(`${key}_val2`)
      return {
        op,
        value:  val  != null ? Number(val)  : undefined,
        value2: val2 != null ? Number(val2) : undefined,
      }
    }
    const q = sp.get('qualified')
    return {
      gp:   dec('gp'),
      min:  dec('min'),
      score: dec('score'),
      ws48: dec('ws48'),
      bpm:  dec('bpm'),
      per:  dec('per'),
      ws:   dec('ws'),
      vorp: dec('vorp'),
      qualifiedOnly: q === 'false' ? false : true,
    }
  }
  
  // Initialize filters from URL params
  const [filters, setFilters] = useState<RankingsFilters>(() =>
    searchParams ? { ...defaultFilters, ...fromQueryString(searchParams) } : defaultFilters
  )
  
  // Field mapping for filtering - memoized to prevent recreation on every render
  const fieldMap = useMemo(() => ({
    gp:    (p: Player) => p.games,
    min:   (p: Player) => p.minutes,
    score: (p: Player) => p.huss_score,
    ws48:  (p: Player) => p.ws48,
    bpm:   (p: Player) => p.bpm,
    per:   (p: Player) => p.per,
    ws:    (p: Player) => p.ws,
    vorp:  (p: Player) => p.vorp,
  }), [])
  
  // Keep URL in sync with filters
  useEffect(() => {
    const qs = toQueryString(filters)
    const newUrl = qs ? `${pathname}?season=${selectedSeason}&${qs}` : `${pathname}?season=${selectedSeason}`
    router.replace(newUrl, { scroll: false })
  }, [filters, pathname, router, selectedSeason])
  
  // Load column preferences from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('husseyquation-columns')
    if (saved) {
      try {
        setColumns(JSON.parse(saved))
      } catch (e) {
        console.warn('Failed to load column preferences:', e)
      }
    }
  }, [])
  
  // Save column preferences to localStorage
  const updateColumns = (newColumns: ColumnState) => {
    setColumns(newColumns)
    localStorage.setItem('husseyquation-columns', JSON.stringify(newColumns))
  }
  
  // Render cell content based on column key
  const renderCellContent = (player: Player, key: ColumnKey) => {
    switch (key) {
      case 'rank':
        return player.rank
      case 'player':
        return (
          <div>
            <div className="text-sm font-medium text-gray-900">{player.player_name}</div>
            <div className="text-xs text-gray-500">{player.position}</div>
          </div>
        )
      case 'team':
        return player.team
      case 'pos':
        return player.position
      case 'score':
        return <span className="font-medium text-blue-700 mono">{player.huss_score?.toFixed(1) || 'N/A'}</span>
      case 'per':
        return <span className="mono">{player.per?.toFixed(1) || 'N/A'}</span>
      case 'ws':
        return <span className="mono">{player.ws?.toFixed(1) || 'N/A'}</span>
      case 'ws48':
        return <span className="mono">{player.ws48?.toFixed(3) || 'N/A'}</span>
      case 'bpm':
        return <span className="mono">{player.bpm?.toFixed(1) || 'N/A'}</span>
      case 'vorp':
        return <span className="mono">{player.vorp?.toFixed(1) || 'N/A'}</span>
      case 'gp':
        return <span className="mono">{player.games || 'N/A'}</span>
      case 'min':
        return <span className="mono">{player.minutes?.toLocaleString() || 'N/A'}</span>
      case 'deltaLy':
        return <TrendIndicator player={player} />
      case 'trend':
        return <TrendCell trend7d={player.trend_7d} trend1d={player.trend_1d} trend14d={player.trend_14d} />
      case 'qualified':
        return player.qualified ? (
          <span className="text-xs font-medium px-2 py-0.5 bg-green-100 text-green-800 rounded-full">Yes</span>
        ) : (
          <span className="text-xs font-medium px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">No</span>
        )
      case 'per_rank':
        return <span className="mono">{player.per_rank || 'N/A'}</span>
      case 'ws_rank':
        return <span className="mono">{player.ws_rank || 'N/A'}</span>
      case 'ws48_rank':
        return <span className="mono">{player.ws48_rank || 'N/A'}</span>
      case 'bpm_rank':
        return <span className="mono">{player.bpm_rank || 'N/A'}</span>
      case 'vorp_rank':
        return <span className="mono">{player.vorp_rank || 'N/A'}</span>
      default:
        return 'N/A'
    }
  }

  useEffect(() => {
    async function fetchRankings() {
      let response: Response | undefined
      try {
        setLoading(true)
        console.log('Fetching rankings from API...')
        const url = `/api/rankings?season=${selectedSeason}&qualified=false&limit=570`
        console.log('URL:', url)
        
        response = await fetch(url, {
          cache: 'no-cache', // Disable cache to avoid stale data
          headers: {
            'Accept': 'application/json',
          }
        })
        
        console.log('Response status:', response.status)
        console.log('Response ok:', response.ok)
        
        if (!response.ok) {
          const errorText = await response.text()
          console.error('Error response body:', errorText)
          throw new Error(`HTTP error! status: ${response.status} - ${errorText}`)
        }
        
        const result = await response.json()
        console.log('API Result:', result.players?.length, 'players loaded')
        setData(result)
        setError(null)
      } catch (err) {
        console.error('Error fetching rankings:', err)
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch rankings'
        console.error('Full error details:', errorMessage)
        console.log('Response status:', response?.status)
        console.log('Response ok:', response?.ok)
        setError(`API Error: ${errorMessage} (Check browser console for details)`)
      } finally {
        setLoading(false)
      }
    }

    fetchRankings()
  }, [selectedSeason])

  // Add sticky controls behavior
  useEffect(() => {
    const handleScroll = () => {
      const controls = document.querySelector('.hx-controls');
      if (controls) {
        const stuck = window.scrollY > 12;
        controls.classList.toggle('is-stuck', stuck);
      }
    };

    handleScroll(); // Set initial state
    window.addEventListener('scroll', handleScroll, { passive: true });
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [])

  // Filter players based on search term and numeric filters - must be before early returns
  const filteredPlayers = useMemo(() => {
    if (!data) return []
    
    return data.players.filter(player => {
      // Text search filter
      const matchesSearch = searchTerm === '' || (
        player.player_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        player.team.toLowerCase().includes(searchTerm.toLowerCase()) ||
        player.position.toLowerCase().includes(searchTerm.toLowerCase())
      )
      
      if (!matchesSearch) return false
      
      // Qualified filter
      if ((filters.qualifiedOnly ?? true) && !player.qualified) return false
      
      // Numeric filters
      for (const [k, getValue] of Object.entries(fieldMap)) {
        const cond = (filters as Record<string, NumericCondition | undefined>)[k] as NumericCondition | undefined
        if (cond && !evaluateNumeric(getValue(player), cond)) return false
      }
      
      return true
    })
  }, [data, searchTerm, filters, fieldMap])

  if (loading) {
    return <div className="p-8 text-center">Loading rankings...</div>
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <p className="text-red-600">Error: {error}</p>
        <p className="text-gray-500 mt-2">Make sure the API server is running on localhost:8000</p>
      </div>
    )
  }

  if (!data || data.players.length === 0) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-500">No rankings data available</p>
      </div>
    )
  }

  return (
    <>
      {/* Hero Section */}
      <Hero season="2024–25" />
      
      {/* Controls Bar */}
      <FilterBar 
        value={filters} 
        onChange={setFilters}
        selectedSeason={selectedSeason}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        columns={columns}
        onColumnsChange={updateColumns}
        filteredCount={filteredPlayers.length}
        totalCount={data.players.length}
      />

      {/* Score Note */}
      <div className="hx-note">
        Score = average rank across PER, WS, WS/48, BPM, VORP • lower is better
      </div>
      
      <div className="overflow-x-auto">

      {/* Desktop View */}
      <div className={`hidden md:block relative ${density === 'compact' ? 'hx-table--compact' : 'hx-table--comfortable'}`}>
        <table className="min-w-full table-freeze-columns">
          <thead className="bg-gray-50">
            <tr>
              {columnOrder.filter(key => columns[key]).map((key) => {
                // const isSticky = key === 'rank' || key === 'player'
                const isLeftAlign = key === 'rank' || key === 'player' || key === 'team' || key === 'pos'
                const hasBorder = key === 'score' || key === 'gp'
                const stickyClasses = key === 'rank' 
                  ? 'sticky left-0 z-10 bg-gray-50 border-r border-gray-200'
                  : key === 'player'
                  ? 'sticky left-16 z-10 bg-gray-50 border-r border-gray-200'
                  : ''
                const borderClasses = hasBorder ? 'border-l border-gray-200' : ''
                
                return (
                  <th
                    key={key}
                    scope="col"
                    className={`px-4 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider ${
                      isLeftAlign ? 'text-left' : 'text-center'
                    } ${stickyClasses} ${borderClasses}`}
                    title={columnTooltips[key]}
                  >
                    {columnLabels[key]}
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {filteredPlayers.map((player) => (
              <tr key={player.player_id} className="hover:bg-gray-25 border-b border-gray-100">
                {columnOrder.filter(key => columns[key]).map((key) => {
                  // const isSticky = key === 'rank' || key === 'player'
                  const isLeftAlign = key === 'rank' || key === 'player' || key === 'team' || key === 'pos'
                  const hasBorder = key === 'score' || key === 'gp'
                  const stickyClasses = key === 'rank' 
                    ? 'sticky left-0 z-10 bg-white border-r border-gray-200'
                    : key === 'player'
                    ? 'sticky left-16 z-10 bg-white border-r border-gray-200'
                    : ''
                  const borderClasses = hasBorder ? 'border-l border-gray-200' : ''
                  const fontWeight = key === 'rank' ? 'font-semibold' : ''
                  
                  return (
                    <td
                      key={key}
                      className={`px-4 py-4 whitespace-nowrap text-sm text-gray-700 ${
                        isLeftAlign ? 'text-left' : 'text-center'
                      } ${stickyClasses} ${borderClasses} ${fontWeight}`}
                    >
                      {renderCellContent(player, key)}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile View */}
      <div className={`md:hidden ${density === 'compact' ? 'hx-table--compact' : 'hx-table--comfortable'}`}>
        <div className="space-y-4 p-4">
          {filteredPlayers.map((player) => (
            <div key={player.player_id} className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <div className="font-medium text-gray-900">#{player.rank} {player.player_name}</div>
                  <div className="text-sm text-gray-500">{player.team} • {player.position}</div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-blue-700">{player.huss_score?.toFixed(1) || 'N/A'}</div>
                  <div className="text-xs text-gray-500">Score</div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="text-center">
                  <div className="font-medium">{player.ws48?.toFixed(3) || 'N/A'}</div>
                  <div className="text-xs text-gray-500">WS/48</div>
                </div>
                <div className="text-center">
                  <div className="font-medium">{player.bpm?.toFixed(1) || 'N/A'}</div>
                  <div className="text-xs text-gray-500">BPM</div>
                </div>
              </div>
              
              <div className="flex justify-between items-center mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
                <span>{player.games || 'N/A'} GP • {player.minutes?.toLocaleString() || 'N/A'} MIN</span>
                <div className="flex items-center gap-2">
                  <TrendIndicator player={player} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <div className="flex justify-between items-center text-sm text-gray-600">
          <span>Showing {filteredPlayers.length} players</span>
          <span>Last updated: {new Date(data.last_updated).toLocaleDateString()}</span>
        </div>
      </div>
      </div>
    </>
  )
}