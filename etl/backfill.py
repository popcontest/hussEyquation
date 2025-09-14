from __future__ import annotations
from run_daily import ACTIVE_SEASON
from pull import build_season_totals
from metrics import compute_per, compute_win_shares, compute_bmp_vorp
from pipeline import qualify, compute_ranks_and_huss

def backfill(start_season=2016, end_season=2025):
    for season in range(start_season, end_season+1):
        print(f"Backfilling season {season}...")
        totals = build_season_totals(season)
        per  = compute_per(totals)
        wsdf = compute_win_shares(totals)
        bmpdf= compute_bmp_vorp(totals)
        df = totals.join(per).join(wsdf).join(bmpdf)
        df["qualified"] = qualify(df, min_minutes=1000)
        ranked = compute_ranks_and_huss(df)
        # TODO: write one season-final snapshot to season_final_ranks
        print(f"Top 5 for {season}:")
        print(ranked.sort_values("huss_rank").head(5)[["player","huss_rank","huss_score"]])

if __name__ == "__main__":
    backfill()