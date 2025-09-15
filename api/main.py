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

# Import cached data (for production deployment reliability)
from cached_data import get_cached_rankings

app = FastAPI(
    title="HussEyquation API",
    description="NBA Player Rankings using the HussEyquation composite metric",
    version="1.0.0"
)

# CORS middleware for frontend
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,https://husseyquation.vercel.app").split(",")
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

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "husseyquation-api"
    }

# Using cached data adapter for production reliability
class CachedDataAdapter:
    def get_season_rankings(self, season: int, qualified: bool = True, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        # Use cached data instead of database for reliability
        result = get_cached_rankings(str(season), qualified, limit or 50, offset)
        
        # Add season name for backward compatibility
        result["season_name"] = f"{season-1}-{str(season)[2:]}"
        
        return result

db = CachedDataAdapter()

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
    window: str = Query("7d", description="Time window for trending", pattern="^(1d|7d|14d)$")
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

# Vercel serverless function handler
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )