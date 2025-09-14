from __future__ import annotations
import os
import pandas as pd
from datetime import date
from pull import build_season_totals
from metrics import compute_per, compute_win_shares, compute_bmp_vorp
from pipeline import qualify, compute_ranks_and_huss, with_trend

ACTIVE_SEASON = int(os.getenv("ACTIVE_SEASON", "2025"))

def main():
    # 1) pull season totals from nba_api
    totals = build_season_totals(ACTIVE_SEASON)
    if totals.empty:
        print("No data pulled; exiting.")
        return

    # 2) compute metrics
    per  = compute_per(totals)
    wsdf = compute_win_shares(totals)
    bmpdf= compute_bmp_vorp(totals)

    df = totals.join(per).join(wsdf).join(bmpdf)

    # 3) qualification + ranks + composite
    df["qualified"] = qualify(df, min_minutes=1000)
    ranked = compute_ranks_and_huss(df)

    # 4) TODO: read yesterday's snapshot from DB for trends
    prev = pd.DataFrame()
    ranked = with_trend(ranked, prev)

    # 5) TODO: upsert to Postgres (stats + ranks) within a transaction
    # 6) print quick log (top 5)
    top5 = ranked.sort_values("huss_rank").head(5)[["player","team","huss_rank","huss_score"]]
    print("Top 5 HussEyquation Rankings:")
    print(top5.to_string(index=False))

if __name__ == "__main__":
    main()