'use client'

import * as React from 'react';
import { Density } from '@/hooks/useDensityPreference';

type Props = {
  value: Density;
  onChange: (next: Density) => void;
};

export function DensityToggle({ value, onChange }: Props) {
  // keyboard support for segmented control
  const ref = React.useRef<HTMLDivElement>(null);
  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      const next = value === 'comfortable' ? 'compact' : 'comfortable';
      onChange(next);
      e.preventDefault();
    }
    if (e.key === ' ' || e.key === 'Enter') {
      onChange(value === 'comfortable' ? 'compact' : 'comfortable');
      e.preventDefault();
    }
  }

  return (
    <div className="hx-density" role="group" aria-label="Density" onKeyDown={onKeyDown} ref={ref} tabIndex={0}>
      <button
        type="button"
        className={`hx-density__btn ${value === 'comfortable' ? 'is-active' : ''}`}
        aria-pressed={value === 'comfortable'}
        onClick={() => onChange('comfortable')}
        title="Comfortable row height"
        tabIndex={-1}
      >
        Comfortable
      </button>
      <button
        type="button"
        className={`hx-density__btn ${value === 'compact' ? 'is-active' : ''}`}
        aria-pressed={value === 'compact'}
        onClick={() => onChange('compact')}
        title="Compact row height"
        tabIndex={-1}
      >
        Compact
      </button>
    </div>
  );
}