# MUD Analyzer API

A test-driven API for AddictMUD world data analysis with Model Context Protocol (MCP) support for local LLM integration.

## Architecture

The project has been completely refactored into a clean, testable API architecture:

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

## Features

### 🔌 **MCP Integration**
- Full Model Context Protocol support
- Direct LLM integration for natural language queries
- Resource and tool-based interaction model

### 🚀 **REST API**
- FastAPI-based REST endpoints
- Automatic OpenAPI documentation
- CORS support for web integration

### 🧪 **Test-Driven Development**
- Comprehensive pytest test suite
- Async/await support throughout
- Mock-based testing for reliability

### 📊 **Core Functionality**
- **World Data Access**: Zones, objects, mobiles, scripts
- **Smart Search**: Relevance-based entity search with filters
- **Assembly Analysis**: Traditional and script-created items
- **Accessibility Checking**: Only show obtainable items
- **Load Location Tracking**: Where items actually spawn

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements-api.txt

# Set environment variables (optional)
export MUD_ANALYZER_WORLD_ROOT=/path/to/world/data
export MUD_ANALYZER_DEBUG=true
```

### MCP Server (for LLM integration)

```bash
# Start MCP server
python mcp_server.py
```

### REST API Server

```bash
# Start REST API
python api_server.py

# Or with uvicorn directly
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Run all tests
pytest mud_analyzer_api/tests/

# Run with coverage
pytest --cov=mud_analyzer_api mud_analyzer_api/tests/
```

## API Endpoints

### Zones
- `GET /zones` - List all zones
- `GET /zones/{zone_number}` - Zone summary

### Entities
- `GET /objects/{vnum}` - Object details
- `GET /mobiles/{vnum}` - Mobile details
- `GET /load-locations/{vnum}` - Where entity loads

### Search
- `GET /search/objects?query=sword&accessible_only=true` - Search objects
- `GET /search/mobiles?query=guard&limit=10` - Search mobiles
- `POST /search` - Advanced search with full request body

### Assemblies
- `GET /assemblies?accessible_only=true&min_success_rate=50` - Get assemblies
- `POST /assemblies/analyze` - Advanced assembly analysis

## MCP Tools

When using the MCP server, these tools are available:

- `search_objects` - Search for objects
- `search_mobiles` - Search for mobiles  
- `get_object_details` - Get object information
- `get_mobile_details` - Get mobile information
- `analyze_assemblies` - Analyze craftable items
- `get_zone_summary` - Zone statistics
- `find_load_locations` - Where items load

## Configuration

Environment variables:

```bash
MUD_ANALYZER_WORLD_ROOT=/path/to/world/data
MUD_ANALYZER_CACHE_DIR=/path/to/cache
MUD_ANALYZER_API_HOST=localhost
MUD_ANALYZER_API_PORT=8000
MUD_ANALYZER_DEBUG=false
MUD_ANALYZER_CACHE_TTL=3600
MUD_ANALYZER_MAX_SEARCH_RESULTS=1000
```

## Example Usage

### Python Client

```python
import asyncio
from mud_analyzer_api.core.world_service import WorldService
from mud_analyzer_api.core.search_service import SearchService
from mud_analyzer_api.models.entities import SearchRequest, EntityType
from mud_analyzer_api.config import Config

async def main():
    config = Config()
    world_service = WorldService(config)
    search_service = SearchService(world_service)
    
    # Search for swords
    request = SearchRequest(
        query="sword",
        entity_type=EntityType.OBJECT,
        accessible_only=True,
        limit=10
    )
    
    results = await search_service.search_entities(request)
    for result in results:
        print(f"{result.entity.name} - {len(result.load_locations)} locations")

asyncio.run(main())
```

### REST API Client

```python
import httpx

async def search_items():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/search/objects",
            params={"query": "armor", "accessible_only": True}
        )
        items = response.json()
        for item in items:
            print(f"{item['entity']['name']} (Zone {item['entity']['zone']})")
```

### LLM Integration (via MCP)

The MCP server allows natural language queries:

```
"Find all accessible swords in the game"
"Show me the Armor of the Gods and how to get it"
"What items can be assembled in zone 100?"
"List all mobiles with special procedures"
```

## Testing

The API includes comprehensive tests:

```bash
# Run specific test categories
pytest mud_analyzer_api/tests/test_api.py::TestWorldService
pytest mud_analyzer_api/tests/test_api.py::TestSearchService
pytest mud_analyzer_api/tests/test_api.py::TestAssemblyService

# Run with verbose output
pytest -v mud_analyzer_api/tests/

# Run integration tests
pytest mud_analyzer_api/tests/test_api.py::TestIntegration
```

## Development

### Adding New Features

1. **Add models** in `mud_analyzer_api/models/entities.py`
2. **Implement service logic** in appropriate service class
3. **Add tests** in `mud_analyzer_api/tests/test_api.py`
4. **Add API endpoints** in `api_server.py`
5. **Add MCP tools** in `mcp_server.py`

### Code Quality

```bash
# Format code
black mud_analyzer_api/

# Sort imports
isort mud_analyzer_api/

# Type checking
mypy mud_analyzer_api/
```

## Migration from Legacy

The legacy interactive menu system is preserved but the new API provides:

- **Better Performance**: Async/await throughout
- **Better Testing**: Comprehensive test coverage
- **Better Integration**: REST API and MCP support
- **Better Maintainability**: Clean separation of concerns
- **Better Extensibility**: Easy to add new features

## License

Same as original MUD Analyzer project.