#!/usr/bin/env python3
"""
Create mock 2023-24 season data for year-over-year comparison
This will show realistic ranking changes between seasons
"""

import sqlite3
import random
from datetime import datetime

def create_mock_previous_season(db_path):
    """Create realistic 2023-24 season data for comparison"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Insert 2024 season (2023-24)
    cursor.execute('''
        INSERT OR IGNORE INTO seasons (season_id, start_date, end_date, status)
        VALUES (?, ?, ?, ?)
    ''', (2024, '2023-10-01', '2024-04-15', 'completed'))
    
    # Create snapshot for 2023-24 season
    snapshot_date = '2024-04-15'  # End of previous season
    cursor.execute('''
        INSERT INTO snapshots (season_id, snapshot_date, source_hash)
        VALUES (?, ?, ?)
    ''', (2024, snapshot_date, 'mock_2023_24_season'))
    mock_snapshot_id = cursor.lastrowid
    
    print(f"Created mock snapshot {mock_snapshot_id} for 2023-24 season")
    
    # Get current season players (top 100 for realistic comparison)
    cursor.execute('''
        SELECT p.player_id, p.full_name, r.huss_rank, r.huss_score,
               s.per, s.ws, s.ws48, s.bpm, s.vorp, s.g, s.mp, s.team_id
        FROM player_snapshot_ranks r
        JOIN players p ON r.player_id = p.player_id
        JOIN player_snapshot_stats s ON r.snapshot_id = s.snapshot_id AND r.player_id = s.player_id
        WHERE r.snapshot_id = (SELECT MAX(snapshot_id) FROM snapshots WHERE season_id = 2025)
        AND r.huss_rank <= 100
        ORDER BY r.huss_rank
    ''')
    
    current_players = cursor.fetchall()
    print(f"Processing {len(current_players)} top players for mock previous season")
    
    # Create realistic year-over-year changes
    mock_rankings = []
    
    for i, (player_id, name, current_rank, current_score, per, ws, ws48, bpm, vorp, games, minutes, team_id) in enumerate(current_players):
        # Skip some players (simulate them not being in top 100 last year)
        if random.random() < 0.15:  # 15% chance to skip (new to top 100)
            continue
            
        # Create realistic ranking variations
        if current_rank <= 5:  # Top 5 players
            # Elite players usually stay in top 10, small variations
            rank_change = random.randint(-3, 7)  # Can drop more than rise
        elif current_rank <= 15:  # Top 15 players  
            # Good players can have bigger swings
            rank_change = random.randint(-8, 15)
        elif current_rank <= 30:  # Top 30 players
            # Mid-tier players have most volatility
            rank_change = random.randint(-15, 25)
        else:  # Everyone else
            # Lower ranked players can have huge swings
            rank_change = random.randint(-25, 40)
        
        # Calculate previous rank (what they were ranked last year)
        previous_rank = max(1, min(150, current_rank + rank_change))
        
        # Adjust previous stats slightly (simulate performance changes)
        stat_variation = random.uniform(0.85, 1.15)  # ±15% variation
        
        prev_per = per * stat_variation if per else None
        prev_ws = ws * stat_variation if ws else None
        prev_ws48 = ws48 * stat_variation if ws48 else None
        prev_bpm = bpm * stat_variation if bpm else None
        prev_vorp = vorp * stat_variation if vorp else None
        prev_games = max(20, int(games * random.uniform(0.8, 1.2))) if games else None
        prev_minutes = max(500, int(minutes * random.uniform(0.8, 1.2))) if minutes else None
        
        # Calculate previous HussEyq score based on rank
        prev_huss_score = previous_rank + random.uniform(-2, 2)
        
        mock_rankings.append({
            'player_id': player_id,
            'name': name,
            'previous_rank': previous_rank,
            'previous_score': prev_huss_score,
            'current_rank': current_rank,
            'rank_change': previous_rank - current_rank,  # Positive = improved
            'stats': {
                'per': prev_per, 'ws': prev_ws, 'ws48': prev_ws48,
                'bpm': prev_bpm, 'vorp': prev_vorp, 'games': prev_games, 'minutes': prev_minutes
            }
        })
    
    # Sort by previous rank for database insertion
    mock_rankings.sort(key=lambda x: x['previous_rank'])
    
    # Insert mock previous season data
    for i, player_data in enumerate(mock_rankings):
        player_id = player_data['player_id']
        prev_rank = player_data['previous_rank']
        prev_score = player_data['previous_score']
        stats = player_data['stats']
        
        # Insert previous season stats
        cursor.execute('''
            INSERT INTO player_snapshot_stats 
            (snapshot_id, player_id, team_id, g, mp, per, ws, ws48, bpm, vorp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            mock_snapshot_id, player_id, team_id, stats['games'], stats['minutes'],
            stats['per'], stats['ws'], stats['ws48'], stats['bpm'], stats['vorp']
        ))
        
        # Calculate mock individual stat ranks (simplified)
        per_rank = prev_rank + random.randint(-10, 10)
        ws_rank = prev_rank + random.randint(-10, 10) 
        ws48_rank = prev_rank + random.randint(-10, 10)
        bpm_rank = prev_rank + random.randint(-10, 10)
        vorp_rank = prev_rank + random.randint(-10, 10)
        
        # Insert previous season ranks
        cursor.execute('''
            INSERT INTO player_snapshot_ranks
            (snapshot_id, player_id, per_rank, ws_rank, ws48_rank, bpm_rank, vorp_rank,
             huss_score, huss_rank, qualified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            mock_snapshot_id, player_id, per_rank, ws_rank, ws48_rank,
            bpm_rank, vorp_rank, prev_score, prev_rank, True
        ))
    
    conn.commit()
    
    # Show interesting year-over-year changes
    print(f"\n=== Mock 2023-24 Season Created ===")
    print(f"Players with previous season data: {len(mock_rankings)}")
    
    # Show biggest improvers and decliners
    print(f"\n=== Biggest Improvers (2023-24 → 2024-25) ===")
    improvers = sorted([p for p in mock_rankings if p['rank_change'] > 0], 
                      key=lambda x: x['rank_change'], reverse=True)[:5]
    for player in improvers:
        print(f"{player['name']}: #{player['previous_rank']} → #{player['current_rank']} (+{player['rank_change']})")
    
    print(f"\n=== Biggest Decliners (2023-24 → 2024-25) ===")
    decliners = sorted([p for p in mock_rankings if p['rank_change'] < 0], 
                      key=lambda x: x['rank_change'])[:5]
    for player in decliners:
        print(f"{player['name']}: #{player['previous_rank']} → #{player['current_rank']} ({player['rank_change']})")
    
    conn.close()
    return mock_snapshot_id

if __name__ == "__main__":
    db_path = "../db/husseyquation.sqlite"
    create_mock_previous_season(db_path)