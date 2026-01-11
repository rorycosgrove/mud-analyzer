#!/usr/bin/env python3
"""
Help System - Comprehensive help and documentation for MUD Analyzer
"""

import sys
from pathlib import Path

# Add parent directory to path for package imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mud_analyzer.shared.config import config


class HelpSystem:
    """Comprehensive help system for MUD Analyzer"""
    
    def __init__(self):
        config.setup_working_directory()
    
    def show_main_help(self):
        """Show main help menu"""
        while True:
            print(f"\n📚 MUD ANALYZER HELP SYSTEM")
            print("=" * 60)
            print("1. 🚀 Getting Started")
            print("2. 🔍 Global Search Help")
            print("3. 🌍 Zone Browser Help")
            print("4. 🏰 Zone Explorer Help")
            print("5. 🔧 Assembled Items Help")
            print("6. 📊 Zone Summary Help")
            print("7. 💡 Tips & Tricks")
            print("8. 🐛 Troubleshooting")
            print("9. 🔍 Project Status Check")
            print("0. ← Back to Main Menu")
            
            choice = input("\n➤ Select help topic: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.show_getting_started()
            elif choice == "2":
                self.show_global_search_help()
            elif choice == "3":
                self.show_zone_browser_help()
            elif choice == "4":
                self.show_zone_explorer_help()
            elif choice == "5":
                self.show_assembled_items_help()
            elif choice == "6":
                self.show_zone_summary_help()
            elif choice == "7":
                self.show_tips_and_tricks()
            elif choice == "8":
                self.show_troubleshooting()
            elif choice == "9":
                self.run_status_check()
            else:
                print("❌ Invalid choice!")
                input("Press Enter to continue...")
    
    def show_getting_started(self):
        """Show getting started guide"""
        print(f"\n🚀 GETTING STARTED WITH MUD ANALYZER")
        print("=" * 60)
        print("""
MUD Analyzer is a comprehensive tool for exploring AddictMUD world data.

📁 SETUP:
   • Place the analyzer in your AddictMUD world directory
   • The tool expects zone folders (numbered directories) containing:
     - room/     (room files)
     - mobile/   (mobile files) 
     - object/   (object files)
     - script/   (script files)
     - assemble/ (assembly recipes)

🎯 MAIN FEATURES:
   • Global Search: Find objects and mobiles across all zones
   • Zone Browser: Browse zones by name, author, or statistics
   • Zone Explorer: Deep dive into individual zones
   • Assembled Items: Analyze craftable items and requirements
   • Zone Summary: Generate detailed zone reports

🚀 QUICK START:
   1. Run 'python main.py' to start the interactive menu
   2. Choose option 2 (Zone Browser) to see available zones
   3. Select a zone to explore its contents
   4. Use Global Search to find specific items across zones

💡 TIP: All data is cached for faster subsequent access!
        """)
        input("\nPress Enter to continue...")
    
    def show_global_search_help(self):
        """Show global search help"""
        print(f"\n🔍 GLOBAL SEARCH HELP")
        print("=" * 60)
        print("""
Global Search allows you to find objects and mobiles across all zones.

🔍 SEARCH FEATURES:
   • Object Search: Find items by name or description
   • Mobile Search: Find creatures by name
   • Case-insensitive partial matching
   • Shows zone, VNUM, and basic info

📋 SEARCH RESULTS:
   • Paginated display (navigate with n/p)
   • Select items to view detailed information
   • Shows load locations and probabilities
   • Identifies where items can be found

🎯 DETAILED VIEW:
   • Complete item statistics and properties
   • Load locations grouped by type:
     🏠 Room loads
     👹 Mobile equipment
     🎒 Mobile inventory  
     📦 Container loads
   • Load probabilities for each location

💡 TIPS:
   • Use partial names for broader searches
   • Check load locations to find rare items
   • Rebuild index if data seems outdated
        """)
        input("\nPress Enter to continue...")
    
    def show_zone_browser_help(self):
        """Show zone browser help"""
        print(f"\n🌍 ZONE BROWSER HELP")
        print("=" * 60)
        print("""
Zone Browser helps you navigate and explore available zones.

🌍 BROWSING OPTIONS:
   • Browse All Zones: See complete zone list
   • Search Zones: Find zones by name or author
   • Browse by Author: Group zones by creator
   • Zone Statistics: Entity counts per zone

📊 ZONE INFORMATION:
   • Zone number and name
   • Author information
   • Reset settings (lifespan, mode)
   • Entity counts (rooms, mobiles, objects, etc.)

🏰 ZONE EXPLORATION:
   • Select any zone to launch Zone Explorer
   • View detailed zone statistics
   • Navigate directly to zone contents

💡 TIPS:
   • Use author browsing to find zones by specific builders
   • Check entity counts to find content-rich zones
   • Search by partial names for easier navigation
        """)
        input("\nPress Enter to continue...")
    
    def show_zone_explorer_help(self):
        """Show zone explorer help"""
        print(f"\n🏰 ZONE EXPLORER HELP")
        print("=" * 60)
        print("""
Zone Explorer provides detailed exploration of individual zones.

🏰 EXPLORATION FEATURES:
   • Zone Overview: Statistics and basic information
   • Room Browser: Navigate zone geography
   • Mobile Browser: Examine creatures and NPCs
   • Object Browser: View items and equipment
   • Script Browser: Analyze zone scripts
   • Assemble Browser: View crafting recipes

📋 ENTITY DETAILS:
   • Complete statistics and properties
   • Formatted display with all relevant data
   • Navigation between related entities
   • Spell and effect information

🔍 SEARCH WITHIN ZONE:
   • Find specific objects within the zone
   • Partial name matching
   • Quick access to detailed views

💡 TIPS:
   • Use overview to get zone layout understanding
   • Check scripts for special zone behaviors
   • Examine assembles for unique crafting opportunities
        """)
        input("\nPress Enter to continue...")
    
    def show_assembled_items_help(self):
        """Show assembled items help"""
        print(f"\n🔧 ASSEMBLED ITEMS HELP")
        print("=" * 60)
        print("""
Assembled Items Explorer analyzes craftable items and their requirements.

🔧 ANALYSIS FEATURES:
   • Possible Items: Items that can be crafted
   • Impossible Items: Items with missing components
   • Complete Item List: All assembly recipes
   • Part Search: Find items using specific components

✅ ACCESSIBILITY ANALYSIS:
   • ✅ Guaranteed: All parts load at 100%
   • ⚠️ Probable: Parts load with lower probability
   • ❌ Impossible: Some parts cannot be loaded

📦 DETAILED INFORMATION:
   • Result item statistics
   • Required components list
   • Load locations for each part
   • Overall success probability
   • Assembly commands and keywords

🔍 SEARCH OPTIONS:
   • Search by result item name
   • Find items requiring specific parts
   • Filter by accessibility status

💡 TIPS:
   • Focus on "Possible" items for viable crafting
   • Check part load locations for gathering routes
   • Use part search to find alternative recipes
        """)
        input("\nPress Enter to continue...")
    
    def show_zone_summary_help(self):
        """Show zone summary help"""
        print(f"\n📊 ZONE SUMMARY HELP")
        print("=" * 60)
        print("""
Zone Summary generates comprehensive reports for individual zones.

📊 REPORT CONTENTS:
   • Zone basic information (name, author, settings)
   • Entity counts and statistics
   • Room layout and connections
   • Mobile distribution and levels
   • Object types and properties
   • Script usage and triggers
   • Assembly recipes and complexity

📋 USAGE:
   • Run from main menu (option 4)
   • Enter zone number when prompted
   • Report displays in terminal
   • Comprehensive analysis of zone content

🎯 REPORT SECTIONS:
   • Header: Basic zone information
   • Statistics: Entity counts and distributions
   • Details: Specific entity information
   • Analysis: Patterns and notable features

💡 TIPS:
   • Use for zone documentation
   • Helpful for understanding zone complexity
   • Good for identifying content gaps
   • Useful for zone balancing analysis
        """)
        input("\nPress Enter to continue...")
    
    def show_tips_and_tricks(self):
        """Show tips and tricks"""
        print(f"\n💡 TIPS & TRICKS")
        print("=" * 60)
        print("""
🚀 PERFORMANCE TIPS:
   • Data is cached automatically for speed
   • Use "Reload Data" options to refresh cache
   • Large zones may take time to load initially

🔍 SEARCH STRATEGIES:
   • Use partial names for broader results
   • Try different spelling variations
   • Check both short and long descriptions

🎯 NAVIGATION TIPS:
   • Use 'n' and 'p' for page navigation
   • Press '0' to go back in any menu
   • Numbers select items from current page

📊 ANALYSIS WORKFLOW:
   1. Start with Zone Browser to get overview
   2. Use Global Search to find specific items
   3. Explore individual zones for details
   4. Check Assembled Items for crafting info

🔧 TROUBLESHOOTING:
   • If data seems wrong, try "Reload Data"
   • Check that you're in the correct directory
   • Ensure zone files are properly formatted JSON

💾 DATA MANAGEMENT:
   • Cache files stored in mud_analyzer/cache/
   • Safe to delete cache files if needed
   • Cache rebuilds automatically when cleared
        """)
        input("\nPress Enter to continue...")
    
    def show_troubleshooting(self):
        """Show troubleshooting guide"""
        print(f"\n🐛 TROUBLESHOOTING")
        print("=" * 60)
        print("""
❌ COMMON ISSUES AND SOLUTIONS:

🚫 "Zone not found" errors:
   • Check that you're in the correct directory
   • Ensure zone folders are numbered (e.g., "100", "200")
   • Verify zone.json files exist in zone directories

📁 "No data loaded" issues:
   • Use "Reload Data" options in menus
   • Check file permissions on zone directories
   • Ensure JSON files are properly formatted

🔍 Search returns no results:
   • Try partial names instead of full names
   • Check spelling and try variations
   • Use "Rebuild Search Index" option

⚡ Performance issues:
   • Clear cache files in mud_analyzer/cache/
   • Restart the application
   • Check available disk space

🔧 Assembly analysis problems:
   • Reload assembled items data
   • Check that zone command files exist
   • Verify object files are present

📊 Display formatting issues:
   • Ensure terminal width is at least 80 characters
   • Try different terminal applications
   • Check terminal encoding settings

🆘 GETTING HELP:
   • Check that all required files are present
   • Verify directory structure matches expectations
   • Try running individual modules directly for testing
        """)
        input("\nPress Enter to continue...")
    
    def run_status_check(self):
        """Run project status check"""
        try:
            from mud_analyzer.status_checker import ProjectStatusChecker
            checker = ProjectStatusChecker()
            checker.run_full_check()
        except Exception as e:
            print(f"❌ Error running status check: {e}")
            input("Press Enter to continue...")


def main():
    help_system = HelpSystem()
    help_system.show_main_help()


if __name__ == "__main__":
    main()