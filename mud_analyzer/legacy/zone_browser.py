#!/usr/bin/env python3
"""
Zone Browser - Refactored version using base classes
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for package imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mud_analyzer.base_explorer import BaseExplorer, MenuMixin
from mud_analyzer.data_service import data_service
from mud_analyzer.legacy.zone_explorer import ZoneExplorer


class ZoneBrowser(BaseExplorer, MenuMixin):
    """Refactored zone browser using unified data service"""
    
    def __init__(self):
        super().__init__()
        self._zones: List[Dict[str, Any]] = []
        self._loaded = False
    
    def get_items(self) -> List[Dict[str, Any]]:
        """Get zone items"""
        if not self._loaded:
            self._load_zones()
        return self._zones
    
    def _load_zones(self) -> None:
        """Load zone information"""
        print("Loading zone information...")
        
        self._zones = []
        for zone_num in data_service.zones:
            zone_data = data_service.world.load_zone(zone_num)
            if zone_data:
                self._zones.append({
                    'zone_num': zone_num,
                    'name': zone_data.get("name", "Unnamed Zone"),
                    'author': zone_data.get("author", "Unknown"),
                    'lifespan': zone_data.get('lifespan', 'Unknown'),
                    'reset_mode': zone_data.get('reset_mode', 'Unknown'),
                    'top': zone_data.get('top', 'Unknown')
                })
        
        self._zones.sort(key=lambda x: x['zone_num'])
        self._loaded = True
        print(f"Loaded {len(self._zones)} zones")
    
    def format_item(self, item: Dict[str, Any]) -> str:
        """Format zone for display"""
        zone_num = item['zone_num']
        name = item['name']
        author = item['author']
        
        # Truncate long names for better formatting
        if len(name) > 40:
            name = name[:37] + "..."
        
        return f"[{zone_num:4d}] {name:<40} by {author}"
    
    def show_item_details(self, item: Dict[str, Any]) -> None:
        """Show zone details and launch zone explorer"""
        zone_num = item['zone_num']
        
        while True:
            print(f"\n🌍 ZONE {zone_num} DETAILS")
            print("=" * 60)
            print(f"📋 Name: {item['name']}")
            print(f"👤 Author: {item['author']}")
            print(f"⏱️ Lifespan: {item['lifespan']}")
            print(f"🔄 Reset Mode: {item['reset_mode']}")
            print(f"🔢 Top VNUM: {item['top']}")
            
            # Count entities in zone
            self._show_zone_statistics(zone_num)
            
            print("\n" + "=" * 60)
            print("1. 🏰 Explore this zone")
            print("0. ← Back to zone list")
            
            choice = input("\n➤ Select option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self._explore_zone(zone_num)
            else:
                print("❌ Invalid choice!")
                input("Press Enter to continue...")
    
    def _show_zone_statistics(self, zone_num: int) -> None:
        """Show zone entity statistics"""
        zone_dir = data_service.world.root / str(zone_num)
        if not zone_dir.exists():
            print("\n❌ Zone directory not found!")
            return
        
        print(f"\n📊 Zone Statistics:")
        counts = {}
        for subdir in ["room", "mobile", "object", "script", "assemble"]:
            path = zone_dir / subdir
            if path.exists():
                counts[subdir] = len([f for f in path.iterdir() if f.is_file() and f.suffix == ".json"])
            else:
                counts[subdir] = 0
        
        icons = {
            'room': '🏠',
            'mobile': '👹', 
            'object': '📦',
            'script': '📜',
            'assemble': '🔧'
        }
        
        for entity_type, count in counts.items():
            icon = icons.get(entity_type, '📄')
            print(f"   {icon} {entity_type.title()}s: {count}")
    
    def _explore_zone(self, zone_num: int) -> None:
        """Launch zone explorer for specific zone"""
        try:
            explorer = ZoneExplorer(zone_num)
            explorer.main_menu()
        except Exception as e:
            print(f"❌ Error exploring zone {zone_num}: {e}")
            input("Press Enter to continue...")
    
    def search_zones(self) -> None:
        """Search zones by name or author"""
        search_term = input("\n🔍 Enter zone name or author to search for: ").strip().lower()
        if not search_term:
            print("❌ No search term entered!")
            input("Press Enter to continue...")
            return
        
        zones = self.get_items()
        matches = []
        
        for zone in zones:
            name = zone['name'].lower()
            author = zone['author'].lower()
            if search_term in name or search_term in author:
                matches.append(zone)
        
        if matches:
            self.display_items(f"🔍 ZONE SEARCH RESULTS: '{search_term}'", matches)
        else:
            print(f"❌ No zones found matching '{search_term}'")
            input("Press Enter to continue...")
    
    def browse_by_author(self) -> None:
        """Browse zones grouped by author"""
        zones = self.get_items()
        
        # Group by author
        by_author = {}
        for zone in zones:
            author = zone['author']
            if author not in by_author:
                by_author[author] = []
            by_author[author].append(zone)
        
        # Show authors
        authors = sorted(by_author.keys())
        
        page = 0
        page_size = 15
        
        while True:
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(authors))
            
            print(f"\n👥 AUTHORS (Page {page + 1} of {(len(authors) - 1) // page_size + 1})")
            print("=" * 60)
            
            for i, author in enumerate(authors[start_idx:end_idx], 1):
                zone_count = len(by_author[author])
                print(f"{i:2d}. {author} ({zone_count} zones)")
            
            print("\n0. ← Back to main menu")
            if page > 0:
                print("p. ← Previous page")
            if end_idx < len(authors):
                print("n. → Next page")
            
            choice = input("\n➤ Select author number, n/p for pages, or 0: ").strip().lower()
            
            if choice == "0":
                break
            elif choice == "n" and end_idx < len(authors):
                page += 1
            elif choice == "p" and page > 0:
                page -= 1
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < (end_idx - start_idx):
                        author = authors[start_idx + idx]
                        author_zones = by_author[author]
                        self.display_items(f"🌍 ZONES BY {author}", author_zones)
                except ValueError:
                    print("❌ Invalid choice!")
                    input("Press Enter to continue...")
    
    def reload_data(self) -> None:
        """Reload zone data"""
        data_service.clear_cache()
        self._loaded = False
        self._zones = []
        print("✅ Zone data reloaded!")
        input("Press Enter to continue...")
    
    def main_menu(self) -> None:
        """Main menu for zone browser"""
        menu_options = {
            "1": ("🌍 Browse All Zones", lambda: self.display_items("🌍 ALL ZONES", self.get_items())),
            "2": ("🔍 Search Zones", self.search_zones),
            "3": ("👥 Browse by Author", self.browse_by_author),
            "4": ("🔄 Reload Data", self.reload_data),
            "0": ("← Back to Main Menu", lambda: None)
        }
        
        self.run_menu_loop("🌍 ZONE BROWSER", menu_options)


def main():
    browser = ZoneBrowser()
    browser.main_menu()


if __name__ == "__main__":
    main()