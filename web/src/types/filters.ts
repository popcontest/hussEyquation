export type Comparator = 'gt' | 'gte' | 'eq' | 'lte' | 'lt' | 'between';

export type NumericCondition = {
  op: Comparator;
  value?: number;     // for gt/gte/eq/lte/lt
  value2?: number;    // only for between
};

export type RankingsFilters = {
  gp?: NumericCondition;
  min?: NumericCondition;
  score?: NumericCondition;   // huss_score
  ws48?: NumericCondition;
  bpm?: NumericCondition;
  per?: NumericCondition;
  ws?: NumericCondition;
  vorp?: NumericCondition;
  // add others as needed…
  qualifiedOnly?: boolean;    // default true
};

export const defaultFilters: RankingsFilters = {
  qualifiedOnly: true
};