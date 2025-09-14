#!/usr/bin/env python3
"""
Calculate proper rankings for each stat category and HussEyquation composite scores
"""

import sqlite3
import pandas as pd
from datetime import datetime

def calculate_rankings():
    """Calculate rankings for all advanced stats and HussEyquation composite score"""
    
    db_path = "../db/husseyquation.sqlite"
    
    with sqlite3.connect(db_path) as conn:
        # Get all player stats from the latest snapshot
        query = """
            SELECT 
                pss.player_id,
                p.full_name,
                t.abbr as team,
                pss.per,
                pss.ws,
                pss.ws48,
                pss.bpm,
                pss.vorp,
                pss.mp,
                pss.g
            FROM player_snapshot_stats pss
            JOIN players p ON pss.player_id = p.player_id
            LEFT JOIN teams t ON pss.team_id = t.team_id
            WHERE pss.snapshot_id = (SELECT MAX(snapshot_id) FROM snapshots)
            AND pss.per IS NOT NULL
            ORDER BY pss.player_id
        """
        
        df = pd.read_sql_query(query, conn)
        print(f"Loaded {len(df)} players with stats")
        
        # Handle null values by replacing with worst possible values
        # This ensures players with missing stats rank last in those categories
        df['per'] = df['per'].fillna(0)
        df['ws'] = df['ws'].fillna(-10)  # Win Shares can be negative
        df['ws48'] = df['ws48'].fillna(0)
        df['bpm'] = df['bpm'].fillna(-20)  # BPM can be very negative
        df['vorp'] = df['vorp'].fillna(-10)  # VORP can be negative
        
        print(f"Sample data:")
        print(df[['full_name', 'per', 'ws', 'ws48', 'bpm', 'vorp']].head())
        
        # Calculate rankings for each stat (1 = best)
        print("\nCalculating rankings...")
        
        # PER: Higher is better
        df['per_rank'] = df['per'].rank(method='dense', ascending=False).astype(int)
        
        # Win Shares: Higher is better  
        df['ws_rank'] = df['ws'].rank(method='dense', ascending=False).astype(int)
        
        # WS/48: Higher is better
        df['ws48_rank'] = df['ws48'].rank(method='dense', ascending=False).astype(int)
        
        # BPM: Higher is better (positive is good, negative is bad)
        df['bpm_rank'] = df['bpm'].rank(method='dense', ascending=False).astype(int)
        
        # VORP: Higher is better (positive is good, negative is bad)
        df['vorp_rank'] = df['vorp'].rank(method='dense', ascending=False).astype(int)
        
        print("Rankings calculated!")
        
        # Calculate HussEyquation score (average of the 5 rankings)
        df['huss_score'] = (df['per_rank'] + df['ws_rank'] + df['ws48_rank'] + 
                           df['bpm_rank'] + df['vorp_rank']) / 5.0
        
        # Rank by HussEyquation score (lower score = better rank)
        df['huss_rank'] = df['huss_score'].rank(method='dense', ascending=True).astype(int)
        
        print(f"\nTop 10 HussEyquation Rankings:")
        top_players = df.nsmallest(10, 'huss_score')[
            ['huss_rank', 'full_name', 'team', 'huss_score', 'per_rank', 'ws_rank', 'ws48_rank', 'bpm_rank', 'vorp_rank']
        ]
        print(top_players.to_string(index=False))
        
        # Update database with calculated rankings
        print(f"\nUpdating database with rankings...")
        
        cursor = conn.cursor()
        
        # Get the latest snapshot ID
        cursor.execute("SELECT MAX(snapshot_id) FROM snapshots")
        snapshot_id = cursor.fetchone()[0]
        
        # Clear existing rankings for this snapshot
        cursor.execute("DELETE FROM player_snapshot_ranks WHERE snapshot_id = ?", (snapshot_id,))
        
        # Insert new rankings
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO player_snapshot_ranks 
                (snapshot_id, player_id, per_rank, ws_rank, ws48_rank, bpm_rank, vorp_rank, 
                 huss_score, huss_rank, qualified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id,
                row['player_id'],
                row['per_rank'],
                row['ws_rank'], 
                row['ws48_rank'],
                row['bpm_rank'],
                row['vorp_rank'],
                round(row['huss_score'], 3),
                row['huss_rank'],
                1  # All players qualified
            ))
        
        conn.commit()
        print(f"Rankings updated for {len(df)} players")
        
        # Copy updated database to API directory
        print("Copying database to API directory...")
        import shutil
        shutil.copy(db_path, "../api/husseyquation.db")
        print("Database copied to API")
        
        return df

if __name__ == "__main__":
    df = calculate_rankings()
    print(f"\nHussEyquation rankings calculated successfully!")
    print(f"Total players ranked: {len(df)}")