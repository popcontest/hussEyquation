'use client'

import * as React from 'react';
import { RankingsFilters } from '@/types/filters';
import { NumericFilter } from './NumericFilter';
import { DensityToggle } from './DensityToggle';
import { useDensityPreference } from '@/hooks/useDensityPreference';
import MethodologyModal from './MethodologyModal';

type Props = { 
  value: RankingsFilters; 
  onChange: (next: RankingsFilters) => void; 
  selectedSeason?: string;
  onSeasonChange?: (season: string) => void;
  searchTerm: string;
  onSearchChange: (term: string) => void;
  columns: Record<string, boolean>;
  onColumnsChange: (columns: Record<string, boolean>) => void;
  filteredCount: number;
  totalCount: number;
};

function ColumnPicker({ value, onChange }: { value: Record<string, boolean>; onChange: (next: Record<string, boolean>) => void }) {
  const [isOpen, setIsOpen] = React.useState(false);
  
  // This is a simplified version - you can expand with full column picker logic
  return (
    <div className="relative">
      <button
        type="button"
        className="hx-btn"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Column settings"
      >
        Columns
      </button>
      {/* Column picker dropdown would go here */}
    </div>
  );
}

export function FilterBar({ 
  value, 
  onChange, 
  selectedSeason = '2025',
  onSeasonChange,
  searchTerm,
  onSearchChange,
  columns,
  onColumnsChange,
  filteredCount,
  totalCount
}: Props) {
  const { density, setDensity } = useDensityPreference('comfortable');
  
  const set = <K extends keyof RankingsFilters>(k: K, v: RankingsFilters[K]) =>
    onChange({ ...value, [k]: v });

  const hasActiveFilters = React.useMemo(() => {
    return value.gp || value.min || (value.qualifiedOnly === false);
  }, [value]);

  const resetFilters = () => {
    onChange({ qualifiedOnly: true });
  };

  return (
    <div className="hx-controls" role="region" aria-label="Rankings controls">
      <div className="hx-controls__row">
        {/* Season selector */}
        <div className="hx-group">
          <label className="hx-label" htmlFor="season">Season</label>
          <select 
            id="season" 
            className="hx-input" 
            value={selectedSeason}
            onChange={(e) => onSeasonChange?.(e.target.value)}
            aria-label="Season"
          >
            <option value="2025">2024–25</option>
            <option value="2024">2023–24</option>
            <option value="2023">2022–23</option>
          </select>
        </div>

        {/* Filters */}
        <NumericFilter
          label="Games (GP)"
          value={value.gp}
          onChange={(v) => set('gp', v)}
          ariaLabel="Games filter"
        />
        
        <NumericFilter
          label="Minutes (MIN)"  
          value={value.min}
          onChange={(v) => set('min', v)}
          ariaLabel="Minutes filter"
        />

        {/* Qualified checkbox */}
        <label className="hx-check">
          <input
            type="checkbox"
            id="qualified"
            checked={value.qualifiedOnly ?? true}
            onChange={(e) => set('qualifiedOnly', e.target.checked)}
            aria-label="Qualified only"
          />
          <span>Qualified only</span>
        </label>

        {/* Search */}
        <div className="hx-spacer"></div>
        <div className="hx-search">
          <input
            className="hx-input hx-input--search"
            type="search"
            placeholder="Search players, teams, positions"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            aria-label="Search"
          />
        </div>

        {/* Actions */}
        <div className="hx-actions">
          <DensityToggle value={density} onChange={setDensity} />
          <ColumnPicker value={columns} onChange={onColumnsChange} />
          <button className="hx-btn" type="button">
            Download CSV
          </button>
          <MethodologyModal />
          {hasActiveFilters && (
            <button
              className="hx-btn hx-btn--ghost"
              type="button"
              onClick={resetFilters}
              aria-label="Reset filters"
            >
              Reset
            </button>
          )}
        </div>
      </div>
      
      {/* Results counter */}
      <div className="px-4 py-2 text-sm text-gray-600 bg-gray-50 border-t border-gray-200" aria-live="polite">
        Showing {filteredCount.toLocaleString()} of {totalCount.toLocaleString()} players
      </div>
    </div>
  );
}