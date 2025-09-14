#!/usr/bin/env python3
"""
Import 2024-2025 NBA HussEyquation CSV data and enable year-over-year comparisons
"""

import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
import re

def create_tables(conn):
    """Create the necessary database tables"""
    cursor = conn.cursor()
    
    # Create tables - keeping existing structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nba_player_id TEXT UNIQUE,
            full_name TEXT NOT NULL,
            primary_pos TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            abbr TEXT UNIQUE NOT NULL,
            name TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seasons (
            season_id INTEGER PRIMARY KEY,
            start_date DATE,
            end_date DATE,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snapshots (
            snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id INTEGER REFERENCES seasons(season_id),
            snapshot_date DATE NOT NULL,
            source_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_snapshot_stats (
            snapshot_id INTEGER REFERENCES snapshots(snapshot_id),
            player_id INTEGER REFERENCES players(player_id),
            team_id INTEGER REFERENCES teams(team_id),
            g INTEGER,
            mp INTEGER,
            per REAL,
            ws REAL,
            ws48 REAL,
            bpm REAL,
            vorp REAL,
            PRIMARY KEY (snapshot_id, player_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_snapshot_ranks (
            snapshot_id INTEGER REFERENCES snapshots(snapshot_id),
            player_id INTEGER REFERENCES players(player_id),
            per_rank INTEGER,
            ws_rank INTEGER,
            ws48_rank INTEGER,
            bpm_rank INTEGER,
            vorp_rank INTEGER,
            huss_score REAL,
            huss_rank INTEGER,
            qualified BOOLEAN DEFAULT 1,
            PRIMARY KEY (snapshot_id, player_id)
        )
    ''')
    
    # Add year-over-year comparison view
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS year_over_year_comparison AS
        SELECT 
            current.player_id,
            p.full_name as player_name,
            current.huss_rank as current_rank,
            current.huss_score as current_score,
            previous.huss_rank as previous_rank,
            previous.huss_score as previous_score,
            (previous.huss_rank - current.huss_rank) as rank_change,
            (previous.huss_score - current.huss_score) as score_change
        FROM player_snapshot_ranks current
        JOIN players p ON current.player_id = p.player_id
        LEFT JOIN player_snapshot_ranks previous ON 
            current.player_id = previous.player_id 
            AND previous.snapshot_id = (
                SELECT snapshot_id FROM snapshots 
                WHERE season_id = 2024 
                ORDER BY snapshot_date DESC 
                LIMIT 1
            )
        WHERE current.snapshot_id = (
            SELECT snapshot_id FROM snapshots 
            WHERE season_id = 2025 
            ORDER BY snapshot_date DESC 
            LIMIT 1
        )
    ''')
    
    conn.commit()

def import_2024_2025_season(csv_path, db_path):
    """Import 2024-2025 season data"""
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from CSV")
    
    # Drop rows where Player is NaN (empty rows)
    df = df.dropna(subset=['Player'])
    print(f"After removing empty rows: {len(df)} players")
    
    # Clean up the data
    df = df.fillna('')  # Replace NaN with empty strings
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    
    # Create tables
    create_tables(conn)
    
    # Insert season data for 2024-25
    season_id = 2025  # 2024-25 season
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO seasons (season_id, start_date, end_date, status)
        VALUES (?, ?, ?, ?)
    ''', (season_id, '2024-10-01', '2025-04-15', 'active'))
    
    # Create snapshot for this import
    snapshot_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        INSERT INTO snapshots (season_id, snapshot_date, source_hash)
        VALUES (?, ?, ?)
    ''', (season_id, snapshot_date, '2024_2025_csv_import'))
    snapshot_id = cursor.lastrowid
    
    print(f"Created snapshot {snapshot_id} for 2024-25 season")
    
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
            
            # Insert player
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
                ''', (f"generated_{idx}", player_name, position))
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
            bpm_stat = safe_float(row['BPM'])
            vorp_stat = safe_float(row['VORP'])
            
            # Insert stats
            cursor.execute('''
                INSERT OR REPLACE INTO player_snapshot_stats 
                (snapshot_id, player_id, team_id, g, mp, per, ws, ws48, bpm, vorp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot_id, player_id, team_id, games, minutes,
                per_stat, ws_stat, ws48_stat, bpm_stat, vorp_stat
            ))
            
            # Extract rankings
            per_rank = safe_int(row['PER Rank'])
            ws_rank = safe_int(row['WS Rank'])
            ws48_rank = safe_int(row['WS 48'])  # Note: column name is 'WS 48' not 'WS/48 Rank'
            bpm_rank = safe_int(row['BPM Rank'])
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
                bpm_rank, vorp_rank, huss_score, huss_rank, qualified
            ))
            
        except Exception as e:
            print(f"Error processing player {idx}: {e}")
            continue
    
    conn.commit()
    
    # Print summary
    cursor.execute('SELECT COUNT(*) FROM players')
    player_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM player_snapshot_stats WHERE snapshot_id = ?', (snapshot_id,))
    stats_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM player_snapshot_ranks WHERE snapshot_id = ?', (snapshot_id,))
    ranks_count = cursor.fetchone()[0]
    
    print(f"Import complete:")
    print(f"  Total players: {player_count}")
    print(f"  Stats records: {stats_count}")
    print(f"  Ranking records: {ranks_count}")
    print(f"  Snapshot ID: {snapshot_id}")
    
    # Show top 5 players for 2024-25
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
    
    print(f"\nTop 5 HussEyquation Rankings (2024-25):")
    print("Rank | Player | Team | HussEyq | PER | WS | BPM | VORP")
    print("-" * 60)
    for row in cursor.fetchall():
        name, team, rank, score, per, ws, bpm, vorp = row
        team = team or '???'
        print(f"{rank:4d} | {name:<20} | {team:3s} | {score:7.1f} | {per:4.1f} | {ws:4.1f} | {bpm:5.1f} | {vorp:4.1f}")
    
    # Show year-over-year comparison for top 10
    print(f"\nYear-over-Year Comparison (Top 10 Current):")
    print("Player | Current Rank | Previous Rank | Change")
    print("-" * 50)
    cursor.execute('''
        SELECT player_name, current_rank, previous_rank, rank_change
        FROM year_over_year_comparison 
        ORDER BY current_rank 
        LIMIT 10
    ''')
    for row in cursor.fetchall():
        name, current, previous, change = row
        change_str = f"+{change}" if change > 0 else str(change) if change else "NEW"
        previous_str = str(previous) if previous else "N/A"
        print(f"{name:<20} | {current:11d} | {previous_str:12s} | {change_str}")
    
    conn.close()
    return snapshot_id

if __name__ == "__main__":
    csv_path = "Z:/Downloads/NBA hussEyquation - 2024-2025 - 2024-2025 (1).csv"
    db_path = "../db/husseyquation.sqlite"
    import_2024_2025_season(csv_path, db_path)