# Quick Start: Running MUD Analyzer Servers

## 🚀 Start REST API Server (Recommended First Step)

The REST API server is fully functional and requires no additional packages:

```bash
cd mud_analyzer
python launch_servers.py --rest
```

Expected output:
```
============================================================
🏰 MUD ANALYZER SERVER LAUNCHER
============================================================

🚀 Starting REST API server on 127.0.0.1:8000...
✅ REST API server started (PID: xxxx)
   📍 OpenAPI Docs: http://127.0.0.1:8000/docs
   📍 API Root: http://127.0.0.1:8000/

============================================================
📡 SERVERS RUNNING
============================================================

✅ REST API available at http://127.0.0.1:8000
   Try: curl http://127.0.0.1:8000/api/zones

Press Ctrl+C to stop all servers...
```

## 🌐 Access the API

1. **Interactive API Docs** (OpenAPI/Swagger):
   - Open browser: `http://127.0.0.1:8000/docs`
   - Try endpoints interactively
   - See request/response examples

2. **Alternative Docs** (ReDoc):
   - Open browser: `http://127.0.0.1:8000/redoc`
   - Read-only documentation view

3. **Using curl**:
   ```bash
   # Get all zones
   curl http://127.0.0.1:8000/api/zones
   
   # Get specific zone
   curl http://127.0.0.1:8000/api/zones/30
   
   # Search for items
   curl -X POST http://127.0.0.1:8000/api/search \
     -H "Content-Type: application/json" \
     -d '{"query":"sword","limit":10}'
   ```

## 🐍 Use Python Client

The project includes a ready-to-use Python client:

```bash
cd mud_analyzer_client
pip install -r requirements.txt
python examples_rest_api.py
```

Example code:
```python
from mud_analyzer_client.rest_client import MudAnalyzerClient

client = MudAnalyzerClient("http://127.0.0.1:8000")

# Search for objects
swords = client.search("sword", entity_type="object", limit=5)
print(f"Found {len(swords)} swords")

# Get zone details
zone = client.get_zone(30)
print(f"Zone: {zone['name']}")

# Find assemblies
assemblies = client.find_assemblies(vnum=1234)
print(f"Item used in {len(assemblies)} assemblies")
```

## 🧠 Enable MCP Server (Optional, for LLM Integration)

The MCP server enables integration with LLMs (Claude, etc):

1. **Install MCP package**:
   ```bash
   pip install mcp
   ```

2. **Start both servers**:
   ```bash
   python launch_servers.py --all
   ```

3. **Use with LLM**:
   ```python
   from mud_analyzer_client.mcp_client import MCPClient
   
   client = MCPClient()
   # Connect to your LLM provider
   ```

## 🔍 Available API Endpoints

### Zones
- `GET /api/zones` - List all zones
- `GET /api/zones/{zone_num}` - Get zone details

### Objects
- `GET /api/objects/{vnum}` - Get object details
- `GET /api/objects` - List objects

### Mobiles
- `GET /api/mobiles/{vnum}` - Get mobile details
- `GET /api/mobiles` - List mobiles

### Search
- `POST /api/search` - Search across world
- Parameters: `query`, `entity_type`, `limit`

### Assemblies
- `POST /api/assemblies/find` - Find item assemblies
- Parameters: `obj_vnum`, `limit`

## 📊 Health Check

```bash
python launch_servers.py --health
```

## 🛑 Stop Servers

Press `Ctrl+C` in the terminal running the servers.

Or:
```bash
killall python  # Force kill all Python processes
```

## 🐛 Troubleshooting

**Port already in use**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

**Import errors**:
```bash
# Make sure you're in the right directory
cd /path/to/mud_analyzer

# Test imports
python -c "from mud_analyzer_api.config import Config; print('OK')"
```

**MCP package missing**:
```bash
pip install mcp
```

---

## 📚 Next Steps

1. Start REST API: `python launch_servers.py --rest`
2. Open docs: http://127.0.0.1:8000/docs
3. Try the client: `python mud_analyzer_client/examples_rest_api.py`
4. (Optional) Install MCP for LLM integration

**Questions?** Check [SERVERS_STATUS.md](SERVERS_STATUS.md) for more details.
