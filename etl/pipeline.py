from __future__ import annotations
import pandas as pd
import numpy as np

METRICS = ["PER","WS","WS/48","BPM","VORP"]

def qualify(df: pd.DataFrame, min_minutes: int = 1000) -> pd.Series:
    return (df["mp"].fillna(0) >= min_minutes)

def dense_rank_desc(s: pd.Series) -> pd.Series:
    return s.rank(method="dense", ascending=False)

def compute_ranks_and_huss(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # rank each metric (descending)
    out["per_rank"]   = dense_rank_desc(out["PER"])
    out["ws_rank"]    = dense_rank_desc(out["WS"])
    out["ws48_rank"]  = dense_rank_desc(out["WS/48"])
    out["bmp_rank"]   = dense_rank_desc(out["BPM"])
    out["vorp_rank"]  = dense_rank_desc(out["VORP"])

    rank_cols = ["per_rank","ws_rank","ws48_rank","bmp_rank","vorp_rank"]
    out["huss_score"] = out[rank_cols].mean(axis=1)
    out["huss_rank"]  = out["huss_score"].rank(method="dense", ascending=True)
    return out

def with_trend(curr: pd.DataFrame, prev: pd.DataFrame | None) -> pd.DataFrame:
    if prev is None or prev.empty:
        curr["delta_1d"] = 0
        curr["delta_7d"] = 0
        curr["delta_14d"] = 0
        return curr
    prev_slim = prev[["nba_player_id","huss_rank"]].rename(columns={"huss_rank":"prev_rank"})
    out = curr.merge(prev_slim, on="nba_player_id", how="left")
    out["delta_1d"] = (out["prev_rank"] - out["huss_rank"]).fillna(0).astype(int)
    # You'll compute 7d/14d using snapshots table when wiring DB reads.
    out["delta_7d"] = 0
    out["delta_14d"] = 0
    return out