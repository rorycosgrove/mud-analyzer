#!/usr/bin/env python3
"""
Test MCP Server Connection
Diagnoses issues with MCP server connectivity
"""

import sys
import subprocess
import json
import time
from pathlib import Path


def test_server_path():
    """Test if server path exists"""
    print("🔍 Testing MCP server path...")
    
    possible_paths = [
        Path(__file__).parent / "mcp_server.py",
        Path(__file__).parent.parent / "mud_analyzer" / "api" / "mcp_server.py",
        Path.cwd() / "api" / "mcp_server.py",
        Path.cwd() / "mud_analyzer" / "api" / "mcp_server.py",
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"✅ Found MCP server at: {path}")
            return str(path)
        else:
            print(f"❌ Not found at: {path}")
    
    print("\n❌ MCP server not found in any expected location")
    return None


def test_server_startup(server_path):
    """Test if server can be started"""
    print(f"\n🚀 Testing server startup from: {server_path}")
    
    try:
        process = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        print("✅ Server process started")
        
        # Give server time to initialize
        time.sleep(1)
        
        # Test with a simple request
        test_request = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}
        
        try:
            request_json = json.dumps(test_request) + "\n"
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # Try to read response with timeout
            response_line = process.stdout.readline()
            
            if response_line:
                print(f"✅ Server responded with: {response_line[:100]}...")
                try:
                    response = json.loads(response_line)
                    print("✅ Response is valid JSON")
                    return True
                except json.JSONDecodeError as e:
                    print(f"❌ Response is not valid JSON: {e}")
                    return False
            else:
                # Check stderr for errors
                stderr_out = process.stderr.readline()
                if stderr_out:
                    print(f"❌ Server error: {stderr_out}")
                else:
                    print("❌ No response from server")
                return False
        
        finally:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
    
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False


def main():
    """Run diagnostics"""
    print("="*60)
    print("MCP SERVER CONNECTION DIAGNOSTICS")
    print("="*60)
    
    server_path = test_server_path()
    
    if not server_path:
        print("\n⚠️  MCP server not found. Please ensure it's in the expected location.")
        sys.exit(1)
    
    success = test_server_startup(server_path)
    
    print("\n" + "="*60)
    if success:
        print("✅ MCP Server is working correctly!")
        print("You can now run examples_mcp.py")
    else:
        print("❌ MCP Server has issues")
        print("Please check the MCP server implementation and try again")
    print("="*60)


if __name__ == "__main__":
    main()
