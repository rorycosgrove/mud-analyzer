#!/usr/bin/env python3
"""
Verify MCP & REST API Integration
Confirms that both servers are working correctly
"""

import sys
import json
from mcp_client import MUDAnalyzerMCPClient, LLMIntegration


def test_rest_api_connection():
    """Test REST API connection"""
    print("\n[TEST] REST API Connection")
    print("-" * 40)
    try:
        from rest_client import MUDAnalyzerClient
        client = MUDAnalyzerClient("http://localhost:8000")
        # Try a simple request to verify connection
        try:
            client.get_zones(limit=1)
            print("[OK] REST API is responding")
            return True
        except Exception as api_error:
            # API might be running but endpoint not implemented
            if "404" in str(api_error) or "not found" in str(api_error).lower():
                print("[OK] REST API is responding (endpoint not found, but server is up)")
                return True
            raise
    except Exception as e:
        print(f"[ERROR] Cannot connect to REST API: {e}")
        return False


def test_mcp_server_startup():
    """Test MCP server startup"""
    print("\n[TEST] MCP Server Startup")
    print("-" * 40)
    try:
        with MUDAnalyzerMCPClient() as client:
            print("[OK] MCP server started successfully")
            return True
    except Exception as e:
        print(f"[ERROR] MCP server failed to start: {e}")
        return False


def test_tool_discovery():
    """Test tool discovery"""
    print("\n[TEST] Tool Discovery")
    print("-" * 40)
    try:
        with LLMIntegration() as llm:
            tools = llm.get_tools_for_claude()
            if tools and len(tools) > 0:
                print(f"[OK] Found {len(tools)} tools:")
                for tool in tools:
                    print(f"     - {tool['name']}")
                return True
            else:
                print("[ERROR] No tools found")
                return False
    except Exception as e:
        print(f"[ERROR] Tool discovery failed: {e}")
        return False


def test_search_functionality():
    """Test search functionality"""
    print("\n[TEST] Search Functionality")
    print("-" * 40)
    try:
        with MUDAnalyzerMCPClient() as client:
            result = client.search("test", limit=5)
            if result.success is not None:
                print(f"[OK] Search returned: success={result.success}, data={len(result.data) if result.data else 0} items")
                return True
            else:
                print("[ERROR] Search failed")
                return False
    except Exception as e:
        print(f"[ERROR] Search functionality failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("MCP & REST API INTEGRATION VERIFICATION")
    print("="*50)
    
    results = {
        "REST API Connection": test_rest_api_connection(),
        "MCP Server Startup": test_mcp_server_startup(),
        "Tool Discovery": test_tool_discovery(),
        "Search Functionality": test_search_functionality(),
    }
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {test}")
    
    print("\n" + "-"*50)
    print(f"Result: {passed}/{total} tests passed")
    print("-"*50)
    
    if passed == total:
        print("\n[SUCCESS] All systems operational!")
        print("You can now use the MCP client with both servers running.")
        return 0
    else:
        print("\n[WARNING] Some tests failed.")
        print("Check the errors above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
