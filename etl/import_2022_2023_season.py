#!/usr/bin/env python3
"""
Import actual 2022-23 NBA HussEyquation CSV data
"""

import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
import re

def clear_existing_2023_data(conn):
    """Clear existing 2023 data if any"""
    cursor = conn.cursor()
    
    # Find snapshot IDs for season 2023
    cursor.execute('SELECT snapshot_id FROM snapshots WHERE season_id = 2023')
    snapshot_ids = [row[0] for row in cursor.fetchall()]
    
    if snapshot_ids:
        print(f"Clearing existing 2023 season data (snapshots: {snapshot_ids})")
        
        # Delete in correct order due to foreign keys
        for snapshot_id in snapshot_ids:
            cursor.execute('DELETE FROM player_snapshot_ranks WHERE snapshot_id = ?', (snapshot_id,))
            cursor.execute('DELETE FROM player_snapshot_stats WHERE snapshot_id = ?', (snapshot_id,))
        
        cursor.execute('DELETE FROM snapshots WHERE season_id = 2023')
        
        conn.commit()
        print("Cleared existing 2023 season data")

def import_2022_2023_season(csv_path, db_path):
    """Import actual 2022-23 season data"""
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from 2022-23 CSV")
    
    # Drop rows where Player is NaN (empty rows)
    df = df.dropna(subset=['Player'])
    print(f"After removing empty rows: {len(df)} players")
    
    # Clean up the data
    df = df.fillna('')  # Replace NaN with empty strings
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    
    # Clear existing data
    clear_existing_2023_data(conn)
    
    # Insert season data for 2022-23
    season_id = 2023  # 2022-23 season
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO seasons (season_id, start_date, end_date, status)
        VALUES (?, ?, ?, ?)
    ''', (season_id, '2022-10-01', '2023-04-15', 'completed'))
    
    # Create snapshot for this import
    snapshot_date = '2023-04-15'  # End of 2022-23 season
    cursor.execute('''
        INSERT INTO snapshots (season_id, snapshot_date, source_hash)
        VALUES (?, ?, ?)
    ''', (season_id, snapshot_date, 'actual_2022_23_csv'))
    snapshot_id = cursor.lastrowid
    
    print(f"Created snapshot {snapshot_id} for 2022-23 season")
    
    # Process each player
    for idx, row in df.iterrows():
        try:
            player_name = row['Player'].strip()
            if not player_name or player_name == 'Player':
                continue
            
            team = row['Tm'].strip() if row['Tm'] else 'UNK'
            position = row['Pos'].strip() if row['Pos'] else ''
            
            # Create a simple player ID based on name
            player_id_str = re.sub(r'[^a-zA-Z0-9]', '', player_name.lower())[:10]
            
            # Insert or get player
            cursor.execute('''
                INSERT OR IGNORE INTO players (nba_player_id, full_name, primary_pos)
                VALUES (?, ?, ?)
            ''', (player_id_str, player_name, position))
            
            # Get player_id
            cursor.execute('SELECT player_id FROM players WHERE full_name = ?', (player_name,))
            player_result = cursor.fetchone()
            if not player_result:
                # Insert if not found
                cursor.execute('''
                    INSERT INTO players (nba_player_id, full_name, primary_pos)
                    VALUES (?, ?, ?)
                ''', (f"2022_{idx}", player_name, position))
                player_id = cursor.lastrowid
            else:
                player_id = player_result[0]
            
            # Insert team
            cursor.execute('INSERT OR IGNORE INTO teams (abbr) VALUES (?)', (team,))
            
            # Get team_id
            cursor.execute('SELECT team_id FROM teams WHERE abbr = ?', (team,))
            team_result = cursor.fetchone()
            team_id = team_result[0] if team_result else None
            
            # Extract stats with proper handling of empty/invalid values
            def safe_float(value):
                if pd.isna(value) or value == '' or value == '-':
                    return None
                try:
                    return float(value)
                except:
                    return None
            
            def safe_int(value):
                if pd.isna(value) or value == '' or value == '-':
                    return None
                try:
                    return int(float(value))
                except:
                    return None
            
            games = safe_int(row['G'])
            minutes = safe_int(row['MP'])
            per_stat = safe_float(row['PER'])
            ws_stat = safe_float(row['WS'])
            ws48_stat = safe_float(row['WS/48'])
            bmp_stat = safe_float(row['BPM'])
            vorp_stat = safe_float(row['VORP'])
            
            # Insert stats
            cursor.execute('''
                INSERT OR REPLACE INTO player_snapshot_stats 
                (snapshot_id, player_id, team_id, g, mp, per, ws, ws48, bpm, vorp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot_id, player_id, team_id, games, minutes,
                per_stat, ws_stat, ws48_stat, bmp_stat, vorp_stat
            ))
            
            # Extract rankings
            per_rank = safe_int(row['PER Rank'])
            ws_rank = safe_int(row['WS Rank'])
            ws48_rank = safe_int(row['WS 48'])  # Note: column name is 'WS 48' not 'WS/48 Rank'
            bmp_rank = safe_int(row['BPM Rank'])
            vorp_rank = safe_int(row['VORP Rank'])
            
            # HussEyquation score and rank
            huss_score = safe_float(row['AVG Rank'])  # This is the HussEyquation score
            huss_rank = safe_int(row['Rk'])  # This is the overall rank
            
            # All players are qualified in this dataset
            qualified = True
            
            cursor.execute('''
                INSERT OR REPLACE INTO player_snapshot_ranks
                (snapshot_id, player_id, per_rank, ws_rank, ws48_rank, bpm_rank, vorp_rank,
                 huss_score, huss_rank, qualified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot_id, player_id, per_rank, ws_rank, ws48_rank,
                bmp_rank, vorp_rank, huss_score, huss_rank, qualified
            ))
            
        except Exception as e:
            print(f"Error processing player {idx}: {e}")
            continue
    
    conn.commit()
    
    # Print summary
    cursor.execute('SELECT COUNT(*) FROM player_snapshot_stats WHERE snapshot_id = ?', (snapshot_id,))
    stats_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM player_snapshot_ranks WHERE snapshot_id = ?', (snapshot_id,))
    ranks_count = cursor.fetchone()[0]
    
    print(f"Import complete:")
    print(f"  Stats records: {stats_count}")
    print(f"  Ranking records: {ranks_count}")
    print(f"  Snapshot ID: {snapshot_id}")
    
    # Show top 5 players for 2022-23
    cursor.execute('''
        SELECT p.full_name, t.abbr, r.huss_rank, r.huss_score, s.per, s.ws, s.bpm, s.vorp
        FROM player_snapshot_ranks r
        JOIN players p ON r.player_id = p.player_id
        JOIN player_snapshot_stats s ON r.snapshot_id = s.snapshot_id AND r.player_id = s.player_id
        LEFT JOIN teams t ON s.team_id = t.team_id
        WHERE r.snapshot_id = ?
        ORDER BY r.huss_rank
        LIMIT 5
    ''', (snapshot_id,))
    
    print(f"\nTop 5 HussEyquation Rankings (2022-23 Actual):")
    print("Rank | Player | Team | HussEyq | PER | WS | BPM | VORP")
    print("-" * 60)
    for row in cursor.fetchall():
        name, team, rank, score, per, ws, bpm, vorp = row
        team = team or '???'
        print(f"{rank:4d} | {name:<20} | {team:3s} | {score:7.1f} | {per:4.1f} | {ws:4.1f} | {bpm:5.1f} | {vorp:4.1f}")
    
    # Update normalized names for new players
    from normalize_player_names import normalize_name
    cursor.execute('SELECT player_id, full_name FROM players WHERE normalized_name IS NULL')
    new_players = cursor.fetchall()
    
    if new_players:
        print(f"\nUpdating normalized names for {len(new_players)} new players...")
        for player_id, full_name in new_players:
            normalized = normalize_name(full_name)
            cursor.execute(
                'UPDATE players SET normalized_name = ? WHERE player_id = ?',
                (normalized, player_id)
            )
        conn.commit()
    
    conn.close()
    return snapshot_id

if __name__ == "__main__":
    csv_path = "Z:/Downloads/NBA hussEyquation - 2024-2025 - 22-23 - FINAL.csv"
    db_path = "../db/husseyquation.sqlite"
    import_2022_2023_season(csv_path, db_path)