# HussEyquation.com

A comprehensive NBA player ranking website using the "HussEyquation" – a composite metric that averages each player's ranking across five advanced statistics: **PER**, **Win Shares (WS)**, **Win Shares per 48 minutes (WS/48)**, **Box Plus/Minus (BPM)**, and **Value Over Replacement Player (VORP)**.

## Architecture

This is a monorepo with the following components:

```
hussEyquation/
├── etl/          # Python ETL pipeline (nba_api → PostgreSQL)
├── api/          # FastAPI backend
├── web/          # Next.js frontend
├── db/           # Database schema and migrations
└── docker-compose.yml
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL (via Docker)

### 1. Environment Setup

```bash
# Copy environment variables
cp .env.example .env

# Edit .env with your settings
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/husseyquation
ACTIVE_SEASON=2025
TZ=America/New_York
```

### 2. Start Database

```bash
# Start PostgreSQL with schema
docker-compose up -d postgres

# Wait for database to be ready
docker-compose logs -f postgres
```

### 3. ETL Pipeline

```bash
cd etl

# Install Python dependencies
pip install -r requirements.txt

# Test data pulling (optional)
python pull.py

# Run full pipeline for current season
python run_daily.py

# Backfill historical seasons (optional)
python backfill.py
```

### 4. API Server

```bash
cd api

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
python main.py
# Server runs on http://localhost:8000
```

### 5. Frontend

```bash
cd web

# Install dependencies
npm install

# Start development server
npm run dev
# Frontend runs on http://localhost:3000
```

## The HussEyquation Formula

The HussEyquation takes each player's **rank** in five advanced metrics and averages them:

**Example**: If a player ranks 1st in PER, 3rd in WS, 5th in WS/48, 2nd in BPM, and 4th in VORP:
- HussEyquation Score = (1 + 3 + 5 + 2 + 4) ÷ 5 = **3.0**

Players are then sorted by their HussEyquation score (lower is better), creating a consensus ranking that rewards consistent excellence across multiple advanced metrics.

### Advanced Metrics Used

1. **PER (Player Efficiency Rating)**: John Hollinger's per-minute metric, pace-adjusted
2. **WS (Win Shares)**: Basketball-Reference's wins contributed estimate  
3. **WS/48**: Win Shares per 48 minutes
4. **BPM (Box Plus/Minus)**: Box score-based plus/minus per 100 possessions
5. **VORP (Value Over Replacement Player)**: BPM scaled to wins above replacement

### Qualification

- Default: 1000+ minutes played
- Stricter qualification rules available for rate stats

## API Endpoints

### Current Season Rankings
```
GET /api/seasons/{season}/rankings?qualified=true&limit=100&offset=0
```

### Trending Players  
```
GET /api/seasons/{season}/trending?window=7d
```

### Player Profile
```
GET /api/players/{player_id}
```

### Player History
```
GET /api/players/{player_id}/history
```

### All-Time Leaderboards
```
GET /api/leaderboards/all-time
```

## Data Sources & Methodology

- **Data Source**: NBA.com via [nba_api](https://github.com/swar/nba_api)
- **Advanced Metrics**: Computed in-house following published methodologies
- **Update Schedule**: Daily at 12:05 PM ET during NBA season
- **BPM Note**: Our BPM 2.0 implementation is approximate per Basketball-Reference guidance

### Key References

- [PER Methodology (Basketball-Reference)](https://www.basketball-reference.com/about/per.html)
- [Win Shares Methodology](https://www.basketball-reference.com/about/ws.html)  
- [BPM 2.0 + VORP Overview](https://www.sports-reference.com/blog/2020/02/introducing-bpm-2-0/)
- [Rate Stat Qualification Guidelines](https://www.basketball-reference.com/about/rate_stat_req.html)

## Development

### ETL Pipeline

The ETL runs in phases:

1. **Pull**: Get game IDs → fetch box scores → aggregate season totals
2. **Compute**: Calculate PER, Win Shares, BPM, VORP from box score stats  
3. **Rank**: Dense rank each metric → average ranks → final HussEyquation rank
4. **Store**: Upsert to PostgreSQL with trend calculations

### Database Schema

- `players`: NBA player master data
- `seasons`: Season definitions (2016-2025+)  
- `snapshots`: Daily ranking captures
- `player_snapshot_stats`: Raw advanced metrics per snapshot
- `player_snapshot_ranks`: Rankings and HussEyquation scores per snapshot
- `season_final_ranks`: End-of-season final standings

### Frontend Features

- **Desktop**: Wide table with sortable columns
- **Mobile**: Collapsible card view with tap-to-expand
- **Real-time**: Server-side rendering with caching
- **Responsive**: Tailwind CSS for all screen sizes

## Deployment

### Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ACTIVE_SEASON=2025                    # Current season end year
TZ=America/New_York                   # Timezone for scheduling
```

### Scheduling

For production deployment, run the ETL daily:

```bash
# Example cron entry (12:05 PM ET daily)
5 17 * * * cd /path/to/hussEyquation/etl && python run_daily.py
```

### Docker Support

```bash
# Run full stack
docker-compose up -d

# Run individual services
docker-compose up -d postgres
docker-compose up -d api
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test ETL pipeline with sample data
4. Ensure API endpoints return correct data structure  
5. Test frontend responsive design on mobile/desktop
6. Submit pull request

## License

MIT License - see [LICENSE](LICENSE) for details

## Acknowledgments

- **NBA.com** for providing game data via undocumented APIs
- **swar/nba_api** for Python client library
- **Basketball-Reference** for advanced metrics methodology
- **Sports-Reference** for BPM/VORP formulas