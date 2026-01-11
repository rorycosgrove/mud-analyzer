#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Client Examples
Demonstrates how to use the MCP client for LLM integration

IMPORTANT: Before running these examples, start the servers:
1. Start the REST API server (required for MCP to function):
   python ../mud_analyzer/launch_servers.py --rest
   
   Or start all servers:
   python ../mud_analyzer/launch_servers.py --all

2. Then run this script:
   python examples_mcp.py
"""

from mcp_client import MUDAnalyzerMCPClient, LLMIntegration, MCPClientError
import json
import sys
import io

# Force UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def print_startup_instructions():
    """Print startup instructions"""
    print("\n" + "="*60)
    print("[*] MUD ANALYZER - MCP CLIENT EXAMPLES")
    print("="*60)
    print("\nMake sure the servers are running:")
    print("  1. REST API server: python ../mud_analyzer/launch_servers.py --rest")
    print("  2. Or run all servers: python ../mud_analyzer/launch_servers.py --all")
    print("\n" + "="*60)


def example_basic_search():
    """Basic search example"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Search via MCP")
    print("="*60)
    
    try:
        with MUDAnalyzerMCPClient() as client:
            print("🔍 Searching for 'sword'...")
            result = client.search("sword", limit=5)
            
            if result.success:
                print(f"✅ Found results:")
                if isinstance(result.data, list):
                    for item in result.data[:3]:
                        print(f"  - {item.get('name', 'Unknown')}")
                else:
                    print(f"  Data: {result.data}")
            else:
                print(f"❌ Error: {result.error}")
    
    except MCPClientError as e:
        print(f"❌ MCP Error: {e}")


def example_zone_info():
    """Get zone information"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Get Zone Info")
    print("="*60)
    
    try:
        with MUDAnalyzerMCPClient() as client:
            print("📍 Getting info for Zone 30...")
            result = client.get_zone(30)
            
            if result.success:
                print(f"✅ Zone information:")
                if isinstance(result.data, dict):
                    print(f"  Name: {result.data.get('name', 'N/A')}")
                    print(f"  Author: {result.data.get('author', 'N/A')}")
                    print(f"  Objects: {result.data.get('object_count', 0)}")
                    print(f"  Mobiles: {result.data.get('mobile_count', 0)}")
                else:
                    print(f"  Data: {result.data}")
            else:
                print(f"❌ Error: {result.error}")
    
    except MCPClientError as e:
        print(f"❌ MCP Error: {e}")


def example_object_details():
    """Get object details"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Get Object Details")
    print("="*60)
    
    try:
        with MUDAnalyzerMCPClient() as client:
            # Example VNUM - adjust based on your data
            vnum = 3001
            print(f"📦 Getting details for object VNUM {vnum}...")
            result = client.get_object(vnum)
            
            if result.success:
                print(f"✅ Object information:")
                if isinstance(result.data, dict):
                    print(f"  Name: {result.data.get('name', 'N/A')}")
                    print(f"  Short: {result.data.get('short_description', 'N/A')}")
                    print(f"  Type: {result.data.get('type', 'N/A')}")
                else:
                    print(f"  Data: {result.data}")
            else:
                print(f"ℹ️  Info: {result.error}")
    
    except MCPClientError as e:
        print(f"❌ MCP Error: {e}")


def example_mobile_details():
    """Get mobile details"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Get Mobile Details")
    print("="*60)
    
    try:
        with MUDAnalyzerMCPClient() as client:
            # Example VNUM - adjust based on your data
            vnum = 3005
            print(f"👹 Getting details for mobile VNUM {vnum}...")
            result = client.get_mobile(vnum)
            
            if result.success:
                print(f"✅ Mobile information:")
                if isinstance(result.data, dict):
                    print(f"  Name: {result.data.get('name', 'N/A')}")
                    print(f"  Short: {result.data.get('short_description', 'N/A')}")
                    print(f"  Level: {result.data.get('level', 'N/A')}")
                else:
                    print(f"  Data: {result.data}")
            else:
                print(f"ℹ️  Info: {result.error}")
    
    except MCPClientError as e:
        print(f"❌ MCP Error: {e}")


def example_find_assemblies():
    """Find item assemblies"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Find Item Assemblies")
    print("="*60)
    
    try:
        with MUDAnalyzerMCPClient() as client:
            # Example VNUM - adjust based on your data
            vnum = 3001
            print(f"🔗 Finding assemblies for VNUM {vnum}...")
            result = client.find_assemblies(vnum, limit=5)
            
            if result.success:
                print(f"✅ Assemblies found:")
                if isinstance(result.data, list):
                    if result.data:
                        for assembly in result.data[:3]:
                            print(f"  - {assembly.get('name', 'Unknown')}")
                    else:
                        print("  No assemblies found")
                else:
                    print(f"  Data: {result.data}")
            else:
                print(f"ℹ️  Info: {result.error}")
    
    except MCPClientError as e:
        print(f"❌ MCP Error: {e}")


def example_search_types():
    """Search for specific entity types"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Search by Entity Type")
    print("="*60)
    
    try:
        with MUDAnalyzerMCPClient() as client:
            # Search for objects
            print("📦 Searching for objects with 'potion'...")
            result = client.search_objects("potion", limit=3)
            
            if result.success and result.data:
                print(f"✅ Found objects:")
                for item in result.data[:2]:
                    print(f"  - {item.get('name', 'Unknown')}")
            else:
                print(f"  No objects found")
            
            # Search for mobiles
            print("\n👹 Searching for mobiles with 'guard'...")
            result = client.search_mobiles("guard", limit=3)
            
            if result.success and result.data:
                print(f"✅ Found mobiles:")
                for item in result.data[:2]:
                    print(f"  - {item.get('name', 'Unknown')}")
            else:
                print(f"  No mobiles found")
    
    except MCPClientError as e:
        print(f"❌ MCP Error: {e}")


def example_llm_integration():
    """LLM integration example"""
    print("\n" + "="*60)
    print("EXAMPLE 7: LLM Integration")
    print("="*60)
    
    try:
        with LLMIntegration() as llm:
            print("🤖 Getting tools for Claude API...")
            tools = llm.get_tools_for_claude()
            
            print(f"\n✅ Available tools ({len(tools)}):")
            for tool in tools:
                print(f"  - {tool['name']}")
                print(f"    {tool['description']}")
            
            # Example: Process a tool call
            print("\n📞 Processing tool call: search_mud_world...")
            result = llm.process_tool_call(
                "search_mud_world",
                {"query": "dragon", "limit": 3}
            )
            
            print(f"Result: {result}")
    
    except MCPClientError as e:
        print(f"❌ MCP Error: {e}")


def example_tool_listing():
    """List available tools"""
    print("\n" + "="*60)
    print("EXAMPLE 8: List Available Tools")
    print("="*60)
    
    try:
        with MUDAnalyzerMCPClient() as client:
            print("📋 Listing available tools...")
            tools = client.list_tools()
            
            if tools:
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")
            else:
                print("  No tools found")
    
    except MCPClientError as e:
        print(f"❌ MCP Error: {e}")


def main():
    """Run all examples"""
    print_startup_instructions()
    
    print("\n⚠️  NOTE: These examples require the REST API server to be running.")
    print("If you see 'REST API client not available' errors, please start the servers first.\n")
    
    try:
        example_basic_search()
        example_zone_info()
        example_object_details()
        example_mobile_details()
        example_find_assemblies()
        example_search_types()
        example_llm_integration()
        example_tool_listing()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the MCP server is running:")
        print("  cd ../mud_analyzer")
        print("  python launch_servers.py --mcp")


if __name__ == "__main__":
    main()
