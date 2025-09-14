#!/usr/bin/env python3
"""
Initialize database for production deployment
"""

import os
import sqlite3
from pathlib import Path
import shutil

def init_production_database():
    """Initialize production database with existing data"""
    
    # Database paths
    source_db = "../db/husseyquation.sqlite"
    production_db = "./husseyquation.sqlite"  # In the API directory for deployment
    
    print(f"Setting up production database...")
    print(f"Source: {source_db}")
    print(f"Target: {production_db}")
    
    # Check if source database exists
    if not os.path.exists(source_db):
        print(f"Source database not found at {source_db}")
        return False
    
    # Copy the database to the API directory
    try:
        shutil.copy2(source_db, production_db)
        print(f"Database copied successfully")
        
        # Verify the copy worked
        with sqlite3.connect(production_db) as conn:
            cursor = conn.cursor()
            
            # Check seasons
            cursor.execute('SELECT season_id, COUNT(*) FROM snapshots GROUP BY season_id')
            seasons = cursor.fetchall()
            
            print(f"Database contains data for {len(seasons)} seasons:")
            for season_id, count in seasons:
                cursor.execute('''
                    SELECT COUNT(*) FROM player_snapshot_ranks r 
                    JOIN snapshots s ON r.snapshot_id = s.snapshot_id 
                    WHERE s.season_id = ?
                ''', (season_id,))
                player_count = cursor.fetchone()[0]
                print(f"  Season {season_id}: {player_count} players")
        
        print(f"Production database ready at {production_db}")
        return True
        
    except Exception as e:
        print(f"Error copying database: {e}")
        return False

if __name__ == "__main__":
    success = init_production_database()
    exit(0 if success else 1)