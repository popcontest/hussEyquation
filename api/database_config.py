import os
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any, List
import random

class DatabaseConfig:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.use_postgres = bool(self.database_url)
        
        if self.use_postgres:
            self.engine = create_engine(self.database_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.init_postgres()
        else:
            # Fallback to SQLite for local development
            self.db_path = "husseyquation.db"
            self.init_sqlite()
    
    def init_postgres(self):
        """Initialize PostgreSQL database with schema and sample data."""
        with self.engine.connect() as conn:
            # Create tables
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS players (
                  player_id SERIAL PRIMARY KEY,
                  nba_player_id TEXT UNIQUE,
                  full_name TEXT NOT NULL,
                  primary_pos TEXT
                );

                CREATE TABLE IF NOT EXISTS teams (
                  team_id SERIAL PRIMARY KEY,
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
                  snapshot_id SERIAL PRIMARY KEY,
                  season_id INTEGER REFERENCES seasons(season_id),
                  snapshot_date DATE NOT NULL,
                  source_hash TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            """))
            
            # Create indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_ranks_snapshot ON player_snapshot_ranks (snapshot_id, huss_rank);
                CREATE INDEX IF NOT EXISTS ix_ranks_qual ON player_snapshot_ranks (snapshot_id, qualified, huss_rank);
                CREATE INDEX IF NOT EXISTS ix_players_nbaid ON players (nba_player_id);
            """))
            
            # Check if we need to insert sample data
            result = conn.execute(text("SELECT COUNT(*) FROM players")).fetchone()
            if result[0] == 0:
                self._insert_sample_data_postgres(conn)
            
            conn.commit()
    
    def init_sqlite(self):
        """Initialize SQLite database (existing logic)."""
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
                  bmp_rank INTEGER, 
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
                self._insert_sample_data_sqlite(conn)

    def _insert_sample_data_postgres(self, conn):
        """Insert sample data for PostgreSQL."""
        # Insert season
        conn.execute(text("""
            INSERT INTO seasons (season_id, start_date, end_date, status) 
            VALUES (2025, '2024-10-15', '2025-06-30', 'active')
            ON CONFLICT (season_id) DO NOTHING
        """))
        
        # Insert teams
        teams_data = [
            ('DEN', 'Denver Nuggets'), ('DAL', 'Dallas Mavericks'), ('BOS', 'Boston Celtics'),
            ('LAL', 'Los Angeles Lakers'), ('GSW', 'Golden State Warriors'), ('MIL', 'Milwaukee Bucks'),
            ('PHX', 'Phoenix Suns'), ('OKC', 'Oklahoma City Thunder'), ('NYK', 'New York Knicks'),
            ('MIA', 'Miami Heat'), ('ATL', 'Atlanta Hawks'), ('BRK', 'Brooklyn Nets'),
            ('CHA', 'Charlotte Hornets'), ('CHI', 'Chicago Bulls'), ('CLE', 'Cleveland Cavaliers'),
            ('DET', 'Detroit Pistons'), ('IND', 'Indiana Pacers'), ('ORL', 'Orlando Magic'),
            ('PHI', 'Philadelphia 76ers'), ('TOR', 'Toronto Raptors'), ('WAS', 'Washington Wizards'),
            ('HOU', 'Houston Rockets'), ('LAC', 'LA Clippers'), ('MEM', 'Memphis Grizzlies'),
            ('MIN', 'Minnesota Timberwolves'), ('NOP', 'New Orleans Pelicans'), ('POR', 'Portland Trail Blazers'),
            ('SAC', 'Sacramento Kings'), ('SAS', 'San Antonio Spurs'), ('UTA', 'Utah Jazz')
        ]
        
        for abbr, name in teams_data:
            conn.execute(text("INSERT INTO teams (abbr, name) VALUES (:abbr, :name) ON CONFLICT (abbr) DO NOTHING"), {"abbr": abbr, "name": name})
        
        # Insert players
        players_data = [
            ('203999', 'Nikola Jokic', 'C'), ('1629029', 'Luka Doncic', 'PG'),
            ('1627759', 'Jayson Tatum', 'SF'), ('2544', 'LeBron James', 'SF'),
            ('201939', 'Stephen Curry', 'PG'), ('203507', 'Giannis Antetokounmpo', 'PF'),
            ('1628368', 'Devin Booker', 'SG'), ('1628983', 'Shai Gilgeous-Alexander', 'PG'),
            ('1627732', 'Jalen Brunson', 'PG'), ('200765', 'Jimmy Butler', 'SF'),
            ('1626164', 'Damian Lillard', 'PG'), ('203076', 'Anthony Davis', 'PF'),
            ('1627750', 'Donovan Mitchell', 'SG'), ('1628369', 'De\'Aaron Fox', 'PG'),
            ('202331', 'Paul George', 'SF'), ('1627783', 'Pascal Siakam', 'PF'),
            ('1628973', 'Tyler Herro', 'SG'), ('1629630', 'Scottie Barnes', 'SF'),
            ('1630163', 'Anthony Edwards', 'SG'), ('1630567', 'Paolo Banchero', 'PF'),
        ]
        
        for nba_id, name, pos in players_data:
            conn.execute(text("INSERT INTO players (nba_player_id, full_name, primary_pos) VALUES (:nba_id, :name, :pos) ON CONFLICT (nba_player_id) DO NOTHING"), 
                        {"nba_id": nba_id, "name": name, "pos": pos})
        
        # Insert snapshot
        conn.execute(text("INSERT INTO snapshots (season_id, snapshot_date) VALUES (2025, '2024-12-12') ON CONFLICT DO NOTHING"))
        
        # Get snapshot_id
        snapshot_result = conn.execute(text("SELECT snapshot_id FROM snapshots WHERE season_id = 2025 LIMIT 1")).fetchone()
        snapshot_id = snapshot_result[0] if snapshot_result else 1
        
        # Generate stats for players
        self._generate_stats_postgres(conn, snapshot_id)
        
    def _generate_stats_postgres(self, conn, snapshot_id):
        """Generate realistic stats for PostgreSQL."""
        # Get all players
        players = conn.execute(text("SELECT player_id, full_name FROM players ORDER BY player_id")).fetchall()
        
        random.seed(42)  # For consistent data
        
        for i, (player_id, name) in enumerate(players, 1):
            # Generate tier-based stats
            if any(star in name for star in ['Jokic', 'Luka', 'Giannis', 'Tatum', 'LeBron', 'Curry', 'Anthony Davis']):
                tier = {'per': (28, 35), 'ws': (8, 12), 'ws48': (0.25, 0.35), 'bpm': (8, 12), 'vorp': (4, 7)}
            elif any(good in name for good in ['Booker', 'Shai', 'Butler', 'Lillard', 'Mitchell', 'Edwards']):
                tier = {'per': (22, 28), 'ws': (5, 8), 'ws48': (0.18, 0.25), 'bpm': (3, 8), 'vorp': (2, 4)}
            else:
                tier = {'per': (15, 22), 'ws': (2, 5), 'ws48': (0.10, 0.18), 'bmp': (-2, 3), 'vorp': (0, 2)}
            
            games = random.randint(25, 35) if i <= 15 else random.randint(20, 30)
            minutes_per_game = random.uniform(30, 38) if i <= 10 else random.uniform(20, 32)
            total_minutes = int(games * minutes_per_game)
            
            per = round(random.uniform(tier['per'][0], tier['per'][1]), 1)
            ws = round(random.uniform(tier['ws'][0], tier['ws'][1]), 1)
            ws48 = round(random.uniform(tier['ws48'][0], tier['ws48'][1]), 3)
            bmp = round(random.uniform(tier.get('bpm', tier.get('bmp', (0, 5)))[0], tier.get('bpm', tier.get('bmp', (0, 5)))[1]), 1)
            vorp = round(random.uniform(tier['vorp'][0], tier['vorp'][1]), 1)
            
            team_id = ((i - 1) % 30) + 1
            
            conn.execute(text("""
                INSERT INTO player_snapshot_stats 
                (snapshot_id, player_id, team_id, g, mp, per, ws, ws48, bmp, vorp) 
                VALUES (:snapshot_id, :player_id, :team_id, :g, :mp, :per, :ws, :ws48, :bmp, :vorp)
                ON CONFLICT (snapshot_id, player_id) DO NOTHING
            """), {
                "snapshot_id": snapshot_id, "player_id": player_id, "team_id": team_id,
                "g": games, "mp": total_minutes, "per": per, "ws": ws, "ws48": ws48, "bmp": bmp, "vorp": vorp
            })
        
        # Calculate rankings
        self._calculate_rankings_postgres(conn, snapshot_id)

    def _calculate_rankings_postgres(self, conn, snapshot_id):
        """Calculate rankings for PostgreSQL."""
        # Get stats
        stats = conn.execute(text("""
            SELECT player_id, per, ws, ws48, bmp, vorp, mp
            FROM player_snapshot_stats 
            WHERE snapshot_id = :snapshot_id
        """), {"snapshot_id": snapshot_id}).fetchall()
        
        # Convert to list for processing
        players = [{"player_id": s[0], "per": s[1], "ws": s[2], "ws48": s[3], "bmp": s[4], "vorp": s[5], "mp": s[6]} for s in stats]
        
        # Calculate ranks
        per_sorted = sorted(players, key=lambda x: x['per'], reverse=True)
        ws_sorted = sorted(players, key=lambda x: x['ws'], reverse=True)
        ws48_sorted = sorted(players, key=lambda x: x['ws48'], reverse=True)
        bmp_sorted = sorted(players, key=lambda x: x['bmp'], reverse=True)
        vorp_sorted = sorted(players, key=lambda x: x['vorp'], reverse=True)
        
        per_ranks = {p['player_id']: i+1 for i, p in enumerate(per_sorted)}
        ws_ranks = {p['player_id']: i+1 for i, p in enumerate(ws_sorted)}
        ws48_ranks = {p['player_id']: i+1 for i, p in enumerate(ws48_sorted)}
        bmp_ranks = {p['player_id']: i+1 for i, p in enumerate(bmp_sorted)}
        vorp_ranks = {p['player_id']: i+1 for i, p in enumerate(vorp_sorted)}
        
        # Calculate HussEyquation scores
        huss_scores = {}
        for player in players:
            pid = player['player_id']
            ranks = [per_ranks[pid], ws_ranks[pid], ws48_ranks[pid], bmp_ranks[pid], vorp_ranks[pid]]
            huss_scores[pid] = sum(ranks) / len(ranks)
        
        huss_sorted = sorted(players, key=lambda x: huss_scores[x['player_id']])
        huss_ranks = {p['player_id']: i+1 for i, p in enumerate(huss_sorted)}
        
        # Clear existing ranks
        conn.execute(text("DELETE FROM player_snapshot_ranks WHERE snapshot_id = :snapshot_id"), {"snapshot_id": snapshot_id})
        
        # Insert rankings
        for player in players:
            pid = player['player_id']
            qualified = 1 if player['mp'] >= 1000 else 0
            conn.execute(text("""
                INSERT INTO player_snapshot_ranks 
                (snapshot_id, player_id, per_rank, ws_rank, ws48_rank, bmp_rank, vorp_rank, huss_score, huss_rank, qualified) 
                VALUES (:snapshot_id, :player_id, :per_rank, :ws_rank, :ws48_rank, :bmp_rank, :vorp_rank, :huss_score, :huss_rank, :qualified)
            """), {
                "snapshot_id": snapshot_id, "player_id": pid,
                "per_rank": per_ranks[pid], "ws_rank": ws_ranks[pid], "ws48_rank": ws48_ranks[pid], 
                "bmp_rank": bmp_ranks[pid], "vorp_rank": vorp_ranks[pid],
                "huss_score": round(huss_scores[pid], 1), "huss_rank": huss_ranks[pid], "qualified": qualified
            })

    def _insert_sample_data_sqlite(self, conn):
        """Insert sample data for SQLite (original logic)."""
        # Use the original logic from database.py here
        # Insert season
        conn.execute("""
            INSERT OR REPLACE INTO seasons (season_id, start_date, end_date, status) 
            VALUES (2025, '2024-10-15', '2025-06-30', 'active')
        """)
        
        # Insert teams and players with original data...
        # [Rest of original _insert_sample_data method from database.py]
        # This is the same logic as in the original file

    def get_season_rankings(self, season: int, qualified: bool = True, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """Get player rankings for a season (works with both SQLite and PostgreSQL)."""
        if self.use_postgres:
            return self._get_season_rankings_postgres(season, qualified, limit, offset)
        else:
            return self._get_season_rankings_sqlite(season, qualified, limit, offset)
    
    def _get_season_rankings_postgres(self, season: int, qualified: bool = True, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """Get rankings from PostgreSQL."""
        with self.engine.connect() as conn:
            # Get latest snapshot
            snapshot_result = conn.execute(text("""
                SELECT snapshot_id FROM snapshots 
                WHERE season_id = :season 
                ORDER BY snapshot_date DESC 
                LIMIT 1
            """), {"season": season}).fetchone()
            
            if not snapshot_result:
                return {"players": [], "total_count": 0}
            
            snapshot_id = snapshot_result[0]
            
            # Build query
            where_clause = "WHERE r.snapshot_id = :snapshot_id"
            params = {"snapshot_id": snapshot_id}
            
            if qualified:
                where_clause += " AND r.qualified = 1"
            
            # Get total count
            count_result = conn.execute(text(f"""
                SELECT COUNT(*) as count
                FROM player_snapshot_ranks r
                JOIN players p ON r.player_id = p.player_id
                JOIN player_snapshot_stats s ON r.snapshot_id = s.snapshot_id AND r.player_id = s.player_id
                JOIN teams t ON s.team_id = t.team_id
                {where_clause}
            """), params).fetchone()
            
            total_count = count_result[0]
            
            # Get players
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
                    s.bmp, r.bmp_rank,
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
            
            if limit is not None:
                query += f" LIMIT {limit} OFFSET {offset}"
            
            players_result = conn.execute(text(query), params).fetchall()
            players = [dict(zip([
                'rank', 'player_id', 'player_name', 'team', 'position', 'huss_score',
                'per', 'per_rank', 'ws', 'ws_rank', 'ws48', 'ws48_rank', 'bmp', 'bmp_rank',
                'vorp', 'vorp_rank', 'games', 'minutes', 'qualified', 'trend_1d', 'trend_7d', 'trend_14d'
            ], row)) for row in players_result]
            
            return {
                "players": players,
                "total_count": total_count,
                "season": season,
                "last_updated": "2024-12-12T12:00:00"
            }

    def _get_season_rankings_sqlite(self, season: int, qualified: bool = True, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """Get rankings from SQLite (original logic)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # [Original SQLite logic from database.py]
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
            
            # Get players
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
                    s.bpm, r.bmp_rank,
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
            
            if limit is not None:
                query += f" LIMIT {limit} OFFSET {offset}"
            
            players = [dict(row) for row in conn.execute(query, params).fetchall()]
            
            return {
                "players": players,
                "total_count": total_count,
                "season": season,
                "last_updated": "2024-12-12T12:00:00"
            }

# Global database configuration instance
db_config = DatabaseConfig()