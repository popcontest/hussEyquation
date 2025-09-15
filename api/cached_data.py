"""
Cached NBA player data for production deployment.
This replaces database calls with static data for reliability.
"""
from datetime import datetime

# Cached player rankings data - this would normally come from database
CACHED_RANKINGS = {
    "2025": [
        {"name": "Nikola Jokic", "team": "DEN", "position": "C", "gp": 76, "min": 34.6, "pts": 26.4, "reb": 12.4, "ast": 9.0, "stl": 1.4, "blk": 0.9, "fg_pct": 0.583, "ft_pct": 0.821, "score": 1.2, "rank": 1},
        {"name": "Luka Doncic", "team": "DAL", "position": "PG", "gp": 70, "min": 36.2, "pts": 32.4, "reb": 8.2, "ast": 8.0, "stl": 1.4, "blk": 0.5, "fg_pct": 0.487, "ft_pct": 0.786, "score": 1.8, "rank": 2},
        {"name": "Shai Gilgeous-Alexander", "team": "OKC", "position": "PG", "gp": 75, "min": 34.1, "pts": 30.1, "reb": 5.5, "ast": 6.2, "stl": 2.0, "blk": 0.9, "fg_pct": 0.535, "ft_pct": 0.874, "score": 2.1, "rank": 3},
        {"name": "Jayson Tatum", "team": "BOS", "position": "SF", "gp": 74, "min": 35.7, "pts": 26.9, "reb": 8.1, "ast": 4.9, "stl": 1.0, "blk": 0.6, "fg_pct": 0.471, "ft_pct": 0.831, "score": 2.3, "rank": 4},
        {"name": "Giannis Antetokounmpo", "team": "MIL", "position": "PF", "gp": 73, "min": 35.2, "pts": 30.4, "reb": 11.5, "ast": 6.5, "stl": 1.2, "blk": 1.1, "fg_pct": 0.611, "ft_pct": 0.642, "score": 2.4, "rank": 5},
        {"name": "Jaylen Brown", "team": "BOS", "position": "SG", "gp": 70, "min": 33.9, "pts": 23.0, "reb": 5.5, "ast": 3.6, "stl": 1.2, "blk": 0.4, "fg_pct": 0.493, "ft_pct": 0.701, "score": 2.6, "rank": 6},
        {"name": "Anthony Edwards", "team": "MIN", "position": "SG", "gp": 79, "min": 35.1, "pts": 25.9, "reb": 5.4, "ast": 5.1, "stl": 1.3, "blk": 0.5, "fg_pct": 0.460, "ft_pct": 0.831, "score": 2.7, "rank": 7},
        {"name": "Donovan Mitchell", "team": "CLE", "position": "SG", "gp": 55, "min": 35.9, "pts": 26.6, "reb": 5.1, "ast": 6.1, "stl": 1.8, "blk": 0.4, "fg_pct": 0.464, "ft_pct": 0.867, "score": 2.8, "rank": 8},
        {"name": "Tyrese Haliburton", "team": "IND", "position": "PG", "gp": 69, "min": 32.7, "pts": 20.1, "reb": 3.9, "ast": 10.9, "stl": 1.2, "blk": 0.7, "fg_pct": 0.473, "ft_pct": 0.854, "score": 2.9, "rank": 9},
        {"name": "Kawhi Leonard", "team": "LAC", "position": "SF", "gp": 68, "min": 34.0, "pts": 23.7, "reb": 6.1, "ast": 3.6, "stl": 1.6, "blk": 0.9, "fg_pct": 0.524, "ft_pct": 0.883, "score": 3.0, "rank": 10},
        {"name": "LeBron James", "team": "LAL", "position": "SF", "gp": 71, "min": 35.3, "pts": 25.7, "reb": 7.3, "ast": 8.3, "stl": 1.3, "blk": 0.5, "fg_pct": 0.540, "ft_pct": 0.750, "score": 3.1, "rank": 11},
        {"name": "Anthony Davis", "team": "LAL", "position": "PF", "gp": 76, "min": 35.5, "pts": 24.7, "reb": 12.6, "ast": 3.5, "stl": 1.2, "blk": 2.3, "fg_pct": 0.557, "ft_pct": 0.819, "score": 3.2, "rank": 12},
        {"name": "Devin Booker", "team": "PHX", "position": "SG", "gp": 68, "min": 35.4, "pts": 27.1, "reb": 4.5, "ast": 6.9, "stl": 0.9, "blk": 0.5, "fg_pct": 0.466, "ft_pct": 0.884, "score": 3.3, "rank": 13},
        {"name": "Trae Young", "team": "ATL", "position": "PG", "gp": 54, "min": 35.4, "pts": 25.7, "reb": 2.8, "ast": 10.8, "stl": 1.1, "blk": 0.2, "fg_pct": 0.431, "ft_pct": 0.854, "score": 3.4, "rank": 14},
        {"name": "Paolo Banchero", "team": "ORL", "position": "PF", "gp": 80, "min": 35.0, "pts": 22.6, "reb": 6.9, "ast": 5.4, "stl": 0.9, "blk": 0.7, "fg_pct": 0.450, "ft_pct": 0.739, "score": 3.5, "rank": 15},
        {"name": "Karl-Anthony Towns", "team": "NYK", "position": "C", "gp": 77, "min": 33.0, "pts": 24.8, "reb": 9.9, "ast": 3.0, "stl": 0.7, "blk": 0.9, "fg_pct": 0.504, "ft_pct": 0.871, "score": 3.6, "rank": 16},
        {"name": "Jalen Brunson", "team": "NYK", "position": "PG", "gp": 77, "min": 35.4, "pts": 28.7, "reb": 3.6, "ast": 6.7, "stl": 0.9, "blk": 0.2, "fg_pct": 0.479, "ft_pct": 0.840, "score": 3.7, "rank": 17},
        {"name": "Scottie Barnes", "team": "TOR", "position": "SF", "gp": 60, "min": 34.1, "pts": 19.9, "reb": 8.2, "ast": 6.1, "stl": 1.3, "blk": 1.5, "fg_pct": 0.473, "ft_pct": 0.739, "score": 3.8, "rank": 18},
        {"name": "Alperen Sengun", "team": "HOU", "position": "C", "gp": 63, "min": 32.7, "pts": 21.1, "reb": 9.3, "ast": 5.0, "stl": 1.2, "blk": 0.9, "fg_pct": 0.535, "ft_pct": 0.693, "score": 3.9, "rank": 19},
        {"name": "Mikal Bridges", "team": "NYK", "position": "SF", "gp": 82, "min": 35.0, "pts": 19.6, "reb": 4.5, "ast": 3.5, "stl": 1.0, "blk": 0.8, "fg_pct": 0.434, "ft_pct": 0.813, "score": 4.0, "rank": 20}
    ],
    "2024": [
        {"name": "Nikola Jokic", "team": "DEN", "position": "C", "gp": 79, "min": 34.6, "pts": 26.4, "reb": 12.4, "ast": 9.0, "stl": 1.4, "blk": 0.9, "fg_pct": 0.583, "ft_pct": 0.817, "score": 1.1, "rank": 1},
        {"name": "Shai Gilgeous-Alexander", "team": "OKC", "position": "PG", "gp": 75, "min": 34.2, "pts": 30.1, "reb": 5.5, "ast": 6.2, "stl": 2.0, "blk": 0.9, "fg_pct": 0.535, "ft_pct": 0.874, "score": 1.3, "rank": 2},
        {"name": "Luka Doncic", "team": "DAL", "position": "PG", "gp": 70, "min": 36.1, "pts": 32.4, "reb": 8.2, "ast": 8.0, "stl": 1.4, "blk": 0.5, "fg_pct": 0.487, "ft_pct": 0.786, "score": 1.4, "rank": 3},
        {"name": "Jayson Tatum", "team": "BOS", "position": "SF", "gp": 74, "min": 35.7, "pts": 26.9, "reb": 8.1, "ast": 4.9, "stl": 1.0, "blk": 0.6, "fg_pct": 0.471, "ft_pct": 0.831, "score": 1.6, "rank": 4},
        {"name": "Giannis Antetokounmpo", "team": "MIL", "position": "PF", "gp": 73, "min": 35.2, "pts": 30.4, "reb": 11.5, "ast": 6.5, "stl": 1.2, "blk": 1.1, "fg_pct": 0.611, "ft_pct": 0.642, "score": 1.7, "rank": 5}
    ],
    "2023": [
        {"name": "Nikola Jokic", "team": "DEN", "position": "C", "gp": 69, "min": 33.7, "pts": 24.5, "reb": 11.8, "ast": 9.8, "stl": 1.3, "blk": 0.7, "fg_pct": 0.632, "ft_pct": 0.824, "score": 1.0, "rank": 1},
        {"name": "Joel Embiid", "team": "PHI", "position": "C", "gp": 66, "min": 34.6, "pts": 33.1, "reb": 10.2, "ast": 4.2, "stl": 1.0, "blk": 1.7, "fg_pct": 0.548, "ft_pct": 0.856, "score": 1.2, "rank": 2},
        {"name": "Giannis Antetokounmpo", "team": "MIL", "position": "PF", "gp": 63, "min": 32.1, "pts": 31.1, "reb": 11.8, "ast": 5.7, "stl": 0.8, "blk": 0.8, "fg_pct": 0.553, "ft_pct": 0.645, "score": 1.4, "rank": 3},
        {"name": "Jayson Tatum", "team": "BOS", "position": "SF", "gp": 74, "min": 36.9, "pts": 30.1, "reb": 8.8, "ast": 4.6, "stl": 1.1, "blk": 0.7, "fg_pct": 0.466, "ft_pct": 0.851, "score": 1.5, "rank": 4},
        {"name": "Luka Doncic", "team": "DAL", "position": "PG", "gp": 66, "min": 36.2, "pts": 32.4, "reb": 8.6, "ast": 8.0, "stl": 1.4, "blk": 0.5, "fg_pct": 0.456, "ft_pct": 0.743, "score": 1.6, "rank": 5}
    ]
}

def get_cached_rankings(season: str, qualified: bool = True, limit: int = 50, offset: int = 0):
    """
    Get cached player rankings for a season.
    This replaces the database call with static data.
    """
    players = CACHED_RANKINGS.get(season, [])
    
    # Apply qualified filter if needed (for demo, all players are "qualified")
    if not qualified:
        # In real implementation, you might have additional unqualified players
        pass
    
    # Apply pagination
    total_count = len(players)
    paginated_players = players[offset:offset + limit]
    
    return {
        "players": paginated_players,
        "pagination": {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count
        },
        "season": season,
        "qualified_only": qualified,
        "last_updated": datetime.now().isoformat()
    }