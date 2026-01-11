# MUD Analyzer Servers Status ✅

## Overview
The MUD Analyzer now has two complementary servers:
- **REST API** - For programmatic HTTP access
- **MCP Server** - For LLM integration via Model Context Protocol

---

## ✅ REST API Server

**Status**: ✅ **WORKING**

**How to Start**:
```bash
python launch_servers.py --rest
# OR run directly:
python mud_analyzer/api/rest_server.py
```

**What's Available**:
- **URL**: `http://127.0.0.1:8000`
- **Docs**: `http://127.0.0.1:8000/docs` (interactive OpenAPI docs)
- **ReDoc**: `http://127.0.0.1:8000/redoc` (alternative docs)

**API Endpoints**:
- `GET /api/zones` - List all zones
- `GET /api/zones/{zone_num}` - Get zone details
- `GET /api/objects/{vnum}` - Get object details
- `GET /api/mobiles/{vnum}` - Get mobile details
- `POST /api/search` - Search across MUD world
- `POST /api/assemblies/find` - Find item assemblies

**Test Command**:
```bash
curl http://127.0.0.1:8000/docs
```

---

## ⚠️ MCP Server

**Status**: ⚠️ **REQUIRES INSTALLATION** (gracefully disabled)

**Current State**:
- The MCP server code is complete and ready
- It requires the `mcp` package to run
- When the package is missing, the launcher detects this and continues with REST API

**How to Enable MCP**:
```bash
# Install the mcp package
pip install mcp

# Then start servers
python launch_servers.py --all
```

**What It Provides** (when installed):
- Model Context Protocol server for LLM integration
- Tools for LLM-based MUD world analysis:
  - Search objects and mobiles
  - Get zone information
  - Get detailed entity data
  - Find item assemblies
  - Explore zone resources

---

## 🚀 Server Launcher

**Usage**:
```bash
# Start both servers (REST always, MCP if available)
python launch_servers.py --all

# Start only REST API
python launch_servers.py --rest

# Start only MCP server
python launch_servers.py --mcp

# Check server health
python launch_servers.py --health

# Show help
python launch_servers.py --help
```

**Features**:
- ✅ Auto-restart on crash
- ✅ Graceful shutdown (Ctrl+C)
- ✅ Health monitoring
- ✅ Clear error messages
- ✅ Process ID tracking

---

## 📱 Client Library

The `mud_analyzer_client/` package provides:

**REST Client**:
```python
from mud_analyzer_client.rest_client import MudAnalyzerClient

client = MudAnalyzerClient("http://127.0.0.1:8000")

# Search for objects
results = client.search("sword", entity_type="object")

# Get zone info
zone = client.get_zone(30)

# Find assemblies
assemblies = client.find_assemblies(vnum=1234)
```

**MCP Client**:
```python
from mud_analyzer_client.mcp_client import MCPClient

client = MCPClient()
# Use with LLM providers (Claude, etc.)
```

---

## 🔧 Recent Fixes

1. **REST API** - Fixed sys.path issues, added proper uvicorn startup
2. **MCP Server** - Graceful handling of missing `mcp` package
3. **Pydantic v2** - Compatible with both v1 and v2
4. **Launcher** - Improved error messages and process management

---

## 🐛 Troubleshooting

**REST API won't start**:
```bash
# Check if port 8000 is in use
lsof -i :8000
# Kill if necessary
killall python
```

**Import errors**:
```bash
# Ensure you're in the right directory
cd /path/to/mud_analyzer

# Check Python path
python -c "import sys; print(sys.path)"
```

**MCP package missing**:
```bash
pip install mcp
# Then restart servers
```

---

## 📊 Architecture

```
mud_analyzer/
├── api/
│   ├── rest_server.py      ← REST API (FastAPI + Uvicorn)
│   └── mcp_server.py       ← MCP Server (Model Context Protocol)
├── mud_analyzer_api/
│   ├── core/              ← Business logic services
│   ├── models/            ← Data models
│   └── config.py          ← Configuration
├── launch_servers.py      ← Server launcher & manager
└── mud_analyzer_client/   ← Python client library
    ├── rest_client.py     ← REST API client
    ├── mcp_client.py      ← MCP client
    └── examples_*.py      ← Example usage
```

---

## ✨ What's Next

1. **Install MCP** (optional):
   ```bash
   pip install mcp
   ```

2. **Start servers**:
   ```bash
   python launch_servers.py --all
   ```

3. **Test REST API**:
   ```bash
   curl http://127.0.0.1:8000/docs
   ```

4. **Use the client library**:
   ```bash
   cd mud_analyzer_client
   python examples_rest_api.py
   ```

---

**Status Last Updated**: Just now ✅
