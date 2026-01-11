"""
MCP (Model Context Protocol) Client for MUD Analyzer
Provides tools and resources for LLM integration
"""

import json
import subprocess
import sys
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class ToolType(Enum):
    """MCP tool types"""
    SEARCH = "search"
    GET_ZONE = "get_zone"
    GET_OBJECT = "get_object"
    GET_MOBILE = "get_mobile"
    FIND_ASSEMBLIES = "find_assemblies"


@dataclass
class Tool:
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    tool_type: ToolType


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    data: Any
    error: Optional[str] = None


import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class MCPClientError(Exception):
    """MCP Client error"""
    pass


class MUDAnalyzerMCPClient:
    """
    MCP Client for MUD Analyzer
    Communicates with the MCP server via stdio
    
    The MCP server should be started separately using:
        python ../mud_analyzer/launch_servers.py --mcp
    
    Example:
        >>> with MUDAnalyzerMCPClient() as client:
        ...     tools = client.list_tools()
        ...     result = client.search_zones("dragon")
    """
    
    def __init__(self, server_path: Optional[str] = None, use_subprocess: bool = True):
        """
        Initialize MCP client
        
        Args:
            server_path: Path to MCP server script (only used if use_subprocess=True)
            use_subprocess: If True, spawn MCP server as subprocess. Otherwise expects server to be running.
        """
        self.server_path = server_path or self._find_server_path()
        self.use_subprocess = use_subprocess
        self.process: Optional[subprocess.Popen] = None
        self.tools: Dict[str, Tool] = {}
        self._initialize()
    
    def _find_server_path(self) -> str:
        """Find MCP server path"""
        from pathlib import Path
        
        possible_paths = [
            Path(__file__).parent / "mcp_server.py",
            Path(__file__).parent.parent / "mud_analyzer" / "api" / "mcp_server.py",
            Path.cwd() / "api" / "mcp_server.py",
            Path.cwd() / "mud_analyzer" / "api" / "mcp_server.py",
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        raise MCPClientError(
            "MCP server not found. Please provide server_path or ensure it's in expected location."
        )
    
    def _initialize(self) -> None:
        """Initialize connection to MCP server"""
        if not self.use_subprocess:
            logging.info(
                "MCP client initialized in connection mode. "
                "Make sure the MCP server is running: "
                "python ../mud_analyzer/launch_servers.py --mcp"
            )
            return
        
        try:
            logging.info(f"Attempting to start MCP server from: {self.server_path}")
            self.process = subprocess.Popen(
                [sys.executable, self.server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            logging.info("MCP server process started successfully")
        except FileNotFoundError:
            raise MCPClientError(
                f"MCP server not found at {self.server_path}. "
                f"Make sure the MCP server is installed and the path is correct, "
                f"or use use_subprocess=False and run the server separately."
            )
    
    def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to MCP server"""
        if not self.process:
            raise MCPClientError("MCP client not connected")
        
        try:
            request_json = json.dumps(request) + "\n"
            logging.debug(f"Sending request: {request_json}")
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            response_line = self.process.stdout.readline()
            if not response_line:
                # Try to read stderr for error messages
                stderr_output = self.process.stderr.readline()
                if stderr_output:
                    raise MCPClientError(f"MCP server error: {stderr_output}")
                raise MCPClientError("No response from MCP server")
            
            logging.debug(f"Received response: {response_line}")
            return json.loads(response_line)
        except json.JSONDecodeError as je:
            raise MCPClientError(f"Invalid JSON response from MCP server: {je}")
        except Exception as e:
            raise MCPClientError(f"MCP communication failed: {e}")
    
    def list_tools(self) -> List[Tool]:
        """List available tools"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        
        try:
            response = self._send_request(request)
            # Parse response and populate self.tools
            return list(self.tools.values())
        except Exception as e:
            raise MCPClientError(f"Failed to list tools: {e}")
    
    def search(
        self,
        query: str,
        entity_type: Optional[str] = None,
        limit: int = 50
    ) -> ToolResult:
        """
        Search for objects and mobiles
        
        Args:
            query: Search query
            entity_type: Filter by type ("object" or "mobile")
            limit: Maximum results
        
        Returns:
            Tool result with search results
        """
        logging.info(f"Searching for {entity_type or 'all'} with query: {query}")
        params = {
            "query": query,
            "limit": limit
        }
        if entity_type:
            params["entity_type"] = entity_type
        
        return self._call_tool("search_mud_world", params)
    
    def search_objects(self, query: str, limit: int = 50) -> ToolResult:
        """Search for objects"""
        return self.search(query, entity_type="object", limit=limit)
    
    def search_mobiles(self, query: str, limit: int = 50) -> ToolResult:
        """Search for mobiles"""
        return self.search(query, entity_type="mobile", limit=limit)
    
    def get_zone(self, zone_num: int) -> ToolResult:
        """
        Get zone information
        
        Args:
            zone_num: Zone number
        
        Returns:
            Tool result with zone details
        """
        return self._call_tool("get_zone_info", {"zone_num": zone_num})
    
    def get_object(self, vnum: int) -> ToolResult:
        """
        Get object information
        
        Args:
            vnum: Object virtual number
        
        Returns:
            Tool result with object details
        """
        return self._call_tool("get_object_details", {"vnum": vnum})
    
    def get_mobile(self, vnum: int) -> ToolResult:
        """
        Get mobile information
        
        Args:
            vnum: Mobile virtual number
        
        Returns:
            Tool result with mobile details
        """
        return self._call_tool("get_mobile_details", {"vnum": vnum})
    
    def find_assemblies(self, obj_vnum: int, limit: int = 50) -> ToolResult:
        """
        Find item assemblies
        
        Args:
            obj_vnum: Object virtual number
            limit: Maximum results
        
        Returns:
            Tool result with assembly information
        """
        return self._call_tool("find_item_assemblies", {"obj_vnum": obj_vnum, "limit": limit})
    
    def _call_tool(self, tool_name: str, params: Dict[str, Any]) -> ToolResult:
        """Call a tool on the MCP server"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            },
            "id": 1
        }
        
        try:
            response = self._send_request(request)
            
            if "error" in response:
                return ToolResult(
                    success=False,
                    data=None,
                    error=response["error"].get("message", "Unknown error")
                )
            
            result = response.get("result", {})
            return ToolResult(
                success=result.get("success", False),
                data=result.get("data"),
                error=result.get("error")
            )
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))
    
    def close(self) -> None:
        """Close the connection"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class LLMIntegration:
    """
    Helper class for LLM integration with MCP server
    Provides a simple interface for Claude and other LLMs
    
    Example:
        >>> llm = LLMIntegration()
        >>> tools = llm.get_tools_for_claude()
        >>> # Use tools in Claude API calls
    """
    
    def __init__(self):
        self.mcp_client = MUDAnalyzerMCPClient()
    
    def get_tools_for_claude(self) -> List[Dict[str, Any]]:
        """
        Get tools formatted for Claude API
        
        Returns:
            List of tool definitions compatible with Claude
        """
        return [
            {
                "name": "search_mud_world",
                "description": "Search for objects and mobiles in the MUD world",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "entity_type": {
                            "type": "string",
                            "enum": ["object", "mobile"],
                            "description": "Filter by entity type (optional)"
                        },
                        "limit": {"type": "integer", "description": "Max results (default: 50)"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_zone_info",
                "description": "Get detailed information about a zone",
                "input_schema": {
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
                "input_schema": {
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
                "input_schema": {
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
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "obj_vnum": {"type": "integer", "description": "Object virtual number"},
                        "limit": {"type": "integer", "description": "Max results (default: 50)"}
                    },
                    "required": ["obj_vnum"]
                }
            }
        ]
    
    def process_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Process a tool call from LLM
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
        
        Returns:
            JSON string with results
        """
        try:
            if tool_name == "search_mud_world":
                result = self.mcp_client.search(
                    arguments["query"],
                    arguments.get("entity_type"),
                    arguments.get("limit", 50)
                )
            elif tool_name == "get_zone_info":
                result = self.mcp_client.get_zone(arguments["zone_num"])
            elif tool_name == "get_object_details":
                result = self.mcp_client.get_object(arguments["vnum"])
            elif tool_name == "get_mobile_details":
                result = self.mcp_client.get_mobile(arguments["vnum"])
            elif tool_name == "find_item_assemblies":
                result = self.mcp_client.find_assemblies(
                    arguments["obj_vnum"],
                    arguments.get("limit", 50)
                )
            else:
                return json.dumps({"error": f"Unknown tool: {tool_name}"})
            
            return json.dumps({
                "success": result.success,
                "data": result.data,
                "error": result.error
            })
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def close(self) -> None:
        """Close MCP connection"""
        self.mcp_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
