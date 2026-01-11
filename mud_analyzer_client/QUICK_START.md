# Quick Start Guide

Get up and running with MUD Analyzer in 5 minutes.

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Start the Servers

```bash
cd ../mud_analyzer
python launch_servers.py --all
```

You should see:
```
🚀 Starting REST API server on 127.0.0.1:8000...
✅ REST API server started (PID: 12345)
   📍 OpenAPI Docs: http://127.0.0.1:8000/docs
   📍 API Root: http://127.0.0.1:8000/

🚀 Starting MCP server...
✅ MCP server started (PID: 12346)
   📍 Ready for LLM integration via stdio

Press Ctrl+C to stop all servers...
```

## 3. Run Examples

### Option A: REST API (Recommended for beginners)

```bash
cd ../mud_analyzer_client
python examples_rest_api.py
```

### Option B: MCP (For LLM integration)

```bash
python examples_mcp.py
```

## Quick Code Examples

### REST API

```python
from rest_client import MUDAnalyzerClient

# Search for items
with MUDAnalyzerClient() as client:
    results = client.search_objects("sword")
    for item in results:
        print(f"Found: {item.name} (VNUM {item.vnum})")
```

### MCP (LLM Integration)

```python
from mcp_client import LLMIntegration

# Get Claude-compatible tools
with LLMIntegration() as llm:
    tools = llm.get_tools_for_claude()
    # Use tools with Claude API
```

## Common Tasks

### Search for an item
```python
client = MUDAnalyzerClient()
results = client.search_objects("dragon", limit=5)
```

### Get zone information
```python
zones = client.get_zones(limit=10)
zone = client.get_zone(zones[0].zone_num)
```

### Get object details
```python
obj = client.get_object(vnum=3001)
print(obj['name'])
print(obj['short_description'])
```

### Find item assemblies
```python
assemblies = client.find_assemblies(obj_vnum=3001)
```

## Troubleshooting

**Q: Connection refused?**
A: Make sure servers are running: `python launch_servers.py --all`

**Q: How do I use custom port?**
A: 
```bash
# Start on custom port
python launch_servers.py --rest --port 8001

# Connect with client
client = MUDAnalyzerClient("http://localhost:8001")
```

**Q: Where's the API documentation?**
A: Visit http://localhost:8000/docs in your browser

## Next Steps

1. Read [README.md](README.md) for complete documentation
2. Run examples to see all features
3. Build your own integration
4. Check API docs at http://localhost:8000/docs

## API Cheat Sheet

```python
# Create client
client = MUDAnalyzerClient("http://localhost:8000")

# Health check
client.health() -> bool

# Zones
client.get_zones(limit=10)
client.get_zone(zone_num=30)

# Search
client.search("sword")
client.search_objects("sword")
client.search_mobiles("dragon")

# Get details
client.get_object(vnum=3001)
client.get_mobile(vnum=3005)

# Assemblies
client.find_assemblies(obj_vnum=3001)

# Docs
print(client.get_docs_url())
```

Happy adventuring! 🏰
