# MUD Analyzer Client Library

Client library and examples for using the MUD Analyzer API and MCP servers.

## Overview

This project provides three ways to interact with the MUD Analyzer:

1. **REST API Client** - Modern REST API for direct integration
2. **MCP Client** - Model Context Protocol for LLM integration
3. **GUI Applications** - User-friendly graphical interfaces

## Project Structure

```
mud_analyzer_client/
├── __init__.py                    # Package root
├── rest_client.py                 # REST API client library
├── mcp_client.py                  # MCP client library & LLM integration
├── gui.py                         # Desktop GUI application
├── web_gui.py                     # Web GUI application
├── templates/
│   └── index.html                 # Web GUI HTML template
├── examples_rest_api.py           # REST API usage examples
├── examples_mcp.py                # MCP client usage examples
├── requirements.txt               # Dependencies
├── README.md                      # This file
└── GUI_README.md                  # GUI documentation
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Servers

Before using the clients, you need to start the API servers:

```bash
# From the mud_analyzer directory
cd ../mud_analyzer

# Start both servers
python launch_servers.py --all

# Or start individually
python launch_servers.py --rest          # REST API only (port 8000)
python launch_servers.py --mcp           # MCP server only
python launch_servers.py --rest --port 8001  # Custom port
```

## Usage

### GUI Applications

**Want a visual interface?** Try one of our GUI applications:

#### Desktop GUI (Tkinter)
```bash
# Start the desktop application
python gui.py
```
Perfect for local use with a native GUI experience.

#### Web GUI (Flask)
```bash
# Start the web server
python web_gui.py
# Open http://localhost:5000 in your browser
```
Perfect for browser-based access and mobile devices.

See [GUI_README.md](GUI_README.md) for detailed GUI documentation.

### REST API Client

The REST client provides a Python interface to the REST API.

#### Basic Example

```python
from rest_client import MUDAnalyzerClient

# Create client
with MUDAnalyzerClient("http://localhost:8000") as client:
    # Check health
    if client.health():
        print("API is healthy")
    
    # Get zones
    zones = client.get_zones(limit=10)
    for zone in zones:
        print(f"Zone {zone.zone_num}: {zone.name}")
    
    # Search
    results = client.search_objects("sword")
    for result in results:
        print(f"Found: {result.name}")
```

#### Complete API Reference

```python
from rest_client import MUDAnalyzerClient

client = MUDAnalyzerClient("http://localhost:8000")

# Health
client.health() -> bool

# Zones
client.get_zones(skip=0, limit=100) -> List[ZoneInfo]
client.get_zone(zone_num) -> Dict

# Search
client.search(query, entity_type=None, skip=0, limit=50) -> List[SearchResult]
client.search_objects(query, skip=0, limit=50) -> List[SearchResult]
client.search_mobiles(query, skip=0, limit=50) -> List[SearchResult]

# Entities
client.get_object(vnum) -> Dict
client.get_mobile(vnum) -> Dict

# Assemblies
client.find_assemblies(obj_vnum, skip=0, limit=50) -> Dict

# Utilities
client.get_docs_url() -> str  # OpenAPI documentation URL
client.close() -> None
```

### MCP Client

The MCP client provides access to the Model Context Protocol server for LLM integration.

#### Basic Example

```python
from mcp_client import MUDAnalyzerMCPClient

# Create client
with MUDAnalyzerMCPClient() as client:
    # Search
    result = client.search("dragon", limit=5)
    if result.success:
        print(f"Found: {result.data}")
    else:
        print(f"Error: {result.error}")
    
    # Get zone info
    result = client.get_zone(30)
    if result.success:
        print(f"Zone: {result.data}")
```

#### LLM Integration

```python
from mcp_client import LLMIntegration

# Create LLM integration
with LLMIntegration() as llm:
    # Get tools for Claude API
    tools = llm.get_tools_for_claude()
    
    # Use in Claude API call
    # client.messages.create(
    #     model="claude-3-5-sonnet-20241022",
    #     max_tokens=1024,
    #     tools=tools,
    #     messages=[...]
    # )
    
    # Process tool calls
    result = llm.process_tool_call(
        "search_mud_world",
        {"query": "dragon", "limit": 5}
    )
    print(result)  # JSON string with results
```

### Running Examples

#### REST API Examples

```bash
# View and run examples
python examples_rest_api.py
```

Examples include:
1. Basic usage and health check
2. Searching objects and mobiles
3. Getting zone details
4. Getting entity details
5. Batch searching
6. Pagination
7. API documentation links

#### MCP Examples

```bash
# View and run examples
python examples_mcp.py
```

Examples include:
1. Basic search via MCP
2. Getting zone info
3. Getting object details
4. Getting mobile details
5. Finding item assemblies
6. Searching by entity type
7. LLM integration setup
8. Listing available tools

## Server Launch Script

The `launch_servers.py` script manages starting and stopping the API and MCP servers.

### Usage

```bash
# Start both servers
python launch_servers.py --all

# Start REST API only
python launch_servers.py --rest

# Start MCP only
python launch_servers.py --mcp

# Custom host/port
python launch_servers.py --rest --host 0.0.0.0 --port 8001

# Check status
python launch_servers.py --check
```

### Features

- ✅ Manages both server processes
- ✅ Auto-restart on crash
- ✅ Health monitoring
- ✅ Clean shutdown (Ctrl+C)
- ✅ Configurable host/port
- ✅ Detailed logging

## REST API Endpoints

All endpoints are available at `http://localhost:8000/api/`

### Zones
- `GET /api/zones` - List zones
- `GET /api/zones/{zone_num}` - Get zone details
- `GET /api/zones/{zone_num}/summary` - Get zone summary

### Entities
- `GET /api/objects/{vnum}` - Get object details
- `GET /api/mobiles/{vnum}` - Get mobile details

### Search
- `POST /api/search` - Search objects and mobiles

### Assemblies
- `POST /api/assemblies` - Find item assemblies

### Documentation
- `GET /docs` - OpenAPI documentation (Swagger UI)
- `GET /redoc` - ReDoc documentation

## MCP Server Tools

The MCP server provides these tools for LLM integration:

### search_mud_world
Search for objects and mobiles in the MUD world

**Parameters:**
- `query` (string, required) - Search query
- `entity_type` (string, optional) - Filter by "object" or "mobile"
- `limit` (integer, optional) - Max results (default: 50)

### get_zone_info
Get detailed information about a zone

**Parameters:**
- `zone_num` (integer, required) - Zone number

### get_object_details
Get detailed information about an object

**Parameters:**
- `vnum` (integer, required) - Object virtual number

### get_mobile_details
Get detailed information about a mobile

**Parameters:**
- `vnum` (integer, required) - Mobile virtual number

### find_item_assemblies
Find how an item is used in assemblies

**Parameters:**
- `obj_vnum` (integer, required) - Object virtual number
- `limit` (integer, optional) - Max results (default: 50)

## Claude AI Integration

Example of using with Claude API:

```python
import anthropic
from mcp_client import LLMIntegration

client = anthropic.Anthropic()

# Get tools
with LLMIntegration() as llm:
    tools = llm.get_tools_for_claude()
    
    messages = [
        {
            "role": "user",
            "content": "What weapons are available in the MUD?"
        }
    ]
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )
    
    # Process tool calls
    for block in response.content:
        if block.type == "tool_use":
            result = llm.process_tool_call(block.name, block.input)
            print(f"Tool: {block.name}")
            print(f"Result: {result}")
```

## Error Handling

### REST Client

```python
from rest_client import MUDAnalyzerClient, MUDAnalyzerClientError

try:
    with MUDAnalyzerClient() as client:
        zones = client.get_zones()
except MUDAnalyzerClientError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

### MCP Client

```python
from mcp_client import MUDAnalyzerMCPClient, MCPClientError

try:
    with MUDAnalyzerMCPClient() as client:
        result = client.search("dragon")
        if result.success:
            print(result.data)
        else:
            print(f"Tool Error: {result.error}")
except MCPClientError as e:
    print(f"MCP Error: {e}")
```

## Development

### Project Layout

```
mud_analyzer_client/
├── rest_client.py           # REST client implementation
│   ├── MUDAnalyzerClient    # Main client class
│   ├── SearchResult         # Data class for search results
│   ├── ZoneInfo             # Data class for zone info
│   └── MUDAnalyzerClientError
├── mcp_client.py            # MCP client implementation
│   ├── MUDAnalyzerMCPClient # MCP client class
│   ├── LLMIntegration       # LLM helper class
│   ├── ToolResult           # Tool result data class
│   ├── Tool                 # Tool definition
│   └── MCPClientError
├── examples_rest_api.py     # 7 REST API examples
├── examples_mcp.py          # 8 MCP examples
└── requirements.txt         # Dependencies
```

### Adding New Features

1. **REST API**: Add methods to `MUDAnalyzerClient` class
2. **MCP**: Add tools to MCP server's tool definitions
3. **Examples**: Add example functions to example files

## Testing

Run examples to test functionality:

```bash
# Terminal 1: Start servers
cd ../mud_analyzer
python launch_servers.py --all

# Terminal 2: Run examples
cd ../mud_analyzer_client
python examples_rest_api.py
python examples_mcp.py
```

## Troubleshooting

### Connection Refused

**Issue**: `ConnectionError: Failed to connect to http://localhost:8000`

**Solution**: Start the API server
```bash
cd ../mud_analyzer
python launch_servers.py --rest
```

### MCP Server Not Found

**Issue**: `MCPClientError: MCP server not found`

**Solution**: Ensure server is running and path is correct
```bash
cd ../mud_analyzer
python launch_servers.py --mcp
```

### Port Already in Use

**Issue**: `OSError: Address already in use`

**Solution**: Use a different port
```bash
python launch_servers.py --rest --port 8001
```

Then update client:
```python
client = MUDAnalyzerClient("http://localhost:8001")
```

## Dependencies

See `requirements.txt`:

```
requests>=2.31.0     # REST API client
# MCP requires no additional dependencies for basic usage
# For LLM integration: pip install anthropic
```

## API Documentation

Once the REST server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Contributing

To extend the client library:

1. Add new methods to the appropriate client class
2. Create examples demonstrating the new functionality
3. Update this README with usage documentation

## License

Same as parent MUD Analyzer project

## Support

For issues, questions, or suggestions:
1. Check the examples for similar use cases
2. Review the API documentation
3. Check the server logs for errors
