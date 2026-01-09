#!/usr/bin/env python3
"""
Zone Browser - Browse and select zones by name
"""

import sys
from pathlib import Path

# Add parent directory to path for package imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mud_analyzer.core.world_lookup import World
from mud_analyzer.zone_explorer import ZoneExplorer


class ZoneBrowser:
    def __init__(self, world_root=None):
        if world_root is None:
            world_root = Path.cwd()
        self.world = World(world_root)
        self.zones = self.load_all_zones(world_root)
    
    def load_all_zones(self, world_root):
        zones = []
        for d in world_root.iterdir():
            if not d.is_dir() or not d.name.isdigit():
                continue
            
            zone_num = int(d.name)
            zone_file = d / f"{zone_num}.json"
            
            if zone_file.exists():
                zone_data = self.world.load_zone(zone_num)
                if zone_data:
                    name = zone_data.get("name", "Unnamed Zone")
                    author = zone_data.get("author", "Unknown")
                    zones.append((zone_num, name, author))
        
        return sorted(zones, key=lambda x: x[0])
    
    def show_zone_list(self, page=0, page_size=15):
        start_idx = page * page_size
        end_idx = min(start_idx + page_size, len(self.zones))
        
        print(f"\n🌍 AVAILABLE ZONES (Page {page + 1}/{(len(self.zones) - 1) // page_size + 1})")
        print("=" * 70)
        
        for i, (zone_num, name, author) in enumerate(self.zones[start_idx:end_idx], 1):
            print(f"{i:2d}. [{zone_num:4d}] {name[:40]:<40} by {author}")
        
        print("\n0. 🚪 Exit")
        if page > 0:
            print("p. ← Previous page")
        if end_idx < len(self.zones):
            print("n. → Next page")
        
        return start_idx, end_idx
    
    def main_menu(self):
        page = 0
        page_size = 15
        
        while True:
            start_idx, end_idx = self.show_zone_list(page, page_size)
            
            choice = input("\n➤ Select zone number, n/p for pages, or 0 to exit: ").strip().lower()
            
            if choice == "0":
                break
            elif choice == "n" and end_idx < len(self.zones):
                page += 1
            elif choice == "p" and page > 0:
                page -= 1
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < (end_idx - start_idx):
                        zone_num = self.zones[start_idx + idx][0]
                        self.explore_zone(zone_num)
                except ValueError:
                    print("❌ Invalid choice!")
                    input("Press Enter to continue...")
    
    def explore_zone(self, zone_num):
        explorer = ZoneExplorer(zone_num)
        explorer.main_menu()


def main():
    browser = ZoneBrowser()
    browser.main_menu()


if __name__ == "__main__":
    main()