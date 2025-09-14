import sqlite3
import os
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self, db_path: str = "husseyquation.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database with schema and sample data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Create tables
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS players (
                  player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nba_player_id TEXT UNIQUE,
                  full_name TEXT NOT NULL,
                  primary_pos TEXT
                );

                CREATE TABLE IF NOT EXISTS teams (
                  team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  abbr TEXT UNIQUE NOT NULL,
                  name TEXT
                );

                CREATE TABLE IF NOT EXISTS seasons (
                  season_id INTEGER PRIMARY KEY,
                  start_date DATE,
                  end_date DATE,
                  status TEXT DEFAULT 'historical'
                );

                CREATE TABLE IF NOT EXISTS snapshots (
                  snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  season_id INTEGER REFERENCES seasons(season_id),
                  snapshot_date DATE NOT NULL,
                  source_hash TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

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
                );

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
                  qualified INTEGER DEFAULT 1,
                  PRIMARY KEY (snapshot_id, player_id)
                );

                CREATE INDEX IF NOT EXISTS ix_ranks_snapshot ON player_snapshot_ranks (snapshot_id, huss_rank);
                CREATE INDEX IF NOT EXISTS ix_ranks_qual ON player_snapshot_ranks (snapshot_id, qualified, huss_rank);
                CREATE INDEX IF NOT EXISTS ix_players_nbaid ON players (nba_player_id);
            """)
            
            # Insert sample data if tables are empty
            count = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
            if count == 0:
                self._insert_sample_data(conn)
    
    def _insert_sample_data(self, conn):
        """Insert sample data for testing."""
        # Insert season
        conn.execute("""
            INSERT OR REPLACE INTO seasons (season_id, start_date, end_date, status) 
            VALUES (2025, '2024-10-15', '2025-06-30', 'active')
        """)
        
        # Insert all 30 NBA teams
        teams_data = [
            ('DEN', 'Denver Nuggets'),
            ('DAL', 'Dallas Mavericks'),
            ('BOS', 'Boston Celtics'),
            ('LAL', 'Los Angeles Lakers'),
            ('GSW', 'Golden State Warriors'),
            ('MIL', 'Milwaukee Bucks'),
            ('PHX', 'Phoenix Suns'),
            ('OKC', 'Oklahoma City Thunder'),
            ('NYK', 'New York Knicks'),
            ('MIA', 'Miami Heat'),
            ('ATL', 'Atlanta Hawks'),
            ('BRK', 'Brooklyn Nets'),
            ('CHA', 'Charlotte Hornets'),
            ('CHI', 'Chicago Bulls'),
            ('CLE', 'Cleveland Cavaliers'),
            ('DET', 'Detroit Pistons'),
            ('IND', 'Indiana Pacers'),
            ('ORL', 'Orlando Magic'),
            ('PHI', 'Philadelphia 76ers'),
            ('TOR', 'Toronto Raptors'),
            ('WAS', 'Washington Wizards'),
            ('HOU', 'Houston Rockets'),
            ('LAC', 'LA Clippers'),
            ('MEM', 'Memphis Grizzlies'),
            ('MIN', 'Minnesota Timberwolves'),
            ('NOP', 'New Orleans Pelicans'),
            ('POR', 'Portland Trail Blazers'),
            ('SAC', 'Sacramento Kings'),
            ('SAS', 'San Antonio Spurs'),
            ('UTA', 'Utah Jazz')
        ]
        
        conn.executemany("INSERT OR REPLACE INTO teams (abbr, name) VALUES (?, ?)", teams_data)
        
        # Insert players - expanded to ~50 players for realistic testing
        players_data = [
            ('203999', 'Nikola Jokic', 'C'),
            ('1629029', 'Luka Doncic', 'PG'),
            ('1627759', 'Jayson Tatum', 'SF'),
            ('2544', 'LeBron James', 'SF'),
            ('201939', 'Stephen Curry', 'PG'),
            ('203507', 'Giannis Antetokounmpo', 'PF'),
            ('1628368', 'Devin Booker', 'SG'),
            ('1628983', 'Shai Gilgeous-Alexander', 'PG'),
            ('1627732', 'Jalen Brunson', 'PG'),
            ('200765', 'Jimmy Butler', 'SF'),
            ('1626164', 'Damian Lillard', 'PG'),
            ('203076', 'Anthony Davis', 'PF'),
            ('1627750', 'Donovan Mitchell', 'SG'),
            ('1628369', 'De\'Aaron Fox', 'PG'),
            ('202331', 'Paul George', 'SF'),
            ('1627783', 'Pascal Siakam', 'PF'),
            ('1628973', 'Tyler Herro', 'SG'),
            ('1629630', 'Scottie Barnes', 'SF'),
            ('1630163', 'Anthony Edwards', 'SG'),
            ('1630567', 'Paolo Banchero', 'PF'),
            ('203994', 'Rudy Gobert', 'C'),
            ('203935', 'Marcus Smart', 'PG'),
            ('1627734', 'Domantas Sabonis', 'PF'),
            ('203924', 'CJ McCollum', 'SG'),
            ('1628420', 'Mikal Bridges', 'SF'),
            ('1629027', 'Tyler Herro', 'SG'),
            ('1629651', 'Cade Cunningham', 'PG'),
            ('1630169', 'Alperen Sengun', 'C'),
            ('1630178', 'Evan Mobley', 'PF'),
            ('1630173', 'Scottie Barnes', 'SF'),
            ('203497', 'Kawhi Leonard', 'SF'),
            ('201933', 'Blake Griffin', 'PF'),
            ('1627742', 'Brandon Ingram', 'SF'),
            ('202710', 'Julius Randle', 'PF'),
            ('1628960', 'Jaren Jackson Jr.', 'PF'),
            ('1629636', 'Franz Wagner', 'SF'),
            ('1630532', 'Jalen Green', 'SG'),
            ('1630224', 'Josh Giddey', 'PG'),
            ('1629029', 'Luka Doncic', 'PG'),
            ('1628386', 'Anfernee Simons', 'SG'),
            ('1628378', 'Gary Trent Jr.', 'SG'),
            ('203114', 'Khris Middleton', 'SF'),
            ('1628389', 'Wendell Carter Jr.', 'C'),
            ('1628969', 'Michael Porter Jr.', 'SF'),
            ('1629052', 'Nic Claxton', 'C'),
            ('1630591', 'Chet Holmgren', 'C'),
            ('1630550', 'Keegan Murray', 'PF'),
            ('1630596', 'Bennedict Mathurin', 'SF'),
            ('1630558', 'Jalen Williams', 'SF'),
            ('1630602', 'Walker Kessler', 'C')
        ]
        
        conn.executemany("INSERT OR REPLACE INTO players (nba_player_id, full_name, primary_pos) VALUES (?, ?, ?)", players_data)
        
        # Insert snapshot
        conn.execute("""
            INSERT OR REPLACE INTO snapshots (season_id, snapshot_date) 
            VALUES (2025, '2024-12-12')
        """)
        
        # Generate realistic stats for all players
        import random
        random.seed(42)  # For consistent data
        
        stats_data = []
        team_id = 1
        
        # Define stat ranges for different tiers of players
        elite_stats = {'per': (28, 35), 'ws': (8, 12), 'ws48': (0.25, 0.35), 'bmp': (8, 12), 'vorp': (4, 7)}
        good_stats = {'per': (22, 28), 'ws': (5, 8), 'ws48': (0.18, 0.25), 'bmp': (3, 8), 'vorp': (2, 4)}
        average_stats = {'per': (15, 22), 'ws': (2, 5), 'ws48': (0.10, 0.18), 'bmp': (-2, 3), 'vorp': (0, 2)}
        bench_stats = {'per': (10, 15), 'ws': (0, 2), 'ws48': (0.05, 0.10), 'bmp': (-5, -2), 'vorp': (-1, 0)}
        
        for i, (nba_id, name, pos) in enumerate(players_data, 1):
            # Determine player tier based on name/reputation
            if any(star in name for star in ['Jokic', 'Luka', 'Giannis', 'Tatum', 'LeBron', 'Curry', 'Anthony Davis']):
                tier = elite_stats
            elif any(good in name for good in ['Booker', 'SGA', 'Butler', 'Lillard', 'Mitchell', 'Edwards']):
                tier = good_stats
            elif i <= 30:  # Top 30 players get average+ stats
                tier = average_stats
            else:  # Bench/role players
                tier = bench_stats
            
            # Generate games and minutes
            games = random.randint(25, 35) if i <= 40 else random.randint(15, 30)
            minutes_per_game = random.uniform(25, 38) if i <= 20 else random.uniform(15, 30) if i <= 40 else random.uniform(8, 20)
            total_minutes = int(games * minutes_per_game)
            
            # Generate stats within tier ranges
            per = round(random.uniform(tier['per'][0], tier['per'][1]), 1)
            ws = round(random.uniform(tier['ws'][0], tier['ws'][1]), 1)
            ws48 = round(random.uniform(tier['ws48'][0], tier['ws48'][1]), 3)
            bmp = round(random.uniform(tier['bmp'][0], tier['bmp'][1]), 1)
            vorp = round(random.uniform(tier['vorp'][0], tier['vorp'][1]), 1)
            
            stats_data.append((1, i, team_id, games, total_minutes, per, ws, ws48, bmp, vorp))
            
            # Cycle through teams (now 30 teams)
            team_id = (team_id % 30) + 1
        
        conn.executemany("""
            INSERT OR REPLACE INTO player_snapshot_stats 
            (snapshot_id, player_id, team_id, g, mp, per, ws, ws48, bmp, vorp) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, stats_data)
        
        # Calculate and insert proper rankings
        self._calculate_rankings(conn, 1)
    
    def _calculate_rankings(self, conn, snapshot_id):
        """Calculate proper rankings from stats data."""
        # Get all stats for the snapshot
        stats = conn.execute("""
            SELECT player_id, per, ws, ws48, bmp, vorp, mp
            FROM player_snapshot_stats 
            WHERE snapshot_id = ?
        """, (snapshot_id,)).fetchall()
        
        # Convert to list of dicts for easier processing
        players = []
        for row in stats:
            players.append({
                'player_id': row[0],
                'per': row[1],
                'ws': row[2], 
                'ws48': row[3],
                'bmp': row[4],
                'vorp': row[5],
                'mp': row[6]
            })
        
        # Sort by each metric (descending = higher is better)
        per_sorted = sorted(players, key=lambda x: x['per'], reverse=True)
        ws_sorted = sorted(players, key=lambda x: x['ws'], reverse=True)
        ws48_sorted = sorted(players, key=lambda x: x['ws48'], reverse=True)
        bmp_sorted = sorted(players, key=lambda x: x['bmp'], reverse=True)
        vorp_sorted = sorted(players, key=lambda x: x['vorp'], reverse=True)
        
        # Create ranking dictionaries
        per_ranks = {player['player_id']: i+1 for i, player in enumerate(per_sorted)}
        ws_ranks = {player['player_id']: i+1 for i, player in enumerate(ws_sorted)}
        ws48_ranks = {player['player_id']: i+1 for i, player in enumerate(ws48_sorted)}
        bmp_ranks = {player['player_id']: i+1 for i, player in enumerate(bmp_sorted)}
        vorp_ranks = {player['player_id']: i+1 for i, player in enumerate(vorp_sorted)}
        
        # Calculate HussEyquation scores and rankings
        huss_scores = {}
        for player in players:
            pid = player['player_id']
            ranks = [per_ranks[pid], ws_ranks[pid], ws48_ranks[pid], bmp_ranks[pid], vorp_ranks[pid]]
            huss_scores[pid] = sum(ranks) / len(ranks)
        
        # Sort by HussEyquation score (ascending = lower is better)
        huss_sorted = sorted(players, key=lambda x: huss_scores[x['player_id']])
        huss_ranks = {player['player_id']: i+1 for i, player in enumerate(huss_sorted)}
        
        # Insert rankings data
        ranks_data = []
        for player in players:
            pid = player['player_id']
            qualified = 1 if player['mp'] >= 1000 else 0
            ranks_data.append((
                snapshot_id, pid,
                per_ranks[pid], ws_ranks[pid], ws48_ranks[pid], bmp_ranks[pid], vorp_ranks[pid],
                round(huss_scores[pid], 1), huss_ranks[pid], qualified
            ))
        
        # Clear existing ranks for this snapshot
        conn.execute("DELETE FROM player_snapshot_ranks WHERE snapshot_id = ?", (snapshot_id,))
        
        # Insert new rankings
        conn.executemany("""
            INSERT INTO player_snapshot_ranks 
            (snapshot_id, player_id, per_rank, ws_rank, ws48_rank, bmp_rank, vorp_rank, huss_score, huss_rank, qualified) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ranks_data)
    
    def get_season_rankings(self, season: int, qualified: bool = True, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """Get player rankings for a season."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get latest snapshot for the season
            snapshot = conn.execute("""
                SELECT snapshot_id FROM snapshots 
                WHERE season_id = ? 
                ORDER BY snapshot_date DESC 
                LIMIT 1
            """, (season,)).fetchone()
            
            if not snapshot:
                return {"players": [], "total_count": 0}
            
            snapshot_id = snapshot["snapshot_id"]
            
            # Build query
            where_clause = "WHERE r.snapshot_id = ?"
            params = [snapshot_id]
            
            if qualified:
                where_clause += " AND r.qualified = 1"
            
            # Get total count
            count_query = f"""
                SELECT COUNT(*) as count
                FROM player_snapshot_ranks r
                JOIN players p ON r.player_id = p.player_id
                JOIN player_snapshot_stats s ON r.snapshot_id = s.snapshot_id AND r.player_id = s.player_id
                JOIN teams t ON s.team_id = t.team_id
                {where_clause}
            """
            
            total_count = conn.execute(count_query, params).fetchone()["count"]
            
            # Get players - show ALL if no limit specified
            query = f"""
                SELECT 
                    r.huss_rank as rank,
                    p.player_id,
                    p.full_name as player_name,
                    t.abbr as team,
                    p.primary_pos as position,
                    r.huss_score,
                    s.per, r.per_rank,
                    s.ws, r.ws_rank,
                    s.ws48, r.ws48_rank,
                    s.bpm, r.bpm_rank,
                    s.vorp, r.vorp_rank,
                    s.g as games,
                    s.mp as minutes,
                    r.qualified,
                    0 as trend_1d,
                    0 as trend_7d,
                    0 as trend_14d
                FROM player_snapshot_ranks r
                JOIN players p ON r.player_id = p.player_id
                JOIN player_snapshot_stats s ON r.snapshot_id = s.snapshot_id AND r.player_id = s.player_id
                JOIN teams t ON s.team_id = t.team_id
                {where_clause}
                ORDER BY r.huss_rank
            """
            
            # Only add LIMIT/OFFSET if limit is specified
            if limit is not None:
                query += f" LIMIT {limit} OFFSET {offset}"
                params_final = params
            else:
                params_final = params
            
            players = [dict(row) for row in conn.execute(query, params_final).fetchall()]
            
            return {
                "players": players,
                "total_count": total_count,
                "season": season,
                "last_updated": "2024-12-12T12:00:00"
            }

# Global database instance
db = Database()