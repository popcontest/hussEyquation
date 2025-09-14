from __future__ import annotations
import pandas as pd
import numpy as np

def compute_per(season_totals: pd.DataFrame) -> pd.Series:
    """
    Return a PER Series aligned to season_totals.index.
    Steps (simplified outline):
      1) Compute uPER from counting stats (fg, 3pt, ft, tov, ast, trb, stl, blk, pf, …)
      2) Adjust for pace/league factors (needs league-level aggregates)
      3) Normalize so league-average PER = 15.00 (scale factor)
    Reference: Basketball-Reference PER explainer + Hollinger notes.
    """
    # Simplified PER calculation (placeholder implementation)
    # Full PER requires league-level context and complex formulas
    df = season_totals.copy()
    
    # Basic per-minute efficiency 
    df['pts_per_min'] = df['pts'] / df['mp'].replace(0, np.nan) if 'pts' in df else 0
    df['ast_per_min'] = df['ast'] / df['mp'].replace(0, np.nan)
    df['trb_per_min'] = df['trb'] / df['mp'].replace(0, np.nan)
    df['stl_per_min'] = df['stl'] / df['mp'].replace(0, np.nan)
    df['blk_per_min'] = df['blk'] / df['mp'].replace(0, np.nan)
    df['tov_per_min'] = df['tov'] / df['mp'].replace(0, np.nan)
    df['fg_miss_per_min'] = (df['fga'] - df['fgm']) / df['mp'].replace(0, np.nan)
    
    # Simplified efficiency calculation
    uper = (
        df['pts_per_min'] * 1.0 +
        df['ast_per_min'] * 1.5 +
        df['trb_per_min'] * 1.2 +
        df['stl_per_min'] * 2.0 +
        df['blk_per_min'] * 2.0 -
        df['tov_per_min'] * 1.5 -
        df['fg_miss_per_min'] * 0.5
    ).fillna(0)
    
    # Normalize to league average = 15.0
    league_avg = uper.mean() if uper.mean() > 0 else 1
    per = (uper / league_avg) * 15.0
    
    return per.rename("PER")

def compute_win_shares(season_totals: pd.DataFrame,
                       team_context: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Compute Win Shares (WS) and WS/48.
    Outline:
      - Offensive WS: based on offensive rating & possessions produced
      - Defensive WS: based on defensive rating & team defense context
      - WS = oWS + dWS; WS48 = WS * 48 / MP (guard MP==0)
    Reference: BBR WS methodology.
    Returns DataFrame with columns ["WS","WS/48"].
    """
    df = season_totals.copy()
    
    # Simplified Win Shares calculation
    # True WS requires team and league context
    
    # Estimate possessions and efficiency
    df['poss_used'] = df['fga'] - df['oreb'] + df['tov'] + 0.44 * df['fta']
    df['pts_produced'] = df['fgm'] * 2 + df['fg3m'] + df['ftm']
    
    # Simple offensive contribution
    df['off_efficiency'] = df['pts_produced'] / df['poss_used'].replace(0, np.nan)
    league_off_avg = 1.1  # approximate
    df['ows'] = ((df['off_efficiency'] - league_off_avg) * df['poss_used'] / 100).fillna(0)
    
    # Simple defensive contribution (based on defensive stats)
    df['def_contribution'] = df['stl'] + df['blk'] + df['dreb'] * 0.2
    df['dws'] = df['def_contribution'] / 100
    
    # Total Win Shares
    ws = (df['ows'] + df['dws']).fillna(0).rename("WS")
    ws48 = (ws * 48 / df['mp'].replace(0, np.nan)).fillna(0).rename("WS/48")
    
    return pd.DataFrame({"WS": ws, "WS/48": ws48})

def compute_bmp_vorp(season_totals: pd.DataFrame,
                     league_context: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Compute BPM (v2.0) and VORP.
    Outline:
      - Fit/apply box-score regression with position & era adjustments
      - VORP scales BPM by playing time vs replacement level (-2.0 BPM)
    Reference: Sports-Reference BPM 2.0 explainer.
    
    Note: This is an approximate implementation. Full BPM 2.0 requires
    proprietary regression coefficients and adjustments not publicly available.
    """
    df = season_totals.copy()
    
    # Calculate per-100-possession stats (simplified)
    df['poss_est'] = df['fga'] - df['oreb'] + df['tov'] + 0.44 * df['fta']
    df['poss_per_min'] = df['poss_est'] / df['mp'].replace(0, np.nan)
    
    # Scale to per-100 possessions
    scale = 100 / (df['poss_per_min'] * df['mp']).replace(0, np.nan).fillna(1)
    
    # Basic box score stats per 100 possessions
    df['ast_100'] = df['ast'] * scale
    df['trb_100'] = df['trb'] * scale  
    df['stl_100'] = df['stl'] * scale
    df['blk_100'] = df['blk'] * scale
    df['tov_100'] = df['tov'] * scale
    df['pts_100'] = df['fgm'] * 2 + df['fg3m'] + df['ftm']
    df['pts_100'] = df['pts_100'] * scale
    
    # Simplified BPM regression (approximate coefficients)
    bmp = (
        df['pts_100'] * 0.123 +
        df['ast_100'] * 0.324 +
        df['trb_100'] * 0.183 +
        df['stl_100'] * 0.691 +
        df['blk_100'] * 0.456 -
        df['tov_100'] * 0.255
    ).fillna(0)
    
    # Center around league average (0.0)
    if bmp.std() > 0:
        bmp = (bmp - bmp.mean())
    
    # VORP: (BPM - replacement level) * fraction of team possessions
    replacement_level = -2.0
    team_poss_per_game = 100  # approximate
    games_in_season = 82
    
    vorp = ((bmp - replacement_level) * 
           (df['mp'] / (games_in_season * 48)) * 
           (games_in_season * team_poss_per_game / 100) / 30.5).fillna(0)
    
    return pd.DataFrame({"BPM": bmp.rename("BPM"), "VORP": vorp.rename("VORP")})