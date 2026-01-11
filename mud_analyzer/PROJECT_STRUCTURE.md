# MUD Analyzer - Project Structure

This document describes the refactored logical structure of the MUD Analyzer project.

## Directory Structure

```
mud_analyzer/
├── api/                               # Modern API servers
│   ├── __init__.py
│   ├── rest_server.py                 # FastAPI REST API
│   └── mcp_server.py                  # Model Context Protocol server
│
├── analysis/                          # Data analysis & formatting utilities
│   ├── __init__.py
│   ├── identify_mobile.py             # Mobile entity identification
│   ├── identify_object.py             # Object entity identification
│   └── zone_summary.py                # Zone statistical summaries
│
├── core/                              # Core world data structures
│   ├── __init__.py
│   └── world_lookup.py                # Main world data loader
│
├── legacy/                            # Interactive CLI components (deprecated)
│   ├── __init__.py
│   ├── main.py                        # Legacy entry point with command routing
│   ├── menu.py                        # Interactive main menu system
│   ├── base_explorer.py               # Base class for explorers
│   ├── zone_explorer.py               # Interactive zone exploration
│   ├── zone_browser.py                # Zone listing and browsing
│   ├── global_search.py               # Global search across all zones
│   ├── help_system.py                 # Built-in help documentation
│   ├── assembled_items.py             # Assembled items exploration
│   └── script_created_items.py        # Script-created items analysis
│
├── mud_analyzer_api/                  # API layer (FastAPI/MCP implementation)
│   ├── __init__.py
│   ├── config.py                      # API-specific configuration
│   ├── core/                          # API business logic
│   │   ├── __init__.py
│   │   ├── assembly_service.py        # Item assembly analysis
│   │   ├── search_service.py          # Search functionality
│   │   └── world_service.py           # World data access
│   ├── models/                        # Pydantic data models
│   │   ├── __init__.py
│   │   └── entities.py                # API entity definitions
│   ├── services/                      # Additional API services
│   └── tests/                         # API tests
│       ├── __init__.py
│       └── test_api.py
│
├── shared/                            # Shared utilities & configuration
│   ├── __init__.py
│   ├── config.py                      # Global configuration & paths
│   ├── error_handler.py               # Error handling & validation
│   └── cache_manager.py               # Caching system
│
├── utils/                             # Utility functions
│   ├── __init__.py
│   └── spell_lookup.py                # Spell data loading
│
├── data/                              # Static data files
│   └── spells.json                    # Spell definitions
│
├── __init__.py                        # Package root
├── README.md                          # Main documentation
├── README-API.md                      # API documentation
├── requirements-api.txt               # Project dependencies
├── data_service.py                    # Unified data access layer
├── status_checker.py                  # Project diagnostics
├── mud_lut.py                         # Lookup table utilities
├── mud_lut_new.py                     # Newer lookup table implementation
└── performance.py                     # Performance profiling tools
```

## Design Principles

### 1. **Separation of Concerns**
- **`api/`**: Modern API servers (REST and MCP)
- **`legacy/`**: Interactive CLI (deprecated but preserved)
- **`core/`**: Core domain logic
- **`shared/`**: Cross-cutting concerns (config, error handling, caching)

### 2. **Clear Dependency Flow**
```
api/ → mud_analyzer_api/ → core/ + analysis/ + utils/
         ↓
       shared/
```

### 3. **Module Responsibilities**

#### Core Modules
- **`core/world_lookup.py`**: Loads and manages world data
- **`data_service.py`**: Unified interface to world data with caching
- **`analysis/`**: Entity identification and formatting

#### API Layer
- **`api/rest_server.py`**: FastAPI endpoints
- **`api/mcp_server.py`**: Model Context Protocol server
- **`mud_analyzer_api/`**: Service implementations

#### Legacy CLI (Preserved for Backward Compatibility)
- **`legacy/main.py`**: Entry point with command routing
- **`legacy/menu.py`**: Interactive menu system
- **`legacy/zone_explorer.py`**: Zone exploration
- **`legacy/global_search.py`**: Full-text search

#### Shared Infrastructure
- **`shared/config.py`**: Path resolution and configuration
- **`shared/error_handler.py`**: Error handling and validation
- **`shared/cache_manager.py`**: Performance optimization

## Entry Points

### Modern API (Recommended)
```bash
# REST API
python api/rest_server.py

# MCP Server
python api/mcp_server.py
```

### Legacy CLI
```bash
# Interactive menu
python legacy/main.py

# Command routing
python legacy/main.py [command]
```

## Import Patterns

### From API Server
```python
from mud_analyzer_api.core.world_service import WorldService
from mud_analyzer_api.models.entities import SearchRequest
```

### From Core/Shared
```python
from mud_analyzer.core.world_lookup import World
from mud_analyzer.shared.config import config
from mud_analyzer.shared.error_handler import validate_vnum
```

### From Legacy (if needed)
```python
from mud_analyzer.legacy.zone_explorer import ZoneExplorer
from mud_analyzer.legacy.global_search import GlobalSearch
```

## Migration Guide

### For New Development
Use the **modern API** (`api/rest_server.py` or `api/mcp_server.py`):
- Better structured
- Type-safe with Pydantic models
- Test-driven
- LLM-friendly

### Legacy Code
The `legacy/` directory preserves the original interactive CLI:
- Use for backward compatibility
- Reference for interactive patterns
- Do not expand further

## Testing

### API Tests
```bash
pytest mud_analyzer_api/tests/
```

### Manual Testing
```bash
# Check project setup
python status_checker.py

# Test CLI
python legacy/main.py menu

# Test REST API
curl http://localhost:8000/api/zones
```

## Dependencies

See `requirements-api.txt` for all project dependencies.

Key dependencies:
- **FastAPI**: REST API framework
- **Pydantic**: Data validation
- **MCP**: Model Context Protocol
- **pytest**: Testing framework

## Performance

- **Caching**: Via `shared/cache_manager.py`
- **Profiling**: Use `performance.py` for analysis
- **Lookup Tables**: `mud_lut.py`, `mud_lut_new.py`

## Configuration

Global settings in `shared/config.py`:
- Path resolution
- Cache validity (default: 1 hour)
- Pagination sizes
- Search limits

API-specific settings in `mud_analyzer_api/config.py`.

## Future Improvements

1. Remove `legacy/` directory once migration is complete
2. Consolidate `mud_lut.py` and `mud_lut_new.py`
3. Move utility scripts to `tools/` or CLI commands
4. Expand `mud_analyzer_api/tests/` coverage
