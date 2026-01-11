#!/usr/bin/env python3
"""
Main entry point for MUD Analyzer tools
"""

import sys
from pathlib import Path
import os

# Add parent directory to path for package imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mud_analyzer.shared.config import config
from mud_analyzer.shared.error_handler import handle_errors, log_error

@handle_errors(show_traceback=False)
def main():
    try:
        # Set working directory to project root where zone files are located
        config.setup_working_directory()
    except Exception as e:
        log_error(f"Failed to setup working directory: {e}")
        return
    
    if len(sys.argv) < 2:
        # Launch interactive menu if no arguments
        try:
            from mud_analyzer.legacy.menu import main as menu_main
            menu_main()
        except Exception as e:
            log_error(f"Failed to launch menu: {e}")
        return
    
    command = sys.argv[1].lower()
    
    if command == "menu":
        from mud_analyzer.legacy.menu import main as menu_main
        menu_main()
    elif command == "browse":
        try:
            from mud_analyzer.legacy.zone_browser import ZoneBrowser
            browser = ZoneBrowser()
            browser.main_menu()
        except Exception as e:
            log_error(f"Failed to launch zone browser: {e}")
    elif command == "search":
        try:
            from mud_analyzer.legacy.global_search import GlobalSearch
            search = GlobalSearch()
            search.main_menu()
        except Exception as e:
            log_error(f"Failed to launch global search: {e}")
    elif command == "summary":
        try:
            from mud_analyzer.analysis.zone_summary import main as zone_summary_main
            # Remove 'summary' from args and call zone_summary
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            zone_summary_main()
        except Exception as e:
            log_error(f"Failed to generate zone summary: {e}")
    elif command == "assembled":
        try:
            from mud_analyzer.assembled_items_refactored import AssembledItemsExplorer
            explorer = AssembledItemsExplorer()
            explorer.main_menu()
        except Exception as e:
            log_error(f"Failed to launch assembled items explorer: {e}")
    elif command == "explore":
        try:
            from mud_analyzer.legacy.zone_explorer import main as explorer_main
            # Remove 'explore' from args and call explorer
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            explorer_main()
        except Exception as e:
            log_error(f"Failed to launch zone explorer: {e}")
    elif command == "help" or command == "--help" or command == "-h":
        show_help()
    elif command == "clear-cache":
        try:
            from mud_analyzer.data_service import data_service
            from mud_analyzer.shared.cache_manager import cache_manager
            print("Clearing all caches...")
            data_service.clear_cache()
            cache_manager.clear_cache()
            print("✅ All caches cleared!")
        except Exception as e:
            log_error(f"Failed to clear cache: {e}")
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

def show_help():
    print("\n🏰 MUD Analyzer - AddictMUD Zone Analysis Tools")
    print("=" * 50)
    print("\nUsage: python mud_analyzer/main.py [command]")
    print("\nAvailable commands:")
    print("  menu       Launch interactive menu (default)")
    print("  browse     Browse zones")
    print("  search     Global search for objects/mobiles")
    print("  explore N  Explore specific zone N")
    print("  summary N  Generate summary for zone N")
    print("  assembled  Analyze assembled items")
    print("  help       Show this help message")
    print("  clear-cache Clear all caches")
    print("\nRun without arguments for interactive menu.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    except Exception as e:
        log_error(f"Unexpected error: {e}", e)
        sys.exit(1)