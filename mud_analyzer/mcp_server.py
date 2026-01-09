#!/usr/bin/env python3
"""
MUD Analyzer MCP Server
A Model Context Protocol server for AddictMUD world data analysis
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

from mud_analyzer_api.core.world_service import WorldService
from mud_analyzer_api.core.search_service import SearchService
from mud_analyzer_api.core.assembly_service import AssemblyService
from mud_analyzer_api.models.entities import SearchRequest, AssemblyRequest
from mud_analyzer_api.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mud_analyzer_mcp")

class MudAnalyzerMCPServer:
    def __init__(self, config: Config):
        self.config = config
        self.world_service = WorldService(config)
        self.search_service = SearchService(self.world_service)
        self.assembly_service = AssemblyService(self.world_service)
        self.server = Server("mud-analyzer")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available MUD world resources"""
            resources = []
            
            # Add zone resources
            zones = await self.world_service.get_zones()
            for zone in zones:
                resources.append(Resource(
                    uri=f"mud://zone/{zone.number}",
                    name=f"Zone {zone.number}: {zone.name}",
                    description=f"Zone data for {zone.name} (Author: {zone.author})",
                    mimeType="application/json"
                ))
            
            return resources
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read a specific MUD resource"""
            if uri.startswith("mud://zone/"):
                zone_num = int(uri.split("/")[-1])
                zone_data = await self.world_service.get_zone_details(zone_num)
                return json.dumps(zone_data.dict(), indent=2)
            
            raise ValueError(f"Unknown resource URI: {uri}")
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available MUD analysis tools"""
            return [
                Tool(
                    name="search_objects",
                    description="Search for objects across all zones",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search term"},
                            "accessible_only": {"type": "boolean", "default": False},
                            "limit": {"type": "integer", "default": 50}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="search_mobiles",
                    description="Search for mobiles across all zones",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search term"},
                            "accessible_only": {"type": "boolean", "default": False},
                            "limit": {"type": "integer", "default": 50}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_object_details",
                    description="Get detailed information about a specific object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "vnum": {"type": "integer", "description": "Object VNUM"}
                        },
                        "required": ["vnum"]
                    }
                ),
                Tool(
                    name="get_mobile_details",
                    description="Get detailed information about a specific mobile",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "vnum": {"type": "integer", "description": "Mobile VNUM"}
                        },
                        "required": ["vnum"]
                    }
                ),
                Tool(
                    name="analyze_assemblies",
                    description="Analyze assembled/craftable items",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "accessible_only": {"type": "boolean", "default": True},
                            "min_success_rate": {"type": "number", "default": 0.0}
                        }
                    }
                ),
                Tool(
                    name="get_zone_summary",
                    description="Get summary information for a specific zone",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "zone_number": {"type": "integer", "description": "Zone number"}
                        },
                        "required": ["zone_number"]
                    }
                ),
                Tool(
                    name="find_load_locations",
                    description="Find where an item loads in the game",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "vnum": {"type": "integer", "description": "Item VNUM"}
                        },
                        "required": ["vnum"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "search_objects":
                    request = SearchRequest(
                        query=arguments["query"],
                        entity_type="object",
                        accessible_only=arguments.get("accessible_only", False),
                        limit=arguments.get("limit", 50)
                    )
                    results = await self.search_service.search_entities(request)
                    return [TextContent(
                        type="text",
                        text=json.dumps([r.dict() for r in results], indent=2)
                    )]
                
                elif name == "search_mobiles":
                    request = SearchRequest(
                        query=arguments["query"],
                        entity_type="mobile",
                        accessible_only=arguments.get("accessible_only", False),
                        limit=arguments.get("limit", 50)
                    )
                    results = await self.search_service.search_entities(request)
                    return [TextContent(
                        type="text",
                        text=json.dumps([r.dict() for r in results], indent=2)
                    )]
                
                elif name == "get_object_details":
                    vnum = arguments["vnum"]
                    details = await self.world_service.get_object_details(vnum)
                    return [TextContent(
                        type="text",
                        text=json.dumps(details.dict(), indent=2)
                    )]
                
                elif name == "get_mobile_details":
                    vnum = arguments["vnum"]
                    details = await self.world_service.get_mobile_details(vnum)
                    return [TextContent(
                        type="text",
                        text=json.dumps(details.dict(), indent=2)
                    )]
                
                elif name == "analyze_assemblies":
                    request = AssemblyRequest(
                        accessible_only=arguments.get("accessible_only", True),
                        min_success_rate=arguments.get("min_success_rate", 0.0)
                    )
                    results = await self.assembly_service.analyze_assemblies(request)
                    return [TextContent(
                        type="text",
                        text=json.dumps([r.dict() for r in results], indent=2)
                    )]
                
                elif name == "get_zone_summary":
                    zone_number = arguments["zone_number"]
                    summary = await self.world_service.get_zone_summary(zone_number)
                    return [TextContent(
                        type="text",
                        text=json.dumps(summary.dict(), indent=2)
                    )]
                
                elif name == "find_load_locations":
                    vnum = arguments["vnum"]
                    locations = await self.world_service.get_load_locations(vnum)
                    return [TextContent(
                        type="text",
                        text=json.dumps([l.dict() for l in locations], indent=2)
                    )]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
            
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

async def main():
    """Main entry point"""
    config = Config()
    mcp_server = MudAnalyzerMCPServer(config)
    
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mud-analyzer",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())