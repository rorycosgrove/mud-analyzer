#!/usr/bin/env python3
"""
MUD Analyzer - Main Menu System
"""

import sys
from pathlib import Path
import os

# Add parent directory to path for package imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mud_analyzer.shared.config import config
from mud_analyzer.shared.error_handler import handle_errors, log_error


class MudAnalyzerMenu:
    def __init__(self):
        try:
            config.setup_working_directory()
        except Exception as e:
            log_error(f"Failed to setup working directory: {e}")
            raise
    
    def show_header(self):
        print(f"\n{'='*60}")
        print("🏰 MUD ANALYZER - AddictMUD Zone Analysis Tools")
        print(f"{'='*60}")
    
    @handle_errors(show_traceback=False)
    def main_menu(self):
        while True:
            try:
                self.show_header()
                print("\n📋 MAIN MENU")
                print("1. 🔍 Global Search (Objects & Mobiles)")
                print("2. 🌍 Zone Browser (List All Zones)")
                print("3. 🏰 Zone Explorer (Explore Specific Zone)")
                print("4. 📊 Zone Summary (Generate Report)")
                print("5. 🔧 Assembled Items Explorer")
                print("6. 🧪 Test Spell Loading")
                print("7. 📚 Help & Documentation")
                print("8. 🗑️ Clear All Caches")
                print("0. 🚪 Exit")
                
                choice = input("\n➤ Select option: ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    self.launch_global_search()
                elif choice == "2":
                    self.launch_zone_browser()
                elif choice == "3":
                    self.launch_zone_explorer()
                elif choice == "4":
                    self.launch_zone_summary()
                elif choice == "5":
                    self.launch_assembled_items()
                elif choice == "6":
                    self.launch_spell_test()
                elif choice == "7":
                    self.launch_help_system()
                elif choice == "8":
                    self.clear_all_caches()
                else:
                    print("❌ Invalid choice! Please select 0-8.")
                    input("Press Enter to continue...")
            except KeyboardInterrupt:
                print("\n⚠️ Returning to menu...")
            except Exception as e:
                log_error(f"Menu error: {e}")
                input("Press Enter to continue...")
    
    def launch_global_search(self):
        try:
            from mud_analyzer.legacy.global_search import GlobalSearch
            search = GlobalSearch()
            search.main_menu()
        except Exception as e:
            print(f"❌ Error launching global search: {e}")
            input("Press Enter to continue...")
    
    def launch_zone_browser(self):
        try:
            from mud_analyzer.legacy.zone_browser import ZoneBrowser
            browser = ZoneBrowser()
            browser.main_menu()
        except Exception as e:
            print(f"❌ Error launching zone browser: {e}")
            input("Press Enter to continue...")
    
    def launch_zone_explorer(self):
        while True:
            zone_num = input("\n🏰 Enter zone number to explore (or 'back' to return): ").strip()
            if zone_num.lower() in ['back', 'b', '']:
                return
            
            try:
                zone_num = int(zone_num)
                from mud_analyzer.legacy.zone_explorer import ZoneExplorer
                explorer = ZoneExplorer(zone_num)
                explorer.main_menu()
                break
            except ValueError:
                print("❌ Zone number must be an integer!")
            except Exception as e:
                log_error(f"Error launching zone explorer: {e}")
                input("Press Enter to continue...")
                break
    
    def launch_zone_summary(self):
        while True:
            zone_num = input("\n📊 Enter zone number for summary (or 'back' to return): ").strip()
            if zone_num.lower() in ['back', 'b', '']:
                return
            
            try:
                zone_num_int = int(zone_num)
                # Set up args for zone_summary
                sys.argv = ["zone_summary.py", zone_num]
                from mud_analyzer.analysis.zone_summary import main as summary_main
                summary_main()
                break
            except ValueError:
                print("❌ Zone number must be an integer!")
            except Exception as e:
                log_error(f"Error generating zone summary: {e}")
                input("Press Enter to continue...")
                break
    
    def launch_assembled_items(self):
        try:
            from mud_analyzer.legacy.assembled_items import AssembledItemsExplorer
            explorer = AssembledItemsExplorer()
            explorer.main_menu()
        except Exception as e:
            print(f"❌ Error launching assembled items explorer: {e}")
            input("Press Enter to continue...")
    
    def launch_spell_test(self):
        try:
            from mud_analyzer.test_spells import test_spell_loading
            test_spell_loading()
        except Exception as e:
            print(f"❌ Error testing spells: {e}")
        input("Press Enter to continue...")
    
    def launch_help_system(self):
        try:
            from mud_analyzer.help_system import HelpSystem
            help_system = HelpSystem()
            help_system.show_main_help()
        except Exception as e:
            print(f"❌ Error launching help system: {e}")
            input("Press Enter to continue...")
    
    def clear_all_caches(self):
        try:
            from mud_analyzer.data_service import data_service
            from mud_analyzer.cache_manager import cache_manager
            
            # Show cache stats before clearing
            stats = cache_manager.get_cache_stats()
            print(f"\n📊 Current cache status:")
            print(f"   Memory caches: {stats['memory_caches']}")
            print(f"   Disk caches: {stats['disk_caches']}")
            print(f"   Cache size: {stats['cache_dir_size'] / 1024 / 1024:.1f} MB")
            
            print("\n🗑️ Clearing all caches...")
            data_service.clear_cache()
            cache_manager.clear_cache()
            print("✅ All caches cleared successfully!")
            print("   Next data access will rebuild caches automatically.")
        except Exception as e:
            print(f"❌ Error clearing caches: {e}")
        input("Press Enter to continue...")


@handle_errors(show_traceback=False)
def main():
    try:
        menu = MudAnalyzerMenu()
        menu.main_menu()
    except KeyboardInterrupt:
        print("\n⚠️ Goodbye!")
    except Exception as e:
        log_error(f"Fatal error: {e}", e)


if __name__ == "__main__":
    main()