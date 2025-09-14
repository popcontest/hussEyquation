import sqlite3
import random

def create_expanded_database():
    """Create database with 50+ players and realistic stats."""
    
    # Remove existing database
    try:
        import os
        os.remove("husseyquation.db")
        print("Removed existing database")
    except:
        pass
    
    conn = sqlite3.connect("husseyquation.db")
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Create tables
    conn.executescript("""
        CREATE TABLE players (
          player_id INTEGER PRIMARY KEY AUTOINCREMENT,
          nba_player_id TEXT UNIQUE,
          full_name TEXT NOT NULL,
          primary_pos TEXT
        );

        CREATE TABLE teams (
          team_id INTEGER PRIMARY KEY AUTOINCREMENT,
          abbr TEXT UNIQUE NOT NULL,
          name TEXT
        );

        CREATE TABLE seasons (
          season_id INTEGER PRIMARY KEY,
          start_date DATE,
          end_date DATE,
          status TEXT DEFAULT 'historical'
        );

        CREATE TABLE snapshots (
          snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
          season_id INTEGER REFERENCES seasons(season_id),
          snapshot_date DATE NOT NULL,
          source_hash TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE player_snapshot_stats (
          snapshot_id INTEGER REFERENCES snapshots(snapshot_id),
          player_id INTEGER REFERENCES players(player_id),
          team_id INTEGER REFERENCES teams(team_id),
          g INTEGER, 
          mp INTEGER,
          per REAL,
          ws REAL,
          ws48 REAL,
          bmp REAL,
          vorp REAL,
          PRIMARY KEY (snapshot_id, player_id)
        );

        CREATE TABLE player_snapshot_ranks (
          snapshot_id INTEGER REFERENCES snapshots(snapshot_id),
          player_id INTEGER REFERENCES players(player_id),
          per_rank INTEGER, 
          ws_rank INTEGER, 
          ws48_rank INTEGER, 
          bmp_rank INTEGER, 
          vorp_rank INTEGER,
          huss_score REAL,
          huss_rank INTEGER,
          qualified INTEGER DEFAULT 1,
          PRIMARY KEY (snapshot_id, player_id)
        );
    """)
    
    # Insert season
    conn.execute("INSERT INTO seasons (season_id, start_date, end_date, status) VALUES (2025, '2024-10-15', '2025-06-30', 'active')")
    
    # Insert 30 teams
    teams = [
        ('ATL', 'Atlanta Hawks'), ('BOS', 'Boston Celtics'), ('BRK', 'Brooklyn Nets'), 
        ('CHA', 'Charlotte Hornets'), ('CHI', 'Chicago Bulls'), ('CLE', 'Cleveland Cavaliers'),
        ('DAL', 'Dallas Mavericks'), ('DEN', 'Denver Nuggets'), ('DET', 'Detroit Pistons'),
        ('GSW', 'Golden State Warriors'), ('HOU', 'Houston Rockets'), ('IND', 'Indiana Pacers'),
        ('LAC', 'LA Clippers'), ('LAL', 'Los Angeles Lakers'), ('MEM', 'Memphis Grizzlies'),
        ('MIA', 'Miami Heat'), ('MIL', 'Milwaukee Bucks'), ('MIN', 'Minnesota Timberwolves'),
        ('NOP', 'New Orleans Pelicans'), ('NYK', 'New York Knicks'), ('OKC', 'Oklahoma City Thunder'),
        ('ORL', 'Orlando Magic'), ('PHI', 'Philadelphia 76ers'), ('PHX', 'Phoenix Suns'),
        ('POR', 'Portland Trail Blazers'), ('SAC', 'Sacramento Kings'), ('SAS', 'San Antonio Spurs'),
        ('TOR', 'Toronto Raptors'), ('UTA', 'Utah Jazz'), ('WAS', 'Washington Wizards')
    ]
    
    conn.executemany("INSERT INTO teams (abbr, name) VALUES (?, ?)", teams)
    
    # Generate unique player data - 60 players
    players = []
    player_names = [
        'Nikola Jokic', 'Luka Doncic', 'Jayson Tatum', 'LeBron James', 'Stephen Curry',
        'Giannis Antetokounmpo', 'Devin Booker', 'Shai Gilgeous-Alexander', 'Jalen Brunson', 'Jimmy Butler',
        'Damian Lillard', 'Anthony Davis', 'Donovan Mitchell', 'De\'Aaron Fox', 'Paul George',
        'Pascal Siakam', 'Anthony Edwards', 'Paolo Banchero', 'Rudy Gobert', 'Domantas Sabonis',
        'CJ McCollum', 'Mikal Bridges', 'Cade Cunningham', 'Alperen Sengun', 'Evan Mobley',
        'Scottie Barnes', 'Kawhi Leonard', 'Brandon Ingram', 'Julius Randle', 'Jaren Jackson Jr.',
        'Franz Wagner', 'Jalen Green', 'Josh Giddey', 'Anfernee Simons', 'Khris Middleton',
        'Michael Porter Jr.', 'Chet Holmgren', 'Keegan Murray', 'Bennedict Mathurin', 'Jalen Williams',
        'Walker Kessler', 'Marcus Smart', 'Gary Trent Jr.', 'Wendell Carter Jr.', 'Nic Claxton',
        'Aaron Gordon', 'Tyler Herro', 'Jalen Suggs', 'Jabari Smith Jr.', 'Isaiah Mobley',
        'Clint Capela', 'Tobias Harris', 'Kristaps Porzingis', 'Jaylen Brown', 'Kevin Durant',
        'Russell Westbrook', 'Joel Embiid', 'Zion Williamson', 'Ja Morant', 'RJ Barrett'
    ]
    
    positions = ['PG', 'SG', 'SF', 'PF', 'C']
    
    for i, name in enumerate(player_names):
        nba_id = str(1000000 + i)  # Generate unique IDs
        pos = positions[i % len(positions)]  # Cycle through positions
        players.append((nba_id, name, pos))
    
    conn.executemany("INSERT INTO players (nba_player_id, full_name, primary_pos) VALUES (?, ?, ?)", players)
    print(f"Inserted {len(players)} players")
    
    # Insert snapshot
    conn.execute("INSERT INTO snapshots (season_id, snapshot_date) VALUES (2025, '2024-12-12')")
    
    # Generate realistic stats for all players
    random.seed(42)  # For consistent results
    
    stats_data = []
    for i in range(1, len(players) + 1):
        # Determine tier - first 10 are superstars, next 15 are stars, etc.
        if i <= 10:
            per_range = (28, 35)
            ws_range = (8, 15)
            ws48_range = (0.25, 0.35)
            bmp_range = (8, 12)
            vorp_range = (4, 8)
            min_range = (32, 38)
        elif i <= 25:
            per_range = (22, 28)
            ws_range = (5, 8)
            ws48_range = (0.18, 0.25)
            bmp_range = (3, 8)
            vorp_range = (2, 4)
            min_range = (28, 35)
        elif i <= 45:
            per_range = (16, 22)
            ws_range = (2, 5)
            ws48_range = (0.12, 0.18)
            bmp_range = (-1, 3)
            vorp_range = (0, 2)
            min_range = (22, 30)
        else:
            per_range = (12, 16)
            ws_range = (0, 2)
            ws48_range = (0.08, 0.12)
            bmp_range = (-3, 1)
            vorp_range = (-1, 1)
            min_range = (15, 25)
        
        games = random.randint(28, 35) if i <= 50 else random.randint(20, 32)
        minutes_per_game = random.uniform(min_range[0], min_range[1])
        total_minutes = int(games * minutes_per_game)
        
        per = round(random.uniform(per_range[0], per_range[1]), 1)
        ws = round(random.uniform(ws_range[0], ws_range[1]), 1) 
        ws48 = round(random.uniform(ws48_range[0], ws48_range[1]), 3)
        bmp = round(random.uniform(bmp_range[0], bmp_range[1]), 1)
        vorp = round(random.uniform(vorp_range[0], vorp_range[1]), 1)
        
        team_id = ((i - 1) % 30) + 1  # Distribute across 30 teams
        
        stats_data.append((1, i, team_id, games, total_minutes, per, ws, ws48, bmp, vorp))
    
    conn.executemany("""
        INSERT INTO player_snapshot_stats (snapshot_id, player_id, team_id, g, mp, per, ws, ws48, bmp, vorp) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, stats_data)
    
    # Calculate rankings
    calculate_rankings(conn, 1)
    
    conn.close()
    print(f"Created database with {len(players)} players")

def calculate_rankings(conn, snapshot_id):
    """Calculate proper rankings from stats data."""
    # Get all stats
    stats = conn.execute("""
        SELECT player_id, per, ws, ws48, bmp, vorp, mp
        FROM player_snapshot_stats 
        WHERE snapshot_id = ?
    """, (snapshot_id,)).fetchall()
    
    players = []
    for row in stats:
        players.append({
            'player_id': row[0], 'per': row[1], 'ws': row[2], 
            'ws48': row[3], 'bmp': row[4], 'vorp': row[5], 'mp': row[6]
        })
    
    # Sort and rank each metric (higher is better, so reverse=True)
    per_sorted = sorted(players, key=lambda x: x['per'], reverse=True)
    ws_sorted = sorted(players, key=lambda x: x['ws'], reverse=True)
    ws48_sorted = sorted(players, key=lambda x: x['ws48'], reverse=True)
    bmp_sorted = sorted(players, key=lambda x: x['bmp'], reverse=True)
    vorp_sorted = sorted(players, key=lambda x: x['vorp'], reverse=True)
    
    # Create rank mappings
    per_ranks = {p['player_id']: i+1 for i, p in enumerate(per_sorted)}
    ws_ranks = {p['player_id']: i+1 for i, p in enumerate(ws_sorted)}
    ws48_ranks = {p['player_id']: i+1 for i, p in enumerate(ws48_sorted)}
    bmp_ranks = {p['player_id']: i+1 for i, p in enumerate(bmp_sorted)}
    vorp_ranks = {p['player_id']: i+1 for i, p in enumerate(vorp_sorted)}
    
    # Calculate HussEyquation scores
    huss_scores = {}
    for p in players:
        pid = p['player_id']
        ranks = [per_ranks[pid], ws_ranks[pid], ws48_ranks[pid], bmp_ranks[pid], vorp_ranks[pid]]
        huss_scores[pid] = sum(ranks) / len(ranks)
    
    # Sort by HussEyquation (lower is better)
    huss_sorted = sorted(players, key=lambda x: huss_scores[x['player_id']])
    huss_ranks = {p['player_id']: i+1 for i, p in enumerate(huss_sorted)}
    
    # Insert rankings
    ranks_data = []
    for p in players:
        pid = p['player_id']
        qualified = 1 if p['mp'] >= 1000 else 0
        ranks_data.append((
            snapshot_id, pid, per_ranks[pid], ws_ranks[pid], ws48_ranks[pid], 
            bmp_ranks[pid], vorp_ranks[pid], round(huss_scores[pid], 1), huss_ranks[pid], qualified
        ))
    
    conn.executemany("""
        INSERT INTO player_snapshot_ranks 
        (snapshot_id, player_id, per_rank, ws_rank, ws48_rank, bmp_rank, vorp_rank, huss_score, huss_rank, qualified) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ranks_data)

if __name__ == "__main__":
    create_expanded_database()