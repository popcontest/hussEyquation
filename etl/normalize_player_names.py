#!/usr/bin/env python3
"""
Normalize player names to handle accent/diacritic variations
"""

import sqlite3
import unicodedata
import re

def normalize_name(name):
    """
    Normalize a player name by:
    1. Converting to lowercase
    2. Removing accents/diacritics (ş -> s, ğ -> g, etc.)
    3. Removing non-alphanumeric characters except spaces
    4. Removing extra whitespace
    """
    if not name:
        return ""
    
    # Convert to lowercase
    normalized = name.lower()
    
    # Remove accents/diacritics using Unicode normalization
    normalized = unicodedata.normalize('NFD', normalized)
    normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    
    # Remove non-alphanumeric characters except spaces
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
    
    # Remove extra whitespace and strip
    normalized = ' '.join(normalized.split())
    
    return normalized

def update_normalized_names(db_path):
    """Update all players with normalized names"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # First, add the normalized_name column if it doesn't exist
    try:
        cursor.execute('ALTER TABLE players ADD COLUMN normalized_name TEXT')
        print("Added normalized_name column to players table")
    except sqlite3.OperationalError:
        print("normalized_name column already exists")
    
    # Get all players
    cursor.execute('SELECT player_id, full_name FROM players')
    players = cursor.fetchall()
    
    print(f"Updating normalized names for {len(players)} players...")
    
    for player_id, full_name in players:
        normalized = normalize_name(full_name)
        cursor.execute(
            'UPDATE players SET normalized_name = ? WHERE player_id = ?',
            (normalized, player_id)
        )
    
    conn.commit()
    
    # Count normalized name differences
    cursor.execute('''
        SELECT COUNT(*) 
        FROM players 
        WHERE full_name != normalized_name
    ''')
    diff_count = cursor.fetchone()[0]
    print(f"\n{diff_count} players had names that needed normalization")
    
    # Check for the specific Alperen case
    cursor.execute('''
        SELECT COUNT(*) 
        FROM players 
        WHERE full_name LIKE '%Alperen%' OR normalized_name LIKE '%alperen%'
    ''')
    alperen_count = cursor.fetchone()[0]
    if alperen_count > 0:
        print(f"Found {alperen_count} Alperen name variations")
    
    conn.close()
    return len(players)

if __name__ == "__main__":
    db_path = "../db/husseyquation.sqlite"
    count = update_normalized_names(db_path)
    print(f"\nNormalized names updated for {count} players")