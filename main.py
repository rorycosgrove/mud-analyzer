#!/usr/bin/env python3
"""
Wrapper script for MUD Analyzer with world directory support.

Usage:
  python main.py                                    # Auto-detect world (current directory)
  python main.py --world /path/to/world             # Use specific world
  python main.py --world /path/to/world [command]   # Use specific world with command
"""

import sys
from pathlib import Path

def main():
    # Parse --world parameter if present
    world_dir = None
    argv = sys.argv[1:]  # Skip script name
    
    if len(argv) >= 2 and argv[0] == "--world":
        world_dir = argv[1]
        argv = argv[2:]  # Remove --world and its value from argv
        
        # Add world directory to sys.path
        world_path = Path(world_dir).resolve()
        if not world_path.exists():
            print(f"❌ Invalid world directory: {world_dir}")
            sys.exit(1)
        
        sys.path.insert(0, str(world_path))
    else:
        # Default: add current directory and parent to path
        sys.path.insert(0, str(Path.cwd()))
        sys.path.insert(0, str(Path(__file__).parent))
    
    # Now import mud_analyzer with the correct path set
    from mud_analyzer.legacy.main import main as legacy_main
    
    # Rebuild sys.argv for legacy main (script name + remaining args)
    sys.argv = [sys.argv[0]] + argv
    
    # Call legacy main
    legacy_main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
