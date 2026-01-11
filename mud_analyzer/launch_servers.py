#!/usr/bin/env python3
"""
MUD Analyzer Server Launcher
Manages starting REST API and MCP servers with proper process management
"""

import sys
import os
import subprocess
import signal
import time
import argparse
from pathlib import Path
from typing import Optional, List

class ServerManager:
    """Manages API and MCP server processes"""
    
    def __init__(self):
        self.rest_process: Optional[subprocess.Popen] = None
        self.mcp_process: Optional[subprocess.Popen] = None
        # Run from parent directory so imports work correctly
        self.project_root = Path(__file__).parent.parent
        self.mud_analyzer_dir = Path(__file__).parent
        
    def start_rest_api(self, host: str = "127.0.0.1", port: int = 8000) -> bool:
        """Start REST API server"""
        try:
            print(f"\n🚀 Starting REST API server on {host}:{port}...")
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            
            # Run from parent directory so module imports work
            self.rest_process = subprocess.Popen(
                [sys.executable, str(self.mud_analyzer_dir / "api" / "rest_server.py")],
                cwd=str(self.project_root),  # Set working directory to parent
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr into stdout
                text=True,
                bufsize=1
            )
            
            # Give server time to start
            time.sleep(2)
            
            if self.rest_process.poll() is None:
                print(f"✅ REST API server started (PID: {self.rest_process.pid})")
                print(f"   📍 OpenAPI Docs: http://{host}:{port}/docs")
                print(f"   📍 API Root: http://{host}:{port}/")
                return True
            else:
                # Server failed to start, show error output
                stdout, _ = self.rest_process.communicate(timeout=1)
                print("❌ Failed to start REST API server")
                if stdout:
                    print("Error output:")
                    print(stdout[:500])  # Show first 500 chars of error
                return False
                
        except Exception as e:
            print(f"❌ Error starting REST API: {e}")
            return False
    
    def start_mcp_server(self) -> bool:
        """Start MCP server"""
        try:
            print(f"\n🚀 Starting MCP server...")
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            
            # Run from parent directory so module imports work
            self.mcp_process = subprocess.Popen(
                [sys.executable, str(self.mud_analyzer_dir / "api" / "mcp_server.py")],
                cwd=str(self.project_root),  # Set working directory to parent
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr into stdout
                text=True,
                bufsize=1
            )
            
            # Give server time to start
            time.sleep(2)
            
            # Check if process exited immediately (likely due to missing mcp package)
            returncode = self.mcp_process.poll()
            if returncode is not None:
                # Server exited, read output to see why
                try:
                    stdout, _ = self.mcp_process.communicate(timeout=0.5)
                except subprocess.TimeoutExpired:
                    stdout = ""
                
                # Check if it's a missing mcp package error
                if "No module named 'mcp'" in stdout or "mcp" in stdout.lower():
                    print("⚠️  MCP server unavailable - 'mcp' package not installed")
                    print("    To enable: pip install mcp")
                    print("    REST API will still be available")
                    return False
                else:
                    print("❌ Failed to start MCP server")
                    if stdout:
                        lines = stdout.split('\n')
                        for line in lines[:10]:  # Show first 10 lines
                            if line.strip():
                                print(f"    {line}")
                    return False
            else:
                print(f"✅ MCP server started (PID: {self.mcp_process.pid})")
                print(f"   📍 Ready for LLM integration via stdio")
                return True
                
        except Exception as e:
            print(f"⚠️  Error starting MCP server: {e}")
            print("    REST API will still be available")
            return False
    
    def stop_rest_api(self) -> None:
        """Stop REST API server"""
        if self.rest_process and self.rest_process.poll() is None:
            try:
                print("\n🛑 Stopping REST API server...")
                self.rest_process.terminate()
                self.rest_process.wait(timeout=5)
                print("✅ REST API server stopped")
            except subprocess.TimeoutExpired:
                self.rest_process.kill()
                print("⚠️  Killed REST API server (forced)")
    
    def stop_mcp_server(self) -> None:
        """Stop MCP server"""
        if self.mcp_process and self.mcp_process.poll() is None:
            try:
                print("\n🛑 Stopping MCP server...")
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
                print("✅ MCP server stopped")
            except subprocess.TimeoutExpired:
                self.mcp_process.kill()
                print("⚠️  Killed MCP server (forced)")
    
    def stop_all(self) -> None:
        """Stop all servers"""
        self.stop_rest_api()
        self.stop_mcp_server()
    
    def check_health(self) -> None:
        """Check server health status"""
        rest_status = "✅ Running" if self.rest_process and self.rest_process.poll() is None else "❌ Stopped"
        mcp_status = "✅ Running" if self.mcp_process and self.mcp_process.poll() is None else "❌ Stopped"
        
        print("\n📊 Server Status:")
        print(f"  REST API: {rest_status}")
        print(f"  MCP:      {mcp_status}")
    
    def run_all(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """Start and monitor all servers"""
        def signal_handler(sig, frame):
            print("\n\n⏸️  Received interrupt signal, shutting down...")
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print("\n" + "="*60)
        print("🏰 MUD ANALYZER SERVER LAUNCHER")
        print("="*60)
        
        # Start both servers
        rest_ok = self.start_rest_api(host, port)
        mcp_ok = self.start_mcp_server()
        
        if not (rest_ok or mcp_ok):
            print("\n❌ Failed to start any servers")
            sys.exit(1)
        
        print("\n" + "="*60)
        print("📡 SERVERS RUNNING")
        print("="*60)
        
        if rest_ok:
            print(f"\n✅ REST API available at http://{host}:{port}")
            print(f"   Try: curl http://{host}:{port}/api/zones")
        
        if mcp_ok:
            print(f"\n✅ MCP Server ready for LLM integration")
        
        print("\nPress Ctrl+C to stop all servers...\n")
        
        try:
            # Monitor processes
            while True:
                if self.rest_process and self.rest_process.poll() is not None:
                    print("⚠️  REST API server crashed, restarting...")
                    rest_ok = self.start_rest_api(host, port)
                
                if self.mcp_process and self.mcp_process.poll() is not None:
                    print("⚠️  MCP server crashed, restarting...")
                    mcp_ok = self.start_mcp_server()
                
                time.sleep(5)
        
        except KeyboardInterrupt:
            self.stop_all()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MUD Analyzer Server Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch_servers.py --all                 # Start both servers
  python launch_servers.py --rest               # Start only REST API
  python launch_servers.py --mcp                # Start only MCP
  python launch_servers.py --rest --port 8001   # REST on custom port
        """
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Start both REST API and MCP servers (default)"
    )
    parser.add_argument(
        "--rest",
        action="store_true",
        help="Start only REST API server"
    )
    parser.add_argument(
        "--mcp",
        action="store_true",
        help="Start only MCP server"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for REST API (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for REST API (default: 8000)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check server status only"
    )
    
    args = parser.parse_args()
    manager = ServerManager()
    
    if args.check:
        manager.check_health()
        return
    
    # Determine which servers to start
    start_rest = args.rest or args.all or (not args.rest and not args.mcp and not args.all)
    start_mcp = args.mcp or args.all
    
    # If only checking or specific server
    if args.rest and not args.mcp:
        manager.start_rest_api(args.host, args.port)
        try:
            while manager.rest_process and manager.rest_process.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop_rest_api()
    elif args.mcp and not args.rest:
        manager.start_mcp_server()
        try:
            while manager.mcp_process and manager.mcp_process.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop_mcp_server()
    else:
        # Run both servers
        manager.run_all(args.host, args.port)


if __name__ == "__main__":
    main()
