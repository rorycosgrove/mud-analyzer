# Migration Guide: Legacy to API

## Overview

MUD Analyzer has been refactored into a modern API architecture while preserving the legacy interactive menu system.

## For New Users

**Use the API version** - it provides better performance, testing, and integration:

```bash
pip install -r requirements-api.txt
python mcp_server.py  # For LLM integration
# OR
python api_server.py  # For REST API
```

See [README-API.md](README-API.md) for complete documentation.

## For Existing Users

**Your existing workflows still work** - the legacy interactive menu is unchanged:

```bash
python main.py  # Same as always
```

## Key Differences

| Feature | Legacy | API |
|---------|--------|-----|
| **Interface** | Interactive menu | REST API + MCP |
| **Performance** | Synchronous | Async/await |
| **Testing** | Manual | Comprehensive pytest suite |
| **Integration** | Standalone | REST API + LLM integration |
| **Type Safety** | Basic | Full Pydantic validation |
| **Documentation** | Built-in help | OpenAPI docs |

## Migration Benefits

### For Developers
- **Better Testing**: Comprehensive test coverage
- **Type Safety**: Full Pydantic models
- **Modern Architecture**: Async/await throughout
- **Easy Integration**: REST API endpoints

### For LLM Integration
- **MCP Support**: Direct LLM integration
- **Natural Language**: Query via LLM tools
- **Structured Data**: JSON responses

### For Automation
- **REST API**: HTTP endpoints for scripts
- **Programmatic Access**: Python API
- **Batch Processing**: Async operations

## Compatibility

- **Legacy menu**: Fully preserved and functional
- **Data format**: Same JSON world data
- **Features**: All original functionality maintained
- **Performance**: Legacy system unchanged

## Recommendation

- **New projects**: Use API version
- **Existing workflows**: Can continue using legacy
- **LLM integration**: Use MCP server
- **Automation**: Use REST API