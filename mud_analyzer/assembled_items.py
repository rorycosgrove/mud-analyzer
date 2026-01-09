#!/usr/bin/env python3
"""
Assembled Items Explorer - Explore assembled items and their loading methods
"""

import sys
from pathlib import Path
import json

# Add parent directory to path for package imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mud_analyzer.core.world_lookup import World
from mud_analyzer.config import config
from mud_analyzer.cache_manager import cache_manager
from mud_analyzer.performance import ProgressIndicator
from mud_analyzer.error_handler import handle_errors, safe_int


class AssembledItemsExplorer:
    def __init__(self):
        config.setup_working_directory()
        self.world = World(config.project_root)
        self.zones = self.get_available_zones()
        self.assembles = []
        self._accessibility_cache = {}
        self._zone_command_index = None  # Global command index for fast lookups
        self._part_cache = {}  # Cache for part analysis results
    
    def get_available_zones(self):
        zones = []
        for d in config.project_root.iterdir():
            if d.is_dir() and d.name.isdigit():
                zones.append(int(d.name))
        return sorted(zones)
    
    @handle_errors()
    def load_all_assembles(self):
        """Load all assemble recipes from all zones"""
        # Try to load from cache first
        cached_data = cache_manager.load_from_cache("assembled_items")
        if cached_data is not None:
            self.assembles = cached_data['assembles']
            self._accessibility_cache = cached_data.get('accessibility', {})
            self._zone_command_index = cached_data.get('command_index')
            self._part_cache = cached_data.get('part_cache', {})
            print(f"✅ Loaded {len(self.assembles)} assembled items from cache")
            return
        
        print("Loading assembled items from all zones...")
        
        self.assembles = []
        for zone_num in self.zones:
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
                    cmds = assemble_data.get('cmd', [])
                    keywords = assemble_data.get('keywords', [])
                    
                    if result_vnum > 0 and parts:
                        self.assembles.append({
                            'zone': zone_num,
                            'file': assemble_file.stem,
                            'result_vnum': result_vnum,
                            'parts': [safe_int(p) for p in parts if safe_int(p) > 0],
                            'cmds': cmds,
                            'keywords': keywords
                        })
                except Exception:
                    continue
        
        print(f"Loaded {len(self.assembles)} assembled items")
        
        # Sort by zone then by result vnum
        self.assembles.sort(key=lambda x: (x['zone'], x['result_vnum']))
        
        # Save to cache
        cache_data = {
            'assembles': self.assembles,
            'accessibility': self._accessibility_cache,
            'command_index': self._zone_command_index,
            'part_cache': self._part_cache
        }
        cache_manager.save_to_cache("assembled_items", cache_data)
    
    def main_menu(self):
        while True:
            print(f"\n🔧 ASSEMBLED ITEMS EXPLORER")
            print("=" * 50)
            print("1. ✅ Browse Possible Items")
            print("2. ❌ Browse Impossible Items")
            print("3. 📋 Browse All Items")
            print("4. 🔍 Search Items")
            print("5. 📦 Find Items by Part")
            print("6. 🔄 Reload Data")
            print("0. ← Back to Main Menu")
            
            choice = input("\n➤ Select option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.browse_possible_items()
            elif choice == "2":
                self.browse_impossible_items()
            elif choice == "3":
                self.browse_all_items()
            elif choice == "4":
                self.search_items()
            elif choice == "5":
                self.find_by_part()
            elif choice == "6":
                cache_manager.clear_cache("assembled_items")
                self._accessibility_cache = {}
                self._zone_command_index = None
                self._part_cache = {}
                self.load_all_assembles()
            else:
                print("❌ Invalid choice!")
                input("Press Enter to continue...")
    
    def browse_possible_items(self):
        """Browse only items that can be assembled"""
        self._ensure_assembles_loaded()
        
        print("Analyzing assembly possibilities...")
        possible_items = []
        for recipe in self.assembles:
            accessibility = self.analyze_accessibility(recipe)
            if accessibility['all_parts_loadable']:
                possible_items.append(recipe)
        
        print(f"Found {len(possible_items)} possible items out of {len(self.assembles)}")
        
        if not possible_items:
            print("❌ No possible assembled items found!")
            input("Press Enter to continue...")
            return
        
        self.display_filtered_items("POSSIBLE ASSEMBLED ITEMS", possible_items)
    
    def browse_impossible_items(self):
        """Browse only items that cannot be assembled"""
        self._ensure_assembles_loaded()
        
        print("Analyzing assembly impossibilities...")
        impossible_items = []
        for recipe in self.assembles:
            accessibility = self.analyze_accessibility(recipe)
            if not accessibility['all_parts_loadable']:
                impossible_items.append(recipe)
        
        print(f"Found {len(impossible_items)} impossible items out of {len(self.assembles)}")
        
        if not impossible_items:
            print("✅ All assembled items are possible to create!")
            input("Press Enter to continue...")
            return
        
        self.display_filtered_items("IMPOSSIBLE ASSEMBLED ITEMS", impossible_items)
    
    def display_filtered_items(self, title, items):
        """Display filtered list of items with pagination"""
        page = 0
        page_size = 12
        
        while True:
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(items))
            
            print(f"\n🔧 {title}")
            print(f"Page {page + 1} of {(len(items) - 1) // page_size + 1} | Total: {len(items)} items")
            print("=" * 80)
            
            for i, recipe in enumerate(items[start_idx:end_idx], 1):
                result_brief = self.world.obj_brief(recipe['result_vnum'])
                accessibility = self.analyze_accessibility(recipe)
                
                if accessibility['all_parts_loadable']:
                    if accessibility['overall_rate'] >= 100:
                        status = "✅"
                    else:
                        status = f"⚠️  {accessibility['overall_rate']:.0f}%"
                else:
                    status = "❌"
                
                # Truncate long names for better formatting
                if len(result_brief) > 50:
                    result_brief = result_brief[:47] + "..."
                
                print(f"{i:2d}. {status:8} [Z{recipe['zone']:3d}] {result_brief:<50} ({len(recipe['parts'])} parts)")
            
            print("\n" + "=" * 80)
            print("0. ← Back to menu")
            if page > 0:
                print("p. ← Previous page")
            if end_idx < len(items):
                print("n. → Next page")
            
            choice = input("\n➤ Select item number, n/p for pages, or 0: ").strip().lower()
            
            if choice == "0":
                break
            elif choice == "n" and end_idx < len(items):
                page += 1
            elif choice == "p" and page > 0:
                page -= 1
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < (end_idx - start_idx):
                        recipe = items[start_idx + idx]
                        self.show_item_details(recipe)
                except ValueError:
                    print("❌ Invalid choice!")
                    input("Press Enter to continue...")
    
    def browse_all_items(self):
        """Browse all assembled items with pagination"""
        self._ensure_assembles_loaded()
        
        if not self.assembles:
            print("❌ No assembled items found!")
            input("Press Enter to continue...")
            return
        
        self.display_filtered_items("ALL ASSEMBLED ITEMS", self.assembles)
    
    def search_items(self):
        """Search assembled items by name"""
        self._ensure_assembles_loaded()
        
        search_term = input("\n🔍 Enter item name to search for: ").strip().lower()
        if not search_term:
            print("❌ No search term entered!")
            input("Press Enter to continue...")
            return
        
        matches = []
        for recipe in self.assembles:
            result_brief = self.world.obj_brief(recipe['result_vnum']).lower()
            if search_term in result_brief:
                matches.append(recipe)
        
        if not matches:
            print(f"❌ No assembled items found matching '{search_term}'")
            input("Press Enter to continue...")
            return
        
        self.display_search_results(f"matching '{search_term}'", matches)
    
    def find_by_part(self):
        """Find assembled items that use a specific part"""
        self._ensure_assembles_loaded()
        
        part_name = input("\n📦 Enter part name to search for: ").strip().lower()
        if not part_name:
            print("❌ No part name entered!")
            input("Press Enter to continue...")
            return
        
        matches = []
        for recipe in self.assembles:
            for part_vnum in recipe['parts']:
                part_brief = self.world.obj_brief(part_vnum).lower()
                if part_name in part_brief:
                    matches.append(recipe)
                    break
        
        if not matches:
            print(f"❌ No assembled items found using part '{part_name}'")
            input("Press Enter to continue...")
            return
        
        self.display_search_results(f"using part '{part_name}'", matches)
    
    def display_search_results(self, search_desc, matches):
        """Display search results with pagination"""
        page = 0
        page_size = 10
        
        while True:
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(matches))
            
            print(f"\n🔍 SEARCH RESULTS: {search_desc}")
            print(f"Page {page + 1} of {(len(matches) - 1) // page_size + 1} | Found {len(matches)} matches")
            print("=" * 80)
            
            for i, recipe in enumerate(matches[start_idx:end_idx], 1):
                result_brief = self.world.obj_brief(recipe['result_vnum'])
                accessibility = self.analyze_accessibility(recipe)
                
                if accessibility['all_parts_loadable']:
                    if accessibility['overall_rate'] >= 100:
                        status = "✅"
                    else:
                        status = f"⚠️  {accessibility['overall_rate']:.0f}%"
                else:
                    status = "❌"
                
                # Truncate long names for better formatting
                if len(result_brief) > 50:
                    result_brief = result_brief[:47] + "..."
                
                print(f"{i:2d}. {status:8} [Z{recipe['zone']:3d}] {result_brief:<50} ({len(recipe['parts'])} parts)")
            
            print("\n" + "=" * 80)
            print("0. ← Back to menu")
            if page > 0:
                print("p. ← Previous page")
            if end_idx < len(matches):
                print("n. → Next page")
            
            choice = input("\n➤ Select item number, n/p for pages, or 0: ").strip().lower()
            
            if choice == "0":
                break
            elif choice == "n" and end_idx < len(matches):
                page += 1
            elif choice == "p" and page > 0:
                page -= 1
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < (end_idx - start_idx):
                        recipe = matches[start_idx + idx]
                        self.show_item_details(recipe)
                except ValueError:
                    print("❌ Invalid choice!")
                    input("Press Enter to continue...")
    
    def show_item_details(self, recipe):
        """Show detailed information about an assembled item"""
        while True:
            print(f"\n🔧 ASSEMBLED ITEM DETAILS")
            print("=" * 80)
            
            # Show result item
            result_brief = self.world.obj_brief(recipe['result_vnum'])
            print(f"📦 Result Item: {result_brief}")
            print(f"🏠 Zone: {recipe['zone']}")
            
            # Analyze accessibility and load rates
            accessibility = self.analyze_accessibility(recipe)
            
            print()
            if not accessibility['zone_accessible']:
                print("❌ STATUS: Zone not accessible")
            elif not accessibility['all_parts_loadable']:
                print("❌ STATUS: Assembly impossible - some parts cannot be loaded")
            elif accessibility['overall_rate'] >= 100:
                print("✅ STATUS: All parts guaranteed to load (100% success)")
            else:
                print(f"⚠️ STATUS: Possible assembly (Overall success rate: {accessibility['overall_rate']:.1f}%)")
            
            # Show commands and keywords
            if recipe['cmds']:
                print(f"⚡ Assembly Commands: {', '.join(str(x) for x in recipe['cmds'])}")
            if recipe['keywords']:
                print(f"🔑 Keywords: {', '.join(str(x) for x in recipe['keywords'])}")
            
            # Show parts with load analysis
            print(f"\n📋 REQUIRED PARTS ({len(recipe['parts'])} items)")
            print("-" * 80)
            
            for i, part_vnum in enumerate(recipe['parts'], 1):
                part_brief = self.world.obj_brief(part_vnum)
                part_info = accessibility['parts'][part_vnum]
                status = "✅" if part_info['loadable'] else "❌"
                
                print(f"\n{i:2d}. {status} {part_brief}")
                
                if part_info['best_rate'] > 0:
                    print(f"    📊 Best Load Rate: {part_info['best_rate']:.1f}%")
                
                # Show top locations
                if part_info['locations']:
                    print("    📍 Load Locations:")
                    for j, location in enumerate(part_info['locations'][:3], 1):
                        print(f"       {j}. {location}")
                    if len(part_info['locations']) > 3:
                        print(f"       ... and {len(part_info['locations']) - 3} more locations")
                else:
                    print("    ❌ No load locations found!")
            
            # Show alternative ways to get result
            result_locations = self._analyze_zone_for_part(recipe['zone'], recipe['result_vnum'])
            if result_locations:
                print(f"\n🎯 ALTERNATIVE SOURCES for {result_brief}")
                print("-" * 80)
                for i, (_, location) in enumerate(result_locations[:5], 1):
                    print(f"  {i}. {location}")
                if len(result_locations) > 5:
                    print(f"  ... and {len(result_locations) - 5} more sources")
            
            print("\n" + "=" * 80)
            print("0. ← Back to list")
            choice = input("➤ Press 0 to return: ").strip()
            if choice == "0" or not choice:
                break
    
    def analyze_accessibility(self, recipe):
        """Analyze if assembled item is possible to create"""
        cache_key = f"{recipe['zone']}_{recipe['result_vnum']}"
        if cache_key in self._accessibility_cache:
            return self._accessibility_cache[cache_key]
        
        analysis = {
            'zone_accessible': self.is_zone_accessible(recipe['zone']),
            'all_parts_loadable': True,
            'overall_rate': 100.0,
            'parts': {}
        }
        
        for part_vnum in recipe['parts']:
            part_analysis = self.analyze_part_loadability(part_vnum)
            analysis['parts'][part_vnum] = part_analysis
            
            if not part_analysis['loadable']:
                analysis['all_parts_loadable'] = False
                analysis['overall_rate'] = 0.0
            elif part_analysis['best_rate'] < 100:
                analysis['overall_rate'] *= (part_analysis['best_rate'] / 100.0)
        
        self._accessibility_cache[cache_key] = analysis
        return analysis
    
    def is_zone_accessible(self, zone_num):
        """Check if zone exists and has data"""
        zone_path = config.project_root / str(zone_num)
        return zone_path.exists() and zone_path.is_dir()
    
    def analyze_part_loadability(self, vnum):
        """Analyze where a part can be obtained using indexed data"""
        # Check cache first
        if vnum in self._part_cache:
            return self._part_cache[vnum]
        
        analysis = {
            'loadable': False,
            'best_rate': 0.0,
            'locations': []
        }
        
        locations_with_rates = []
        
        # Use indexed commands for fast lookup
        commands = self._zone_command_index.get(vnum, [])
        for cmd in commands:
            cmd_type = cmd['cmd_type']
            zone = cmd['zone']
            prob = cmd['prob']
            
            if cmd_type in ("O", "X"):  # Object in room
                room_brief = self.world.room_brief(cmd['arg3'])
                location = f"Zone {zone}: {room_brief} ({prob}%)"
                locations_with_rates.append((prob, location))
                
            elif cmd_type in ("E", "Z") and cmd['mobile_context']:  # Object equipped
                mob_brief = self.world.mob_brief(cmd['mobile_context'])
                location = f"Zone {zone}: {mob_brief} (equipped) ({prob}%)"
                locations_with_rates.append((prob, location))
                
            elif cmd_type in ("G", "Y") and cmd['mobile_context']:  # Object in inventory
                mob_brief = self.world.mob_brief(cmd['mobile_context'])
                location = f"Zone {zone}: {mob_brief} (inventory) ({prob}%)"
                locations_with_rates.append((prob, location))
                
            elif cmd_type in ("P", "Q"):  # Object in container
                container_brief = self.world.obj_brief(cmd['arg3'])
                location = f"Zone {zone}: in {container_brief} ({prob}%)"
                locations_with_rates.append((prob, location))
            
            elif cmd_type == "CONTAINS":  # Container receives this item
                item_brief = self.world.obj_brief(cmd['arg1'])
                location = f"Zone {zone}: Contains {item_brief} ({prob}%)"
                locations_with_rates.append((prob, location))
        
        # Check scripts that create this item
        script_locations = self._find_script_references(vnum)
        locations_with_rates.extend(script_locations)
        
        if locations_with_rates:
            analysis['loadable'] = True
            locations_with_rates.sort(key=lambda x: x[0], reverse=True)
            analysis['best_rate'] = locations_with_rates[0][0]
            analysis['locations'] = [loc for _, loc in locations_with_rates]
        
        # Cache the result
        self._part_cache[vnum] = analysis
        return analysis
    
    def _find_script_references(self, vnum):
        """Find scripts that create or reference this item"""
        script_locations = []
        
        for zone_num in self.zones:
            script_dir = config.project_root / str(zone_num) / "script"
            if not script_dir.exists():
                continue
            
            for script_file in script_dir.iterdir():
                if script_file.suffix != ".json":
                    continue
                
                try:
                    script_data = self.world.load("script", int(script_file.stem))
                    if not script_data:
                        continue
                    
                    code = script_data.get("code", "")
                    if not code or str(vnum) not in code:
                        continue
                    
                    # Analyze script code for item creation patterns
                    prob = self._analyze_script_creation_probability(code, vnum)
                    if prob > 0:
                        script_name = script_data.get("name", "Unnamed")
                        script_type = script_data.get("type", "Unknown")
                        location = f"Zone {zone_num}: Script '{script_name}' ({script_type}) creates item ({prob}%)"
                        script_locations.append((prob, location))
                
                except Exception:
                    continue
        
        return script_locations
    
    def _analyze_script_creation_probability(self, code, vnum):
        """Analyze script code to determine item creation probability"""
        vnum_str = str(vnum)
        
        # Check for direct object creation commands
        creation_patterns = [
            f"oload {vnum_str}",
            f"load obj {vnum_str}",
            f"create {vnum_str}",
            f"give {vnum_str}",
            f"drop {vnum_str}"
        ]
        
        for pattern in creation_patterns:
            if pattern in code.lower():
                # Check if it's in a conditional or loop
                if "if" in code.lower() or "random" in code.lower():
                    return 75  # Conditional creation
                else:
                    return 100  # Direct creation
        
        # Check for variable assignments or references
        if vnum_str in code:
            return 25  # Referenced but unclear creation method
        
        return 0
    
    def _build_zone_command_index(self):
        """Build comprehensive index of all zone commands for fast lookups"""
        if self._zone_command_index is not None:
            return
        
        print("Building zone command index for fast analysis...")
        self._zone_command_index = {}
        
        for zone_num in self.zones:
            zone_data = self.world.load_zone(zone_num)
            if not zone_data or "cmds" not in zone_data:
                continue
            
            current_mobile = None
            for cmd in zone_data["cmds"]:
                if not isinstance(cmd, dict):
                    continue
                
                cmd_type = cmd.get("cmd", "")
                arg1 = safe_int(cmd.get("arg1", 0))
                arg2 = safe_int(cmd.get("arg2", 0))
                arg3 = safe_int(cmd.get("arg3", 0))
                prob = safe_int(cmd.get("prob", 100))
                
                # Track mobile context
                if cmd_type == "M":
                    current_mobile = arg1
                
                # Index commands that load objects
                if cmd_type in ("O", "X", "E", "Z", "G", "Y", "P", "Q") and arg1 > 0:
                    if arg1 not in self._zone_command_index:
                        self._zone_command_index[arg1] = []
                    
                    self._zone_command_index[arg1].append({
                        'zone': zone_num,
                        'cmd_type': cmd_type,
                        'arg1': arg1,
                        'arg2': arg2,
                        'arg3': arg3,
                        'prob': prob,
                        'mobile_context': current_mobile if cmd_type in ('E', 'Z', 'G', 'Y') else None
                    })
                
                # Also index container contents (P/Q commands put arg1 into arg3)
                if cmd_type in ("P", "Q") and arg3 > 0:
                    if arg3 not in self._zone_command_index:
                        self._zone_command_index[arg3] = []
                    
                    self._zone_command_index[arg3].append({
                        'zone': zone_num,
                        'cmd_type': 'CONTAINS',
                        'arg1': arg1,  # What goes into the container
                        'arg2': arg2,
                        'arg3': arg3,  # The container
                        'prob': prob,
                        'mobile_context': None
                    })
        
    def _ensure_assembles_loaded(self):
        """Lazy load assembles with status updates"""
        if not self.assembles:
            print("Loading assembled items data...")
            self.load_all_assembles()
        
        # Build command index for fast analysis
        self._build_zone_command_index()
        """Lazy load assembles with status updates"""
        if not self.assembles:
            print("Loading assembled items data...")
            self.load_all_assembles()
    
    def _analyze_zone_for_part(self, zone_num, vnum):
        """Analyze a single zone for part loadability"""
        locations_with_rates = []
        
        if not self.is_zone_accessible(zone_num):
            return locations_with_rates
            
        zone_data = self.world.load_zone(zone_num)
        if not zone_data or "cmds" not in zone_data:
            return locations_with_rates
            
        current_mobile = None
        
        for cmd in zone_data["cmds"]:
            if not isinstance(cmd, dict):
                continue
            
            cmd_type = cmd.get("cmd", "")
            arg1 = safe_int(cmd.get("arg1", 0))
            arg2 = safe_int(cmd.get("arg2", 0))
            arg3 = safe_int(cmd.get("arg3", 0))
            prob = safe_int(cmd.get("prob", 100))
            
            # Track mobile loading
            if cmd_type == "M":
                current_mobile = arg1
            
            # Check if this command loads our item
            if arg1 == vnum:
                if cmd_type in ("O", "X"):  # Object in room
                    room_brief = self.world.room_brief(arg3)
                    location = f"Zone {zone_num}: {room_brief} ({prob}%)"
                    locations_with_rates.append((prob, location))
                    
                elif cmd_type in ("E", "Z") and current_mobile:  # Object equipped on mobile
                    mob_brief = self.world.mob_brief(current_mobile)
                    location = f"Zone {zone_num}: {mob_brief} (equipped) ({prob}%)"
                    locations_with_rates.append((prob, location))
                    
                elif cmd_type in ("G", "Y") and current_mobile:  # Object given to mobile
                    mob_brief = self.world.mob_brief(current_mobile)
                    location = f"Zone {zone_num}: {mob_brief} (inventory) ({prob}%)"
                    locations_with_rates.append((prob, location))
                    
                elif cmd_type in ("P", "Q"):  # Object in container
                    container_brief = self.world.obj_brief(arg3)
                    location = f"Zone {zone_num}: in {container_brief} ({prob}%)"
                    locations_with_rates.append((prob, location))
        
        return locations_with_rates
    

def main():
    explorer = AssembledItemsExplorer()
    explorer.main_menu()


if __name__ == "__main__":
    main()