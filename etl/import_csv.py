#!/usr/bin/env python3
"""
Import Basketball Reference CSV data into HussEyquation database
"""

import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
import re

def create_tables(conn):
    """Create the necessary database tables"""
    cursor = conn.cursor()
    
    # Create tables
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
    
    conn.commit()

def extract_player_id(href):
    """Extract player ID from Basketball Reference URL"""
    if not href or pd.isna(href):
        return None
    match = re.search(r'/players/[a-z]/([^.]+)\.html', href)
    return match.group(1) if match else None

def map_csv_columns(df):
    """Map the CSV columns to meaningful names based on Basketball Reference structure"""
    # Based on the sample data, this appears to be a Basketball Reference advanced stats table
    column_mapping = {
        'right': 'rank',           # 1 (ranking)
        'left': 'player_name',     # Mikal Bridges
        'left href': 'player_url', # URL
        'right 2': 'age',          # 28
        'left 2': 'team',          # NYK  
        'left href 2': 'team_url', # Team URL
        'center': 'pos',           # SF (position)
        'right 3': 'g',            # 82 (games)
        'right 4': 'gs',           # 82 (games started)
        'right 5': 'mp',           # 3036 (minutes played)
        'right 6': 'per',          # 14.0 (PER)
        'right 7': 'ts_pct',       # 0.585 (True Shooting %)
        'right 8': 'threep_ar',    # 0.391 (3P Attempt Rate)
        'right 9': 'ftr',          # 0.100 (Free Throw Rate)
        'right 10': 'orb_pct',     # 2.7 (ORB%)
        'right 11': 'drb_pct',     # 7.0 (DRB%)
        'right 12': 'trb_pct',     # 4.9 (TRB%)
        'right 13': 'ast_pct',     # 14.4 (AST%)
        'right 14': 'stl_pct',     # 1.2 (STL%)
        'right 15': 'blk_pct',     # 1.3 (BLK%)
        'right 16': 'tov_pct',     # 9.7 (TOV%)
        'right 17': 'usg_pct',     # 19.6 (USG%)
        'right 18': 'ows',         # 3.7 (Offensive Win Shares)
        'right 19': 'dws',         # 2.0 (Defensive Win Shares)  
        'right 20': 'ws',          # 5.7 (Win Shares)
        'right 21': 'ws48',        # 0.090 (WS/48)
        'right 22': 'obpm',        # 0.4 (Offensive BPM)
        'right 23': 'dbpm',        # -0.9 (Defensive BPM)
        'right 24': 'bpm',         # -0.5 (BPM)
        'right 25': 'vorp',        # 1.2 (VORP)
        'right 26': 'g_qual',      # Games for qualification
        'right 27': 'mp_qual',     # Minutes for qualification
    }
    
    return df.rename(columns=column_mapping)

def import_csv_data(csv_path, db_path):
    """Import CSV data into the database"""
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from CSV")
    
    # Map columns to meaningful names
    df = map_csv_columns(df)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    
    # Create tables
    create_tables(conn)
    
    # Insert season data
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
    ''', (season_id, snapshot_date, 'basketball_reference_csv'))
    snapshot_id = cursor.lastrowid
    
    # Process each player
    for idx, row in df.iterrows():
        if pd.isna(row['player_name']) or row['player_name'] == 'Player':
            continue
            
        # Extract player ID from URL
        player_id_str = extract_player_id(row['player_url'])
        
        # Insert player
        cursor.execute('''
            INSERT OR IGNORE INTO players (nba_player_id, full_name, primary_pos)
            VALUES (?, ?, ?)
        ''', (player_id_str, row['player_name'], row['pos']))
        
        # Get player_id
        cursor.execute('SELECT player_id FROM players WHERE nba_player_id = ? OR full_name = ?', (player_id_str, row['player_name']))
        player_result = cursor.fetchone()
        if not player_result:
            # Insert with a generated ID if lookup fails
            cursor.execute('''
                INSERT INTO players (nba_player_id, full_name, primary_pos)
                VALUES (?, ?, ?)
            ''', (f"generated_{idx}", row['player_name'], row['pos']))
            player_id = cursor.lastrowid
        else:
            player_id = player_result[0]
        
        # Insert team
        cursor.execute('INSERT OR IGNORE INTO teams (abbr) VALUES (?)', (row['team'],))
        
        # Get team_id
        cursor.execute('SELECT team_id FROM teams WHERE abbr = ?', (row['team'],))
        team_result = cursor.fetchone()
        team_id = team_result[0] if team_result else None
        
        # Convert minutes from total to integer
        mp = int(row['mp']) if pd.notna(row['mp']) else 0
        g = int(row['g']) if pd.notna(row['g']) else 0
        
        # Insert stats
        cursor.execute('''
            INSERT OR REPLACE INTO player_snapshot_stats 
            (snapshot_id, player_id, team_id, g, mp, per, ws, ws48, bpm, vorp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            snapshot_id, player_id, team_id, g, mp,
            row['per'] if pd.notna(row['per']) else None,
            row['ws'] if pd.notna(row['ws']) else None,
            row['ws48'] if pd.notna(row['ws48']) else None,
            row['bpm'] if pd.notna(row['bpm']) else None,
            row['vorp'] if pd.notna(row['vorp']) else None
        ))
        
        # Calculate ranks and HussEyquation score
        # For now, use the rank from the CSV (which might be overall rank)
        huss_rank = int(row['rank']) if pd.notna(row['rank']) else None
        qualified = True  # All players are qualified
        
        cursor.execute('''
            INSERT OR REPLACE INTO player_snapshot_ranks
            (snapshot_id, player_id, huss_rank, qualified)
            VALUES (?, ?, ?, ?)
        ''', (snapshot_id, player_id, huss_rank, qualified))
    
    conn.commit()
    
    # Print summary
    cursor.execute('SELECT COUNT(*) FROM players')
    player_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM player_snapshot_stats WHERE snapshot_id = ?', (snapshot_id,))
    stats_count = cursor.fetchone()[0]
    
    print(f"Import complete:")
    print(f"  Total players: {player_count}")
    print(f"  Stats records: {stats_count}")
    print(f"  Snapshot ID: {snapshot_id}")
    
    conn.close()

if __name__ == "__main__":
    csv_path = "Z:/Downloads/basketball-reference.csv"
    db_path = "../db/husseyquation.sqlite"
    import_csv_data(csv_path, db_path)