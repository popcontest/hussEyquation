'use client'

import * as React from 'react';

type Props = {
  season?: string;
};

export function Hero({ season = '2024–25' }: Props) {
  return (
    <header className="hx-hero">
      <h1 className="hx-title">
        <span className="hx-brand">huss</span>
        <span className="hx-accent">Equation</span> — NBA Player Impact Rankings
      </h1>
      <p className="hx-sub">
        One composite score for player impact. <strong>Lower is better.</strong><br />
        Calculated from PER, Win Shares, WS/48, BPM, and VORP.
      </p>
      <div className="hx-meta">
        <span className="hx-badge">Updated daily</span>
        <span className="hx-dot">•</span>
        <span className="hx-badge">Season: <strong>{season}</strong></span>
        <span className="hx-dot">•</span>
        <span className="hx-badge">Source: Basketball-Reference</span>
      </div>
    </header>
  );
}