#!/usr/bin/env python3
"""
Test Alperen name matching between seasons
"""

import sqlite3
import requests

def test_alperen_database():
    """Test Alperen matching in database"""
    conn = sqlite3.connect("../db/husseyquation.sqlite")
    cursor = conn.cursor()
    
    # Check Alperen players in both seasons
    cursor.execute('''
        SELECT s.season_id, p.full_name, p.normalized_name, r.huss_rank
        FROM players p
        JOIN player_snapshot_ranks r ON p.player_id = r.player_id
        JOIN snapshots s ON r.snapshot_id = s.snapshot_id
        WHERE p.normalized_name LIKE '%alperen%'
        ORDER BY s.season_id, r.huss_rank
    ''')
    
    results = cursor.fetchall()
    print("Alperen players found in database:")
    for season, full_name, normalized_name, rank in results:
        print(f"  Season {season}: '{full_name}' -> '{normalized_name}' (Rank {rank})")
    
    # Test the normalized matching query manually
    print("\nTesting normalized matching query:")
    cursor.execute('''
        SELECT 
            p2025.full_name as name_2025,
            p2024.full_name as name_2024,
            r2025.huss_rank as rank_2025,
            r2024.huss_rank as rank_2024,
            r2024.huss_rank - r2025.huss_rank as rank_change
        FROM players p2025
        JOIN player_snapshot_ranks r2025 ON p2025.player_id = r2025.player_id
        JOIN snapshots s2025 ON r2025.snapshot_id = s2025.snapshot_id AND s2025.season_id = 2025
        JOIN players p2024 ON p2025.normalized_name = p2024.normalized_name
        JOIN player_snapshot_ranks r2024 ON p2024.player_id = r2024.player_id  
        JOIN snapshots s2024 ON r2024.snapshot_id = s2024.snapshot_id AND s2024.season_id = 2024
        WHERE p2025.normalized_name LIKE '%alperen%'
    ''')
    
    match_results = cursor.fetchall()
    if match_results:
        print("  Successful matches:")
        for name_2025, name_2024, rank_2025, rank_2024, change in match_results:
            direction = "UP" if change > 0 else "DOWN" if change < 0 else "SAME"
            print(f"    '{name_2025}' (2025 #{rank_2025}) matched with '{name_2024}' (2024 #{rank_2024}) - {direction} ({change:+d})")
    else:
        print("  No matches found - this indicates the matching logic needs work")
    
    conn.close()

def test_api_endpoint():
    """Test API endpoint for Alperen"""
    try:
        response = requests.get("http://localhost:8000/api/seasons/2025/rankings?limit=50&qualified=false")
        if response.status_code == 200:
            data = response.json()
            alperen_players = [p for p in data['players'] if 'alperen' in p['player_name'].lower()]
            
            print(f"\nAPI test - found {len(alperen_players)} Alperen players:")
            for player in alperen_players:
                print(f"  {player['player_name']} (Rank #{player['rank']}) - {player['trend_direction']} (change: {player['rank_change']:+d})")
        else:
            print(f"API request failed with status {response.status_code}")
    except Exception as e:
        print(f"API test failed: {e}")

if __name__ == "__main__":
    test_alperen_database()
    test_api_endpoint()