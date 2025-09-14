from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import os
from datetime import datetime, timedelta
import hashlib
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="HussEyquation API",
    description="NBA Player Rankings using the HussEyquation composite metric",
    version="1.0.0"
)

# CORS middleware for frontend
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Cache control headers
CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",  # Disable cache
    "Pragma": "no-cache",
    "Expires": "0",
    "Vary": "Accept-Encoding"
}

def generate_etag(content: Any) -> str:
    """Generate ETag from content hash."""
    content_str = json.dumps(content, sort_keys=True, default=str)
    return f'"{hashlib.md5(content_str.encode()).hexdigest()}"'

# Use existing database file instead of auto-generating
import sqlite3
from typing import Dict, Any

class SimpleDB:
    def __init__(self):
        # Use environment variable for database path, fallback to local production DB or development path
        self.db_path = os.getenv("DATABASE_PATH", "./husseyquation.sqlite" if os.path.exists("./husseyquation.sqlite") else "../db/husseyquation.sqlite")
    
    def get_season_rankings(self, season: int, qualified: bool = True, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get the latest snapshot for the requested season
            where_clause = f"WHERE r.snapshot_id = (SELECT MAX(snapshot_id) FROM snapshots WHERE season_id = {season})"
            if qualified:
                where_clause += " AND r.qualified = 1"
            
            # Main query with year-over-year comparison
            query = f"""
                SELECT 
                    r.huss_rank as rank, p.player_id, p.full_name as player_name,
                    t.abbr as team, p.primary_pos as position, r.huss_score,
                    s.per, r.per_rank, s.ws, r.ws_rank, s.ws48, r.ws48_rank,
                    s.bpm, r.bpm_rank, s.vorp, r.vorp_rank,
                    s.g as games, s.mp as minutes, r.qualified,
                    -- Year-over-year comparison
                    COALESCE(prev.huss_rank - r.huss_rank, 0) as rank_change,
                    COALESCE(prev.huss_rank, 0) as previous_rank,
                    CASE 
                        WHEN prev.huss_rank IS NULL THEN 'NEW'
                        WHEN prev.huss_rank > r.huss_rank THEN 'UP'
                        WHEN prev.huss_rank < r.huss_rank THEN 'DOWN'
                        ELSE 'SAME'
                    END as trend_direction,
                    0 as trend_1d, 0 as trend_7d, 0 as trend_14d
                FROM player_snapshot_ranks r
                JOIN players p ON r.player_id = p.player_id
                JOIN player_snapshot_stats s ON r.snapshot_id = s.snapshot_id AND r.player_id = s.player_id
                JOIN teams t ON s.team_id = t.team_id
                -- Left join with previous season data using normalized names
                LEFT JOIN (
                    SELECT pr.*, p_prev.normalized_name
                    FROM player_snapshot_ranks pr 
                    JOIN players p_prev ON pr.player_id = p_prev.player_id
                    WHERE pr.snapshot_id = (
                        SELECT MAX(snapshot_id) FROM snapshots 
                        WHERE season_id = {season - 1}
                    )
                ) prev ON prev.normalized_name = p.normalized_name
                {where_clause}
                ORDER BY r.huss_rank
            """
            
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
            
            players = [dict(row) for row in conn.execute(query).fetchall()]
            total_count = len(players) if not limit else conn.execute(f"SELECT COUNT(*) FROM player_snapshot_ranks r JOIN players p ON r.player_id = p.player_id JOIN player_snapshot_stats s ON r.snapshot_id = s.snapshot_id AND r.player_id = s.player_id JOIN teams t ON s.team_id = t.team_id {where_clause}").fetchone()[0]
            
            # Get season info
            season_info = conn.execute("SELECT start_date, end_date FROM seasons WHERE season_id = ?", (season,)).fetchone()
            last_updated = datetime.now().isoformat()
            
            return {
                "players": players,
                "total_count": total_count,
                "season": season,
                "season_name": f"{season-1}-{str(season)[2:]}",
                "last_updated": last_updated
            }

db = SimpleDB()

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "HussEyquation API",
        "version": "1.0.0",
        "endpoints": [
            "/api/seasons/{season}/rankings",
            "/api/seasons/{season}/trending", 
            "/api/players/{player_id}",
            "/api/players/{player_id}/history"
        ]
    }

@app.get("/api/seasons/{season}/rankings")
async def get_season_rankings(
    season: int = Path(..., description="Season ending year (e.g., 2025 for 2024-25 season)", ge=2016, le=2030),
    qualified: bool = Query(True, description="Only show qualified players (1000+ minutes)"),
    limit: Optional[int] = Query(None, description="Number of players to return (leave empty for all)", ge=1, le=1000),
    offset: int = Query(0, description="Number of players to skip", ge=0)
):
    """Get player rankings for a season."""
    try:
        response_data = db.get_season_rankings(season, qualified, limit, offset)
        response_data.update({
            "qualified": qualified,
            "limit": limit,
            "offset": offset
        })
        
        # Generate ETag
        etag = generate_etag(response_data)
        
        return JSONResponse(
            content=response_data,
            headers={**CACHE_HEADERS, "ETag": etag}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/seasons/{season}/trending")
async def get_trending_players(
    season: int = Path(..., description="Season ending year", ge=2016, le=2030),
    window: str = Query("7d", description="Time window for trending", regex="^(1d|7d|14d)$")
):
    """Get trending players (biggest movers) for a season."""
    # For now, return sample trending data
    response_data = {
        "season": season,
        "window": window,
        "trending_up": [],
        "trending_down": [],
        "last_updated": datetime.now().isoformat()
    }
    
    etag = generate_etag(response_data)
    
    return JSONResponse(
        content=response_data,
        headers={**CACHE_HEADERS, "ETag": etag}
    )

@app.get("/api/players/{player_id}")
async def get_player_profile(
    player_id: int = Path(..., description="Player ID", ge=1)
):
    """Get current season player profile with rank history."""
    # For now, return sample player data
    response_data = {
        "player_id": player_id,
        "player_name": "Sample Player",
        "rank_history": [],
        "current_season": 2025,
        "last_updated": datetime.now().isoformat()
    }
    
    etag = generate_etag(response_data)
    
    return JSONResponse(
        content=response_data,
        headers={**CACHE_HEADERS, "ETag": etag}
    )

@app.get("/api/players/{player_id}/history")
async def get_player_history(
    player_id: int = Path(..., description="Player ID", ge=1)
):
    """Get player's historical season finishes."""
    response_data = {
        "player_id": player_id,
        "player_name": "Sample Player",
        "history": [],
        "seasons_qualified": 0,
        "best_huss_rank": None,
        "last_updated": datetime.now().isoformat()
    }
    
    etag = generate_etag(response_data)
    
    return JSONResponse(
        content=response_data,
        headers={**CACHE_HEADERS, "ETag": etag}
    )

@app.get("/api/leaderboards/all-time")
async def get_all_time_leaderboards():
    """Get all-time leaderboard stats (best single seasons, most #1s, etc.)."""
    # TODO: Replace with actual database queries
    
    response_data = {
        "best_single_seasons": [
            {"player_name": "Nikola Jokic", "season": 2021, "huss_score": 1.8},
            {"player_name": "Giannis Antetokounmpo", "season": 2020, "huss_score": 2.1}
        ],
        "most_number_ones": [
            {"player_name": "LeBron James", "count": 4},
            {"player_name": "Michael Jordan", "count": 6}
        ],
        "most_top_tens": [
            {"player_name": "LeBron James", "count": 15},
            {"player_name": "Tim Duncan", "count": 12}
        ],
        "last_updated": datetime.now().isoformat()
    }
    
    etag = generate_etag(response_data)
    
    return JSONResponse(
        content=response_data,
        headers={**CACHE_HEADERS, "ETag": etag}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )