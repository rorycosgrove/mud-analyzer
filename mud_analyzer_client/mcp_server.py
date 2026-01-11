#!/usr/bin/env python3
"""
MCP Server for MUD Analyzer
Implements the Model Context Protocol for MUD Analyzer
"""

import json
import sys
import logging
from typing import Dict, Any, List, Optional
import os

# Add parent directory to path to import rest_client
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging to stderr so stdout is reserved for JSON protocol
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server implementation for MUD Analyzer
    Communicates via JSON-RPC over stdio
    """
    
    def __init__(self):
        """Initialize the MCP server"""
        self.methods = {
            "tools/list": self.list_tools,
            "tools/call": self.call_tool,
            "initialize": self.initialize,
        }
        
        # Import REST client to use its functionality
        try:
            from rest_client import MUDAnalyzerClient
            try:
                self.rest_client = MUDAnalyzerClient("http://localhost:8000")
                logger.info("Connected to REST API backend at http://localhost:8000")
            except Exception as e:
                logger.warning(f"Could not connect to REST API at http://localhost:8000: {e}")
                logger.warning("Make sure to start the REST API server: python ../mud_analyzer/launch_servers.py --rest")
                self.rest_client = None
        except ImportError as e:
            logger.error(f"Could not import REST client: {e}")
            self.rest_client = None
    
    def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the MCP session"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            }
        }
    
    def list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available tools"""
        tools = [
            {
                "name": "search_mud_world",
                "description": "Search for objects and mobiles in the MUD world",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "entity_type": {
                            "type": "string",
                            "enum": ["object", "mobile", None],
                            "description": "Type of entity to search for"
                        },
                        "limit": {"type": "integer", "description": "Maximum results"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_zone_info",
                "description": "Get detailed information about a zone",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "zone_num": {"type": "integer", "description": "Zone number"}
                    },
                    "required": ["zone_num"]
                }
            },
            {
                "name": "get_object_details",
                "description": "Get detailed information about an object",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vnum": {"type": "integer", "description": "Object virtual number"}
                    },
                    "required": ["vnum"]
                }
            },
            {
                "name": "get_mobile_details",
                "description": "Get detailed information about a mobile",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vnum": {"type": "integer", "description": "Mobile virtual number"}
                    },
                    "required": ["vnum"]
                }
            },
            {
                "name": "find_item_assemblies",
                "description": "Find how an item is used in assemblies",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "obj_vnum": {"type": "integer", "description": "Object virtual number"},
                        "limit": {"type": "integer", "description": "Maximum results"}
                    },
                    "required": ["obj_vnum"]
                }
            }
        ]
        
        return {"tools": tools}
    
    def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        
        if tool_name == "search_mud_world":
            return self._search_mud_world(arguments)
        elif tool_name == "get_zone_info":
            return self._get_zone_info(arguments)
        elif tool_name == "get_object_details":
            return self._get_object_details(arguments)
        elif tool_name == "get_mobile_details":
            return self._get_mobile_details(arguments)
        elif tool_name == "find_item_assemblies":
            return self._find_item_assemblies(arguments)
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
    
    def _search_mud_world(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search for objects and mobiles"""
        try:
            if not self.rest_client:
                return {"success": False, "error": "REST API client not available"}
            
            query = args.get("query", "")
            entity_type = args.get("entity_type")
            limit = args.get("limit", 50)
            
            results = []
            
            if entity_type in [None, "object"]:
                try:
                    obj_results = self.rest_client.search_objects(query, limit=limit)
                    results.extend([r.__dict__ if hasattr(r, '__dict__') else r for r in obj_results])
                except Exception as e:
                    logger.warning(f"Object search failed: {e}")
            
            if entity_type in [None, "mobile"]:
                try:
                    mob_results = self.rest_client.search_mobiles(query, limit=limit)
                    results.extend([r.__dict__ if hasattr(r, '__dict__') else r for r in mob_results])
                except Exception as e:
                    logger.warning(f"Mobile search failed: {e}")
            
            return {"success": True, "data": results}
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_zone_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get zone information"""
        try:
            if not self.rest_client:
                return {"success": False, "error": "REST API client not available"}
            
            zone_num = args.get("zone_num")
            zone_info = self.rest_client.get_zone(zone_num)
            
            return {
                "success": True,
                "data": zone_info.__dict__ if hasattr(zone_info, '__dict__') else zone_info
            }
        except Exception as e:
            logger.error(f"Get zone info failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_object_details(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get object details"""
        try:
            if not self.rest_client:
                return {"success": False, "error": "REST API client not available"}
            
            vnum = args.get("vnum")
            obj_details = self.rest_client.get_object(vnum)
            
            return {
                "success": True,
                "data": obj_details.__dict__ if hasattr(obj_details, '__dict__') else obj_details
            }
        except Exception as e:
            logger.error(f"Get object details failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_mobile_details(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get mobile details"""
        try:
            if not self.rest_client:
                return {"success": False, "error": "REST API client not available"}
            
            vnum = args.get("vnum")
            mob_details = self.rest_client.get_mobile(vnum)
            
            return {
                "success": True,
                "data": mob_details.__dict__ if hasattr(mob_details, '__dict__') else mob_details
            }
        except Exception as e:
            logger.error(f"Get mobile details failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _find_item_assemblies(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Find item assemblies"""
        try:
            if not self.rest_client:
                return {"success": False, "error": "REST API client not available"}
            
            obj_vnum = args.get("obj_vnum")
            limit = args.get("limit", 50)
            
            result = self.rest_client.find_assemblies(obj_vnum, limit=limit)
            
            return {
                "success": True,
                "data": result.get("assemblies", []) if isinstance(result, dict) else result
            }
        except Exception as e:
            logger.error(f"Find assemblies failed: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a JSON-RPC request"""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id", 1)
        
        if method not in self.methods:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": "Method not found"},
                "id": request_id
            }
        
        try:
            result = self.methods[method](params)
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }
        except Exception as e:
            logger.error(f"Error handling method {method}: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": request_id
            }
    
    def run(self):
        """Run the MCP server"""
        logger.info("MCP Server started. Listening on stdio...")
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
            except EOFError:
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    server = MCPServer()
    server.run()
