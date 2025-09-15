from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Sample data for demonstration
SAMPLE_PLAYERS = [
    {"name": "Nikola Jokic", "team": "DEN", "position": "C", "gp": 76, "min": 34.6, "pts": 26.4, "reb": 12.4, "ast": 9.0, "score": 1.2, "rank": 1},
    {"name": "Luka Doncic", "team": "DAL", "position": "PG", "gp": 70, "min": 36.2, "pts": 32.4, "reb": 8.2, "ast": 8.0, "score": 1.8, "rank": 2},
    {"name": "Shai Gilgeous-Alexander", "team": "OKC", "position": "PG", "gp": 75, "min": 34.1, "pts": 30.1, "reb": 5.5, "ast": 6.2, "score": 2.1, "rank": 3},
    {"name": "Jayson Tatum", "team": "BOS", "position": "SF", "gp": 74, "min": 35.7, "pts": 26.9, "reb": 8.1, "ast": 4.9, "score": 2.3, "rank": 4},
    {"name": "Giannis Antetokounmpo", "team": "MIL", "position": "PF", "gp": 73, "min": 35.2, "pts": 30.4, "reb": 11.5, "ast": 6.5, "score": 2.4, "rank": 5}
]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        
        if path == '/health':
            response = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "husseyquation-api"
            }
        elif path.startswith('/api/seasons/') and path.endswith('/rankings'):
            # Extract season from path
            season = path.split('/')[-2]
            
            # Get query parameters
            limit = int(query_params.get('limit', [50])[0])
            offset = int(query_params.get('offset', [0])[0])
            qualified = query_params.get('qualified', ['true'])[0].lower() == 'true'
            
            # Apply pagination
            total_count = len(SAMPLE_PLAYERS)
            paginated_players = SAMPLE_PLAYERS[offset:offset + limit]
            
            response = {
                "players": paginated_players,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                },
                "season": season,
                "qualified_only": qualified,
                "last_updated": datetime.now().isoformat()
            }
        else:
            response = {"error": "Not found"}
            
        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()