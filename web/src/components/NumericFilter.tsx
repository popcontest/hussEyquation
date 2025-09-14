'use client'

import * as React from 'react';
import { Comparator, NumericCondition } from '@/types/filters';

const OPS: { label: string; value: Comparator }[] = [
  { label: '≥', value: 'gte' },
  { label: '>', value: 'gt' },
  { label: '=', value: 'eq' },
  { label: '≤', value: 'lte' },
  { label: '<', value: 'lt' },
  { label: 'Between', value: 'between' },
];

type Props = {
  label: string;
  placeholder?: string;
  step?: number;
  value?: NumericCondition;
  onChange: (next?: NumericCondition) => void;
  ariaLabel?: string;
};

export function NumericFilter({ label, placeholder, step = 1, value, onChange, ariaLabel }: Props) {
  const op = value?.op ?? 'gte';
  const v = value?.value ?? '';
  const v2 = value?.value2 ?? '';

  function set<K extends keyof NumericCondition>(k: K, val: NumericCondition[K]) {
    const base: NumericCondition = { op, value: v as string | number, value2: v2 as string | number };
    const next = { ...base, [k]: val };

    // if numbers are empty, clear condition
    const empty = next.op !== 'between'
      ? (next.value == null || (typeof next.value === 'number' && isNaN(next.value)))
      : (next.value == null || next.value2 == null || 
         (typeof next.value === 'number' && isNaN(next.value)) ||
         (typeof next.value2 === 'number' && isNaN(next.value2)));

    onChange(empty ? undefined : next);
  }

  return (
    <div className="hx-group">
      <label className="hx-label">{label}</label>
      <div className="hx-opinput" role="group" aria-label={ariaLabel || `${label} filter`}>
        <select
          className="hx-op"
          value={op}
          onChange={(e) => set('op', e.target.value as Comparator)}
          aria-label={`${label} operator`}
        >
          {OPS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>

        <input
          type="number"
          className="hx-input"
          step={step}
          placeholder={placeholder ?? '0'}
          value={v}
          onChange={(e) => set('value', e.target.value === '' ? undefined : Number(e.target.value))}
          aria-label={`${label} value`}
          inputMode="numeric"
        />

        {op === 'between' && (
          <>
            <span className="hx-dash">–</span>
            <input
              type="number"
              className="hx-input"
              step={step}
              placeholder="max"
              value={v2}
              onChange={(e) => set('value2', e.target.value === '' ? undefined : Number(e.target.value))}
              aria-label={`${label} max value`}
              inputMode="numeric"
            />
          </>
        )}
      </div>
    </div>
  );
}