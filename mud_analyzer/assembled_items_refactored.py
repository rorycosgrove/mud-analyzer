#!/usr/bin/env python3
"""
Assembled Items Explorer - Refactored version using base classes
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import json

# Add parent directory to path for package imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mud_analyzer.base_explorer import BaseExplorer, MenuMixin
from mud_analyzer.data_service import data_service
from mud_analyzer.config import config
from mud_analyzer.error_handler import handle_errors, safe_int


class AssembledItemsExplorer(BaseExplorer, MenuMixin):
    """Refactored assembled items explorer"""
    
    def __init__(self):
        super().__init__()
        self._assembles: List[Dict[str, Any]] = []
        self._loaded = False
    
    def get_items(self) -> List[Dict[str, Any]]:
        """Get assembled items"""
        if not self._loaded:
            self._load_assembles()
        return self._assembles
    
    @handle_errors()
    def _load_assembles(self) -> None:
        """Load assembled items from all zones"""
        print("Loading assembled items...")
        
        self._assembles = []
        for zone_num in data_service.zones:
            assemble_dir = config.project_root / str(zone_num) / "assemble"
            if not assemble_dir.exists():
                continue
            
            for assemble_file in assemble_dir.iterdir():
                if assemble_file.suffix != ".json":
                    continue
                
                try:
                    with open(assemble_file, 'r') as f:
                        assemble_data = json.load(f)
                    
                    result_vnum = safe_int(assemble_data.get('vnum', 0))
                    parts = assemble_data.get('parts', [])
                    
                    if result_vnum > 0 and parts:
                        self._assembles.append({
                            'zone': zone_num,
                            'result_vnum': result_vnum,
                            'parts': [safe_int(p) for p in parts if safe_int(p) > 0],
                            'cmds': assemble_data.get('cmd', []),
                            'keywords': assemble_data.get('keywords', []),
                            'name': data_service.world.obj_brief(result_vnum)
                        })
                except Exception:
                    continue
        
        self._assembles.sort(key=lambda x: (x['zone'], x['result_vnum']))
        self._loaded = True
        print(f"Loaded {len(self._assembles)} assembled items")
    
    def format_item(self, item: Dict[str, Any]) -> str:
        """Format assembled item for display"""
        accessibility = self._analyze_accessibility(item)
        
        if accessibility['all_parts_loadable']:
            status = "✅" if accessibility['overall_rate'] >= 100 else f"⚠️ {accessibility['overall_rate']:.0f}%"
        else:
            status = "❌"
        
        name = item['name']
        if len(name) > 50:
            name = name[:47] + "..."
        
        return f"{status:8} [Z{item['zone']:3d}] {name:<50} ({len(item['parts'])} parts)"
    
    def show_item_details(self, item: Dict[str, Any]) -> None:
        """Show detailed assembled item information"""
        while True:
            print(f"\n🔧 ASSEMBLED ITEM DETAILS")
            print("=" * 80)
            print(f"📦 Result Item: {item['name']}")
            print(f"🏠 Zone: {item['zone']}")
            
            accessibility = self._analyze_accessibility(item)
            self._display_accessibility_status(accessibility)
            
            if item['cmds']:
                print(f"⚡ Commands: {', '.join(str(x) for x in item['cmds'])}")
            if item['keywords']:
                print(f"🔑 Keywords: {', '.join(str(x) for x in item['keywords'])}")
            
            print(f"\n📋 REQUIRED PARTS ({len(item['parts'])} items)")
            print("-" * 80)
            
            for i, part_vnum in enumerate(item['parts'], 1):
                part_brief = data_service.world.obj_brief(part_vnum)
                locations = data_service.get_load_locations(part_vnum)
                
                status = "✅" if locations else "❌"
                print(f"\n{i:2d}. {status} {part_brief}")
                
                if locations:
                    best_prob = max(loc['probability'] for loc in locations)
                    print(f"    📊 Best Load Rate: {best_prob}%")
                    print("    📍 Load Locations:")
                    for j, loc in enumerate(locations[:3], 1):
                        print(f"       {j}. {loc['location']} ({loc['probability']}%)")
                    if len(locations) > 3:
                        print(f"       ... and {len(locations) - 3} more locations")
                else:
                    print("    ❌ No load locations found!")
            
            print("\n" + "=" * 80)
            print("0. ← Back to list")
            print("d. 🐛 Debug missing parts")
            choice = input("➤ Press 0 to return or d for debug: ").strip().lower()
            if choice == "0" or not choice:
                break
            elif choice == "d":
                self._debug_missing_parts(item)
    
    def _debug_missing_parts(self, item: Dict[str, Any]) -> None:
        """Debug missing parts for assembled item"""
        print(f"\n🐛 DEBUG: Investigating missing parts for {item['name']}")
        command_index = data_service.get_command_index()
        
        for part_vnum in item['parts']:
            print(f"\nPart {part_vnum}:")
            commands = command_index.get(part_vnum, [])
            if not commands:
                print("  No commands found in index")
                # Check raw zone data
                for zone_num in data_service.zones:
                    zone_data = data_service.world.load_zone(zone_num)
                    if zone_data and "cmds" in zone_data:
                        for cmd in zone_data["cmds"]:
                            if isinstance(cmd, dict) and safe_int(cmd.get("arg1", 0)) == part_vnum:
                                print(f"  Found in zone {zone_num}: {cmd}")
            else:
                for cmd in commands:
                    print(f"  {cmd}")
        input("\nPress Enter to continue...")
    
    def _analyze_accessibility(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze if assembled item can be created"""
        analysis = {
            'all_parts_loadable': True,
            'overall_rate': 100.0,
            'parts': {}
        }
        
        for part_vnum in item['parts']:
            locations = data_service.get_load_locations(part_vnum)
            
            if not locations:
                analysis['all_parts_loadable'] = False
                analysis['overall_rate'] = 0.0
            else:
                best_rate = max(loc['probability'] for loc in locations)
                if best_rate < 100:
                    analysis['overall_rate'] *= (best_rate / 100.0)
        
        return analysis
    
    def _display_accessibility_status(self, accessibility: Dict[str, Any]) -> None:
        """Display accessibility status"""
        print()
        if not accessibility['all_parts_loadable']:
            print("❌ STATUS: Assembly impossible - some parts cannot be loaded")
        elif accessibility['overall_rate'] >= 100:
            print("✅ STATUS: All parts guaranteed to load (100% success)")
        else:
            print(f"⚠️ STATUS: Possible assembly (Overall success rate: {accessibility['overall_rate']:.1f}%)")
    
    def _get_searchable_text(self, item: Dict[str, Any]) -> str:
        """Get searchable text for assembled items"""
        return item['name']
    
    def browse_possible_items(self) -> None:
        """Browse items that can be assembled"""
        items = self.get_items()
        possible_items = [
            item for item in items
            if self._analyze_accessibility(item)['all_parts_loadable']
        ]
        
        print(f"Found {len(possible_items)} possible items out of {len(items)}")
        self.display_items("🔧 POSSIBLE ASSEMBLED ITEMS", possible_items)
    
    def browse_impossible_items(self) -> None:
        """Browse items that cannot be assembled"""
        items = self.get_items()
        impossible_items = [
            item for item in items
            if not self._analyze_accessibility(item)['all_parts_loadable']
        ]
        
        print(f"Found {len(impossible_items)} impossible items out of {len(items)}")
        self.display_items("🔧 IMPOSSIBLE ASSEMBLED ITEMS", impossible_items)
    
    def browse_all_items(self) -> None:
        """Browse all assembled items"""
        items = self.get_items()
        self.display_items("🔧 ALL ASSEMBLED ITEMS", items)
    
    def search_items_menu(self) -> None:
        """Search assembled items"""
        items = self.get_items()
        matches = self.search_items(items, "item name")
        if matches:
            self.display_items("🔍 SEARCH RESULTS", matches)
    
    def find_by_part(self) -> None:
        """Find items by part name"""
        part_name = input("\n📦 Enter part name to search for: ").strip().lower()
        if not part_name:
            print("❌ No part name entered!")
            input("Press Enter to continue...")
            return
        
        items = self.get_items()
        matches = []
        
        for item in items:
            for part_vnum in item['parts']:
                part_brief = data_service.world.obj_brief(part_vnum).lower()
                if part_name in part_brief:
                    matches.append(item)
                    break
        
        if matches:
            self.display_items(f"🔍 ITEMS USING PART '{part_name}'", matches)
        else:
            print(f"❌ No items found using part '{part_name}'")
            input("Press Enter to continue...")
    
    def reload_data(self) -> None:
        """Reload all data"""
        data_service.clear_cache()
        self._loaded = False
        self._assembles = []
        print("✅ Data reloaded!")
        input("Press Enter to continue...")
    
    def main_menu(self) -> None:
        """Main menu for assembled items explorer"""
        menu_options = {
            "1": ("✅ Browse Possible Items", self.browse_possible_items),
            "2": ("❌ Browse Impossible Items", self.browse_impossible_items),
            "3": ("📋 Browse All Items", self.browse_all_items),
            "4": ("🔍 Search Items", self.search_items_menu),
            "5": ("📦 Find Items by Part", self.find_by_part),
            "6": ("🔄 Reload Data", self.reload_data),
            "0": ("← Back to Main Menu", lambda: None)
        }
        
        self.run_menu_loop("🔧 ASSEMBLED ITEMS EXPLORER", menu_options)


def main():
    explorer = AssembledItemsExplorer()
    explorer.main_menu()


if __name__ == "__main__":
    main()