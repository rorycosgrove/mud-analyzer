# Server Launch & Client Project Summary

## Overview

Created a complete infrastructure for launching API servers and a full-featured client library for integration.

## What Was Created

### 1. Server Launch Script
**Location**: `mud_analyzer/launch_servers.py` (8.6 KB)

A comprehensive Python script for managing API and MCP servers with the following features:

✅ **Server Management**
- Start REST API and MCP servers individually or together
- Auto-restart on crash
- Health monitoring
- Clean shutdown (Ctrl+C)
- PID tracking and logging

✅ **Configuration Options**
- Custom host and port for REST API
- Check server status
- Monitor running processes

✅ **Usage**
```bash
# Start both servers
python launch_servers.py --all

# Start REST API only (port 8000)
python launch_servers.py --rest

# Start MCP only
python launch_servers.py --mcp

# Custom port
python launch_servers.py --rest --port 8001

# Check status
python launch_servers.py --check
```

### 2. Client Library
**Location**: `mud_analyzer_client/` directory

Complete Python client library with 6 files:

#### Core Modules

**rest_client.py** (6.2 KB)
- `MUDAnalyzerClient` - Main REST API client
- `SearchResult` - Search result data class
- `ZoneInfo` - Zone information data class
- Methods:
  - `health()` - Check API health
  - `get_zones()` - List zones
  - `get_zone(zone_num)` - Zone details
  - `search(query)` - Search objects/mobiles
  - `search_objects(query)` - Object search
  - `search_mobiles(query)` - Mobile search
  - `get_object(vnum)` - Object details
  - `get_mobile(vnum)` - Mobile details
  - `find_assemblies(vnum)` - Item assemblies

**mcp_client.py** (12.6 KB)
- `MUDAnalyzerMCPClient` - MCP server client
- `LLMIntegration` - Claude API integration helper
- `ToolResult` - Tool execution result
- Methods for all MCP tools
- Claude-compatible tool definitions
- Tool call processing

#### Example Scripts

**examples_rest_api.py** (6.6 KB)
7 complete example functions:
1. Basic usage and health check
2. Searching objects and mobiles
3. Getting zone details
4. Getting entity details
5. Batch searching
6. Pagination
7. API documentation

**examples_mcp.py** (8.7 KB)
8 complete example functions:
1. Basic search via MCP
2. Getting zone info
3. Getting object details
4. Getting mobile details
5. Finding item assemblies
6. Searching by entity type
7. LLM integration setup
8. Listing available tools

#### Documentation

**README.md** (10.6 KB)
Comprehensive documentation including:
- Overview of REST and MCP clients
- Project structure
- Setup instructions
- Complete API reference
- LLM integration guide
- Claude AI examples
- Error handling
- Troubleshooting guide
- Dependencies

**QUICK_START.md** (2.8 KB)
Quick start guide:
- 5-minute setup
- Quick code examples
- Common tasks
- Troubleshooting
- API cheat sheet

**requirements.txt** (335 bytes)
Dependencies:
- `requests>=2.31.0` - REST API client
- Optional: `anthropic>=0.7.0` - LLM integration

**__init__.py** (116 bytes)
Package initialization

## File Structure

```
mud_analyzer/
├── launch_servers.py          # Server launcher script ✨ NEW

mud_analyzer_client/           # ✨ NEW CLIENT PROJECT
├── __init__.py
├── rest_client.py             # REST API client
├── mcp_client.py              # MCP client & LLM integration
├── examples_rest_api.py       # 7 REST examples
├── examples_mcp.py            # 8 MCP examples
├── README.md                  # Complete documentation
├── QUICK_START.md             # Quick start guide
└── requirements.txt           # Dependencies
```

## Quick Usage Examples

### Starting Servers

```bash
# Terminal 1: Start servers
cd mud_analyzer
python launch_servers.py --all

# Output:
# 🚀 Starting REST API server...
# ✅ REST API server started (PID: 12345)
#    📍 OpenAPI Docs: http://127.0.0.1:8000/docs
#
# 🚀 Starting MCP server...
# ✅ MCP server started (PID: 12346)
```

### REST API Client

```python
# Terminal 2: Use REST client
from rest_client import MUDAnalyzerClient

with MUDAnalyzerClient() as client:
    # Search
    results = client.search_objects("sword")
    for item in results:
        print(f"Found: {item.name} (VNUM {item.vnum})")
    
    # Get zones
    zones = client.get_zones(limit=5)
    for zone in zones:
        print(f"Zone {zone.zone_num}: {zone.name}")
```

### MCP Client (LLM Integration)

```python
from mcp_client import LLMIntegration

with LLMIntegration() as llm:
    # Get Claude-compatible tools
    tools = llm.get_tools_for_claude()
    
    # Process tool calls
    result = llm.process_tool_call(
        "search_mud_world",
        {"query": "dragon"}
    )
    print(result)  # JSON with results
```

## Running Examples

```bash
cd mud_analyzer_client

# Run REST API examples
python examples_rest_api.py
# Output:
# ============================================================
# 🏰 MUD ANALYZER - REST API CLIENT EXAMPLES
# ============================================================
#
# ============================================================
# EXAMPLE 1: Basic Usage
# ============================================================
# ✅ API is healthy
# 📍 Getting zones...
#   Zone 30: Necrotic Citadel by keldor
# ... (more examples)

# Run MCP examples
python examples_mcp.py
# Output:
# ============================================================
# 🏰 MUD ANALYZER - MCP CLIENT EXAMPLES
# ============================================================
#
# ============================================================
# EXAMPLE 1: Basic Search via MCP
# ============================================================
# ... (examples)
```

## API Documentation

Once servers are running, view documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Key Features

### Server Launcher
- ✅ Dual-server management
- ✅ Auto-restart on crash
- ✅ Process health monitoring
- ✅ Clean shutdown handling
- ✅ Detailed logging
- ✅ Configurable ports/hosts

### REST Client
- ✅ Pythonic interface
- ✅ Type hints
- ✅ Context manager support
- ✅ Error handling
- ✅ Comprehensive methods
- ✅ Data classes for results

### MCP Client
- ✅ Tool-based interface
- ✅ JSON-RPC 2.0 support
- ✅ Error handling
- ✅ LLM integration helpers

### LLM Integration
- ✅ Claude API ready
- ✅ Tool definitions included
- ✅ Tool call processing
- ✅ JSON response format

## Integration Points

### With FastAPI Server
```python
client = MUDAnalyzerClient("http://api.example.com:8000")
results = client.search("dragon")
```

### With Claude API
```python
import anthropic
from mcp_client import LLMIntegration

with LLMIntegration() as llm:
    tools = llm.get_tools_for_claude()
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=tools,
        messages=[...]
    )
```

## Error Handling

### REST Client
```python
from rest_client import MUDAnalyzerClientError

try:
    with MUDAnalyzerClient() as client:
        zones = client.get_zones()
except MUDAnalyzerClientError as e:
    print(f"API Error: {e}")
```

### MCP Client
```python
from mcp_client import MCPClientError, ToolResult

try:
    with MUDAnalyzerMCPClient() as client:
        result = client.search("dragon")
        if result.success:
            print(result.data)
        else:
            print(f"Error: {result.error}")
except MCPClientError as e:
    print(f"MCP Error: {e}")
```

## Dependencies

**Minimal**: Only `requests` for REST client
**With LLM**: Add `anthropic` package

```bash
pip install -r requirements.txt
pip install anthropic  # Optional for LLM integration
```

## Next Steps

1. **Start servers**: `cd mud_analyzer && python launch_servers.py --all`
2. **Run examples**: `cd mud_analyzer_client && python examples_rest_api.py`
3. **Check docs**: Visit http://localhost:8000/docs
4. **Build integration**: Use clients in your application
5. **Explore LLM**: Try Claude integration with tools

## File Statistics

| Component | Files | Size | Purpose |
|-----------|-------|------|---------|
| Server Launcher | 1 | 8.6 KB | Manage API/MCP servers |
| REST Client | 1 | 6.2 KB | HTTP API access |
| MCP Client | 1 | 12.6 KB | LLM server integration |
| Examples | 2 | 15.3 KB | Usage demonstrations |
| Docs | 3 | 13.4 KB | Documentation |
| Config | 1 | 0.3 KB | Dependencies |

**Total**: 9 files, ~56 KB

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│          MUD ANALYZER ECOSYSTEM              │
└─────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌───▼───┐    ┌───▼───┐   ┌──▼────┐
    │ Launch│    │ REST  │   │ MCP   │
    │Servers│    │API    │   │Server │
    └───┬───┘    └───┬───┘   └──┬────┘
        │            │          │
        │        ┌───▼──────────▼─┐
        │        │ mud_analyzer_  │
        │        │ api/           │
        │        │ (Services)     │
        │        └───┬────────────┘
        │            │
        │        ┌───▼──────────────────┐
        │        │ core/ & analysis/    │
        │        │ (Business Logic)     │
        │        └──────────────────────┘
        │
    ┌───▼──────────────────────────────┐
    │  mud_analyzer_client/             │
    │  ┌─ REST Client                   │
    │  ├─ MCP Client                    │
    │  ├─ LLM Integration               │
    │  └─ Examples & Docs               │
    └───────────────────────────────────┘
```

## Verification

To verify everything was created correctly:

```bash
# Check launch script
ls -l mud_analyzer/launch_servers.py

# Check client project
ls -l mud_analyzer_client/
# Should show: __init__.py, rest_client.py, mcp_client.py,
#              examples_*.py, README.md, QUICK_START.md, requirements.txt
```

---

**Status**: ✅ Complete
**Date**: January 10, 2026
**Files Created**: 10 files (1 launcher + 9 client files)
**Ready to Use**: Yes, see QUICK_START.md in mud_analyzer_client/
