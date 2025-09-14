from __future__ import annotations
from typing import List, Dict
import pandas as pd
from nba_api.stats.endpoints import leaguegamelog, boxscoretraditionalv3, boxscoreadvancedv3
from time import sleep

def get_season_game_ids(season_end_year: int) -> List[str]:
    """
    Returns NBA.com GameIDs for a season (e.g., 2025 for 2024-25 season).
    """
    season_str = f"{season_end_year-1}-{str(season_end_year)[-2:]}"
    gl = leaguegamelog.LeagueGameLog(season=season_str, season_type_all_star="Regular Season")
    df = gl.get_data_frames()[0]
    # NBA GameIDs look like "00222xxxxx" for regular season
    return df["GAME_ID"].dropna().astype(str).unique().tolist()

def fetch_box_traditional(game_id: str) -> Dict[str, pd.DataFrame]:
    """
    Traditional per-game box (minutes, points, FGA, FTA, REB, AST, STL, BLK, TOV, PF, etc.).
    """
    resp = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game_id)
    frames = resp.get_data_frames()
    # frames: [PlayerTraditional, TeamTraditional, ...] – rely on index order
    return {
        "player_trad": frames[0].copy(),
        "team_trad": frames[1].copy()
    }

def fetch_box_advanced(game_id: str) -> Dict[str, pd.DataFrame]:
    """
    Advanced per-game box (pace, ortg/drtg, usage, etc.).
    """
    resp = boxscoreadvancedv3.BoxScoreAdvancedV3(game_id=game_id)
    frames = resp.get_data_frames()
    return {
        "player_adv": frames[0].copy(),
        "team_adv": frames[1].copy()
    }

def build_season_totals(season_end_year: int, throttle_sec: float = 0.6) -> pd.DataFrame:
    """
    Loops game_ids → joins traditional + advanced → aggregates to per-player season totals.
    Returns DataFrame with counting stats needed for PER/WS/BPM/VORP.
    """
    game_ids = get_season_game_ids(season_end_year)
    rows = []
    for gid in game_ids:
        try:
            trad = fetch_box_traditional(gid)
            adv  = fetch_box_advanced(gid)
        except Exception:
            # endpoints can hiccup; skip this game and continue
            continue
        # join player-level traditional and advanced by PLAYER_ID / TEAM_ID
        p = pd.merge(
            trad["player_trad"],
            adv["player_adv"],
            on=["PLAYER_ID","TEAM_ID","GAME_ID"],
            how="left",
            suffixes=("_trad","_adv")
        )
        rows.append(p)
        sleep(throttle_sec)  # be polite; endpoints are undocumented

    all_games = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    # Minimal rename/select; normalize minutes to integer, etc.
    # Keep only columns needed for metric calcs; you'll refine as you implement metrics.
    keep = {
        "PLAYER_ID":"nba_player_id",
        "PLAYER_NAME":"player",
        "TEAM_ID":"nba_team_id",
        "TEAM_ABBREVIATION":"team",
        "MIN":"mp",
        "FGA":"fga","FGM":"fgm",
        "FG3A":"fg3a","FG3M":"fg3m",
        "FTA":"fta","FTM":"ftm",
        "OREB":"oreb","DREB":"dreb","REB":"trb",
        "AST":"ast","STL":"stl","BLK":"blk",
        "TOV":"tov","PF":"pf",
        # advanced (examples; keep what you'll use)
        "PACE":"pace","OFF_RATING":"ortg","DEF_RATING":"drtg","USG_PCT":"usg_pct"
    }
    df = all_games.rename(columns=keep)[list(keep.values())].copy()
    # coerce numerics, handle mm:ss minutes
    def parse_min(x):
        if isinstance(x, str) and ":" in x:
            m,s = x.split(":")
            return int(m) + int(s)/60.0
        return pd.to_numeric(x, errors="coerce")

    df["mp"] = df["mp"].apply(parse_min)
    num_cols = [c for c in df.columns if c not in ["player","team","nba_player_id","nba_team_id"]]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")

    # aggregate to season totals by player
    agg_map = {c:"sum" for c in ["mp","fga","fgm","fg3a","fg3m","fta","ftm",
                                 "oreb","dreb","trb","ast","stl","blk","tov","pf"]}
    # keep simple team context by most frequent team code
    totals = df.groupby(["nba_player_id","player"]).agg(agg_map)
    # attach a representative team (mode)
    team_mode = df.groupby(["nba_player_id"])["team"].agg(lambda s: s.mode().iat[0] if not s.mode().empty else None)
    totals["team"] = team_mode
    totals = totals.reset_index()
    return totals