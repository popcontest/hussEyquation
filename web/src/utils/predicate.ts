import { Comparator, NumericCondition } from '@/types/filters';

export function evaluateNumeric(value: number | undefined, cond?: NumericCondition): boolean {
  if (cond == null) return true;
  if (value == null || Number.isNaN(value)) return false;

  const { op, value: v, value2 } = cond;
  switch (op) {
    case 'gt':  return v != null && value >  v;
    case 'gte': return v != null && value >= v;
    case 'eq':  return v != null && value === v;
    case 'lte': return v != null && value <= v;
    case 'lt':  return v != null && value <  v;
    case 'between':
      if (v == null || value2 == null) return true; // treat missing as no-op
      const lo = Math.min(v, value2), hi = Math.max(v, value2);
      return value >= lo && value <= hi;
    default: return true;
  }
}