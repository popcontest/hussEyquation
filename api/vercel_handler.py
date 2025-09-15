from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import os
from datetime import datetime
import hashlib
import json

app = FastAPI(
    title="HussEyquation API",
    description="NBA Player Rankings using the HussEyquation composite metric",
    version="1.0.0"
)

# CORS middleware for frontend
cors_origins = ["http://localhost:3000", "https://husseyquation.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Cache control headers
CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
    "Vary": "Accept-Encoding"
}

def generate_etag(content: Any) -> str:
    """Generate ETag from content hash."""
    content_str = json.dumps(content, sort_keys=True, default=str)
    return f'"{hashlib.md5(content_str.encode()).hexdigest()}"'

# Sample data for demonstration
SAMPLE_PLAYERS = [
    {"name": "Nikola Jokic", "team": "DEN", "position": "C", "gp": 76, "min": 34.6, "pts": 26.4, "reb": 12.4, "ast": 9.0, "score": 1.2, "rank": 1},
    {"name": "Luka Doncic", "team": "DAL", "position": "PG", "gp": 70, "min": 36.2, "pts": 32.4, "reb": 8.2, "ast": 8.0, "score": 1.8, "rank": 2},
    {"name": "Shai Gilgeous-Alexander", "team": "OKC", "position": "PG", "gp": 75, "min": 34.1, "pts": 30.1, "reb": 5.5, "ast": 6.2, "score": 2.1, "rank": 3},
    {"name": "Jayson Tatum", "team": "BOS", "position": "SF", "gp": 74, "min": 35.7, "pts": 26.9, "reb": 8.1, "ast": 4.9, "score": 2.3, "rank": 4},
    {"name": "Giannis Antetokounmpo", "team": "MIL", "position": "PF", "gp": 73, "min": 35.2, "pts": 30.4, "reb": 11.5, "ast": 6.5, "score": 2.4, "rank": 5}
]

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "husseyquation-api"
    }

@app.get("/api/seasons/{season}/rankings")
async def get_season_rankings(
    season: str,
    limit: int = Query(50, ge=1, le=1000, description="Number of players to return"),
    offset: int = Query(0, ge=0, description="Number of players to skip"),
    qualified: bool = Query(True, description="Only include qualified players")
):
    """Get player rankings for a specific season."""
    
    # For demo purposes, return sample data
    players = SAMPLE_PLAYERS.copy()
    
    # Apply pagination
    total_count = len(players)
    paginated_players = players[offset:offset + limit]
    
    response_data = {
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
    
    etag = generate_etag(response_data)
    
    return JSONResponse(
        content=response_data,
        headers={**CACHE_HEADERS, "ETag": etag}
    )

# Vercel handler
handler = app