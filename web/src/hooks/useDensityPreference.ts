import * as React from 'react';

export type Density = 'comfortable' | 'compact';
const KEY = 'hx_density';

export function useDensityPreference(initial: Density = 'comfortable') {
  const [density, setDensity] = React.useState<Density>(initial);

  React.useEffect(() => {
    const saved = typeof window !== 'undefined' ? (localStorage.getItem(KEY) as Density | null) : null;
    if (saved === 'compact' || saved === 'comfortable') setDensity(saved);
  }, []);

  React.useEffect(() => {
    if (typeof window !== 'undefined') localStorage.setItem(KEY, density);
  }, [density]);

  return { density, setDensity };
}