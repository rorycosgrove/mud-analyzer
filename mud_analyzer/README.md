# MUD Analyzer - AddictMUD World Analysis Tools

## Overview

MUD Analyzer provides comprehensive tools for exploring and analyzing AddictMUD world data. Available as both a modern API and legacy interactive menu system.

## 🚀 **NEW: API Version (Recommended)**

The project has been completely refactored into a modern, test-driven API with MCP support for LLM integration.

### Quick Start (API)

```bash
# Install API dependencies
pip install -r requirements-api.txt

# Start MCP server (for LLM integration)
python mcp_server.py

# OR start REST API server
python api_server.py
```

**See [README-API.md](README-API.md) for complete API documentation.**

### API Features

- 🔌 **MCP Integration** - Direct LLM integration via Model Context Protocol
- 🚀 **REST API** - FastAPI-based endpoints with OpenAPI docs
- 🧪 **Test-Driven** - Comprehensive pytest test suite
- ⚡ **Async/Await** - Modern async architecture throughout
- 🔍 **Smart Search** - Relevance-based entity search with accessibility filters
- 📊 **Assembly Analysis** - Traditional and script-created items
- 🎯 **Type Safety** - Full Pydantic models with validation

## 📜 **Legacy: Interactive Menu System**

The original interactive menu system is preserved for backward compatibility.

### Quick Start (Legacy)

1. **Setup**: Place analyzer in AddictMUD world directory
2. **Run**: `python main.py` for interactive menu
3. **Explore**: Start with Zone Browser to see available zones

### Legacy Features

- 🔍 **Global Search** - Search objects & mobiles across all zones
- 🌍 **Zone Browser** - Browse zones by name, author, or statistics  
- 🏰 **Zone Explorer** - Interactive exploration of individual zones
- 🔧 **Assembled Items** - Analyze craftable items and requirements
- 📊 **Zone Summary** - Generate comprehensive zone reports
- 📚 **Help System** - Built-in documentation and guidance

## Architecture

### New API Architecture (Recommended)

```
mud_analyzer/
├── mcp_server.py              # MCP server for LLM integration
├── api_server.py              # FastAPI REST server
├── requirements-api.txt       # API dependencies
└── mud_analyzer_api/
    ├── config.py              # Configuration management
    ├── models/
    │   └── entities.py        # Pydantic data models
    ├── core/
    │   ├── world_service.py   # World data access
    │   ├── search_service.py  # Entity search
    │   └── assembly_service.py # Assembly analysis
    └── tests/
        └── test_api.py        # Comprehensive test suite
```

### Legacy Architecture

```
mud_analyzer/
├── main.py                           # Entry point
├── menu.py                           # Main menu system
├── global_search_refactored.py       # Enhanced global search
├── zone_browser_refactored.py        # Enhanced zone browser
├── assembled_items_refactored.py     # Enhanced assembly analysis
├── zone_explorer.py                  # Zone exploration
└── core/
    └── world_lookup.py               # Core data access
```

## Usage

### API Usage (Recommended)

```bash
# MCP Server (for LLM integration)
python mcp_server.py

# REST API Server
python api_server.py
# Then visit http://localhost:8000/docs for API documentation

# Run tests
pytest mud_analyzer_api/tests/
```

### Legacy Usage

```bash
# Interactive menu
python main.py

# Command line shortcuts
python main.py search      # Global search
python main.py browse      # Zone browser  
python main.py explore 100 # Zone explorer
python main.py assembled   # Assembled items
```

## Migration Guide

**For New Projects**: Use the API version (README-API.md)

**For Existing Users**: The legacy interactive menu still works exactly as before

**For Developers**: The API provides better testing, type safety, and integration capabilities

## Performance Features

- **Async/Await**: Modern async architecture (API version)
- **Lazy Loading**: Data loaded only when needed
- **Intelligent Caching**: Automatic cache management
- **Type Safety**: Full Pydantic validation (API version)
- **Test Coverage**: Comprehensive test suite (API version)