#!/usr/bin/env python3
"""
Global Search - Search objects and mobiles across all zones
"""

import sys
from pathlib import Path
import pickle
import time
import threading

# Add parent directory to path for package imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mud_analyzer.core.world_lookup import World
from mud_analyzer.analysis.identify_object import format_object_identify
from mud_analyzer.analysis.identify_mobile import format_mobile_identify
from mud_analyzer.utils.spell_lookup import load_spell_name_map
from mud_analyzer.config import config
from mud_analyzer.cache_manager import cache_manager
from mud_analyzer.error_handler import handle_errors, safe_int
from mud_analyzer.performance import ProgressIndicator, with_progress


class GlobalSearch:
    def __init__(self, world_root=None):
        if world_root is None:
            world_root = config.project_root
        self.world = World(world_root)
        self.spell_map = load_spell_name_map()
        self.zones = self.get_available_zones(world_root)
        self._object_cache = None
        self._mobile_cache = None
    
    def get_available_zones(self, world_root):
        zones = []
        for d in world_root.iterdir():
            if d.is_dir() and d.name.isdigit():
                zones.append(int(d.name))
        return sorted(zones)
    
    @handle_errors()
    def build_object_cache(self):
        """Build searchable cache of all objects"""
        if self._object_cache is not None:
            return
        
        # Try to load from cache manager
        cached_data = cache_manager.load_from_cache("objects")
        if cached_data is not None:
            self._object_cache = cached_data
            print(f"✅ Loaded {len(self._object_cache)} objects from cache")
            return
        
        progress = ProgressIndicator("Building object search index...")
        progress.start()
        
        self._object_cache = []
        
        for zone_num in self.zones:
            zone_dir = Path(str(zone_num)) / "object"
            if not zone_dir.exists():
                continue
            
            for obj_file in zone_dir.iterdir():
                if obj_file.suffix != ".json":
                    continue
                
                try:
                    vnum = safe_int(obj_file.stem)
                    if vnum <= 0:
                        continue
                    obj_data = self.world.load("object", vnum)
                    if obj_data:
                        short = obj_data.get("short_desc", "").lower()
                        name = obj_data.get("name", "").lower()
                        search_text = f"{short} {name}"
                        self._object_cache.append((zone_num, vnum, obj_data, search_text))
                except Exception:
                    continue
        
        # Save to cache manager
        cache_manager.save_to_cache("objects", self._object_cache)
        
        progress.stop()
        print(f"✅ Indexed {len(self._object_cache)} objects")
    
    def build_mobile_cache(self):
        """Build searchable cache of all mobiles"""
        if self._mobile_cache is not None:
            return
        
        # Try to load from cache manager
        cached_data = cache_manager.load_from_cache("mobiles")
        if cached_data is not None:
            self._mobile_cache = cached_data
            print(f"✅ Loaded {len(self._mobile_cache)} mobiles from cache")
            return
        
        progress = ProgressIndicator("Building mobile search index...")
        progress.start()
        
        self._mobile_cache = []
        
        for zone_num in self.zones:
            zone_dir = Path(str(zone_num)) / "mobile"
            if not zone_dir.exists():
                continue
            
            for mob_file in zone_dir.iterdir():
                if mob_file.suffix != ".json":
                    continue
                
                try:
                    vnum = safe_int(mob_file.stem)
                    if vnum <= 0:
                        continue
                    mob_data = self.world.load("mobile", vnum)
                    if mob_data:
                        short = mob_data.get("short_descr", "").lower()
                        name = mob_data.get("name", "").lower()
                        search_text = f"{short} {name}"
                        self._mobile_cache.append((zone_num, vnum, mob_data, search_text))
                except Exception:
                    continue
        
        # Save to cache manager
        cache_manager.save_to_cache("mobiles", self._mobile_cache)
        
        progress.stop()
        print(f"✅ Indexed {len(self._mobile_cache)} mobiles")
    
    def main_menu(self):
        while True:
            print(f"\n🔍 GLOBAL SEARCH")
            print("=" * 40)
            print("1. 📦 Search Objects")
            print("2. 👹 Search Mobiles")
            print("3. 🔧 Browse Assembles")
            print("4. 🔄 Rebuild Search Index")
            print("0. ← Back to Main Menu")
            
            choice = input("\n➤ Select option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.search_objects()
            elif choice == "2":
                self.search_mobiles()
            elif choice == "3":
                self.browse_assembles()
            elif choice == "4":
                self.rebuild_cache()
            else:
                print("❌ Invalid choice!")
                input("Press Enter to continue...")
    
    def rebuild_cache(self):
        """Force rebuild of search caches"""
        cache_manager.clear_cache("objects")
        cache_manager.clear_cache("mobiles")
        
        self._object_cache = None
        self._mobile_cache = None
        self.build_object_cache()
        self.build_mobile_cache()
        print("✅ Search index rebuilt!")
        input("Press Enter to continue...")
    
    def _is_cache_valid(self, cache_timestamp):
        """Check if cache is still valid (less than 1 hour old)"""
        return (time.time() - cache_timestamp) < config.cache_validity_seconds
    
    def search_objects(self):
        search_term = input("\n🔍 Enter object name to search for: ").strip().lower()
        if not search_term:
            print("❌ No search term entered!")
            input("Press Enter to continue...")
            return
        
        # Build cache if needed
        print("Preparing object search...")
        self.build_object_cache()
        
        # Fast search through cached data
        print(f"Searching {len(self._object_cache)} objects...")
        matches = []
        for zone_num, vnum, obj_data, search_text in self._object_cache:
            if search_term in search_text:
                matches.append((zone_num, vnum, obj_data))
        
        print(f"Found {len(matches)} matches")
        
        if not matches:
            print(f"❌ No objects found matching '{search_term}'")
            input("Press Enter to continue...")
            return
        
        self.display_object_results(search_term, matches)
    
    def search_mobiles(self):
        search_term = input("\n🔍 Enter mobile name to search for: ").strip().lower()
        if not search_term:
            print("❌ No search term entered!")
            input("Press Enter to continue...")
            return
        
        # Build cache if needed
        print("Preparing mobile search...")
        self.build_mobile_cache()
        
        # Fast search through cached data
        print(f"Searching {len(self._mobile_cache)} mobiles...")
        matches = []
        for zone_num, vnum, mob_data, search_text in self._mobile_cache:
            if search_term in search_text:
                matches.append((zone_num, vnum, mob_data))
        
        print(f"Found {len(matches)} matches")
        
        if not matches:
            print(f"❌ No mobiles found matching '{search_term}'")
            input("Press Enter to continue...")
            return
        
        self.display_mobile_results(search_term, matches)
    
    def display_object_results(self, search_term, matches):
        page = 0
        page_size = 10
        
        while True:
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(matches))
            
            print(f"\n📦 OBJECT SEARCH RESULTS: '{search_term}' (Page {page + 1}/{(len(matches) - 1) // page_size + 1})")
            print(f"Found {len(matches)} matches")
            print("-" * 60)
            
            for i, (zone_num, vnum, obj_data) in enumerate(matches[start_idx:end_idx], 1):
                short = obj_data.get("short_desc", "Unnamed")
                obj_type = obj_data.get("type_flag", "?")
                print(f"{i:2d}. [Zone {zone_num}] [{vnum}] {short} (Type {obj_type})")
            
            print("\n0. ← Back to search menu")
            if page > 0:
                print("p. ← Previous page")
            if end_idx < len(matches):
                print("n. → Next page")
            
            choice = input("\n➤ Select object number, n/p for pages, or 0: ").strip().lower()
            
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
                        zone_num, vnum, obj_data = matches[start_idx + idx]
                        self.show_object_details(zone_num, vnum, obj_data)
                except ValueError:
                    print("❌ Invalid choice!")
                    input("Press Enter to continue...")
    
    def display_mobile_results(self, search_term, matches):
        page = 0
        page_size = 10
        
        while True:
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(matches))
            
            print(f"\n👹 MOBILE SEARCH RESULTS: '{search_term}' (Page {page + 1}/{(len(matches) - 1) // page_size + 1})")
            print(f"Found {len(matches)} matches")
            print("-" * 60)
            
            for i, (zone_num, vnum, mob_data) in enumerate(matches[start_idx:end_idx], 1):
                short = mob_data.get("short_descr", "Unnamed")
                level = mob_data.get("level", "?")
                print(f"{i:2d}. [Zone {zone_num}] [{vnum}] {short} (Level {level})")
            
            print("\n0. ← Back to search menu")
            if page > 0:
                print("p. ← Previous page")
            if end_idx < len(matches):
                print("n. → Next page")
            
            choice = input("\n➤ Select mobile number, n/p for pages, or 0: ").strip().lower()
            
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
                        zone_num, vnum, mob_data = matches[start_idx + idx]
                        self.show_mobile_details(zone_num, vnum, mob_data)
                except ValueError:
                    print("❌ Invalid choice!")
                    input("Press Enter to continue...")
    
    def show_object_details(self, zone_num, vnum, obj_data):
        while True:
            print(f"\n📦 OBJECT [Zone {zone_num}] [{vnum}]")
            print("=" * 60)
            output = format_object_identify(obj_data, self.spell_map)
            print(output)
            
            # Show associated items
            self.show_associations("object", vnum)
            
            print("\n0. ← Back to search results")
            choice = input("➤ Press 0 to return: ").strip()
            if choice == "0" or not choice:
                break
    
    def show_mobile_details(self, zone_num, vnum, mob_data):
        while True:
            print(f"\n👹 MOBILE [Zone {zone_num}] [{vnum}]")
            print("=" * 60)
            output = format_mobile_identify(mob_data, self.world)
            print(output)
            
            # Show associated items
            self.show_associations("mobile", vnum)
            
            print("\n0. ← Back to search results")
            choice = input("➤ Press 0 to return: ").strip()
            if choice == "0" or not choice:
                break
    
    def show_associations(self, entity_type, vnum):
        """Find and display associated items across all zones"""
        print("\nFinding associations across all zones...")
        
        associations = self.find_associations(entity_type, vnum)
        
        if not associations:
            print("ℹ️ No associations found")
            return
        
        print(f"\n🔗 ASSOCIATIONS:")
        print("-" * 30)
        
        for assoc_type, items in associations.items():
            if items:
                print(f"\n{assoc_type}:")
                for item in items[:5]:  # Limit to 5 per type
                    print(f"  - {item}")
                if len(items) > 5:
                    print(f"  ... and {len(items) - 5} more")
    
    def find_associations(self, entity_type, vnum):
        """Find all associations for an entity across all zones"""
        associations = {
            "🏠 Loads in rooms": [],
            "👹 Carried by mobiles": [],
            "📦 Found in containers": [],
            "📦 Contains objects": [],
            "🔧 Crafted via recipes": [],
            "🔧 Used as recipe part": [],
            "📜 Referenced in scripts": [],
            "🎯 Load probability": []
        }
        
        # Track mobile context for equipment/inventory
        current_mobile = None
        
        for zone_num in self.zones:
            # Check zone resets
            zone_data = self.world.load_zone(zone_num)
            if zone_data and "cmds" in zone_data:
                for cmd in zone_data["cmds"]:
                    if not isinstance(cmd, dict):
                        continue
                    
                    cmd_type = cmd.get("cmd", "")
                    arg1 = cmd.get("arg1", 0)
                    arg2 = cmd.get("arg2", 0)
                    arg3 = cmd.get("arg3", 0)
                    prob = cmd.get("prob", 100)
                    
                    # Track current mobile for equipment context
                    if cmd_type in ("M", "W"):
                        current_mobile = arg1
                    
                    # Object loaded in room
                    if cmd_type in ("O", "X") and arg1 == vnum:
                        room_brief = self.world.room_brief(arg3)
                        prob_text = f" ({prob}% chance)" if prob < 100 else ""
                        associations["🏠 Loads in rooms"].append(f"Zone {zone_num}: {room_brief} (max {arg2}){prob_text}")
                        if prob < 100:
                            associations["🎯 Load probability"].append(f"Zone {zone_num}: {prob}% chance to load")
                    
                    # Object equipped/given to mobile
                    elif cmd_type in ("E", "Z", "G", "Y") and arg1 == vnum:
                        if current_mobile:
                            mob_brief = self.world.mob_brief(current_mobile)
                            wear_info = ""
                            if cmd_type in ("E", "Z"):
                                wear_slots = ["light", "finger", "finger", "neck", "neck", "body", "head", "legs", "feet", "hands", "arms", "shield", "about", "waist", "wrist", "wrist", "wield", "hold", "throw", "two hands", "ankle", "ankle", "floating", "orb"]
                                slot_name = wear_slots[arg3] if 0 <= arg3 < len(wear_slots) else f"slot#{arg3}"
                                wear_info = f" (worn on {slot_name})"
                            prob_text = f" ({prob}% chance)" if prob < 100 else ""
                            associations["👹 Carried by mobiles"].append(f"Zone {zone_num}: {mob_brief} (max {arg2}){wear_info}{prob_text}")
                            if prob < 100:
                                associations["🎯 Load probability"].append(f"Zone {zone_num}: {prob}% chance on {self.world.mob_brief(current_mobile)}")
                        else:
                            associations["👹 Carried by mobiles"].append(f"Zone {zone_num}: Unknown mobile (max {arg2})")
                    
                    # Container relationships
                    elif cmd_type in ("P", "Q"):
                        prob_text = f" ({prob}% chance)" if prob < 100 else ""
                        if arg1 == vnum:  # This object is put into container arg3
                            container_brief = self.world.obj_brief(arg3)
                            associations["📦 Found in containers"].append(f"Zone {zone_num}: {container_brief} (max {arg2}){prob_text}")
                        elif arg3 == vnum:  # This container contains object arg1
                            contained_brief = self.world.obj_brief(arg1)
                            associations["📦 Contains objects"].append(f"Zone {zone_num}: {contained_brief} (max {arg2}){prob_text}")
                        if prob < 100:
                            associations["🎯 Load probability"].append(f"Zone {zone_num}: {prob}% chance in container")
                    
                    # Reset mobile context for non-mobile commands
                    if cmd_type not in ("M", "W", "E", "Z", "G", "Y"):
                        current_mobile = None
            
            # Check assembles
            assemble_dir = Path(str(zone_num)) / "assemble"
            if assemble_dir.exists():
                for assemble_file in assemble_dir.iterdir():
                    if assemble_file.suffix != ".json":
                        continue
                    try:
                        import json
                        with open(assemble_file, 'r') as f:
                            assemble_data = json.load(f)
                        
                        result_vnum = assemble_data.get("vnum", 0)
                        parts = assemble_data.get("parts", [])
                        cmds = assemble_data.get("cmd", [])
                        
                        if result_vnum == vnum:
                            cmd_text = f" (commands: {', '.join(str(x) for x in cmds)})" if cmds else ""
                            associations["🔧 Crafted via recipes"].append(f"Zone {zone_num}: Recipe {assemble_file.stem}{cmd_text}")
                        
                        if isinstance(parts, list) and vnum in parts:
                            result_brief = self.world.obj_brief(result_vnum)
                            associations["🔧 Used as recipe part"].append(f"Zone {zone_num}: Part for {result_brief}")
                    except Exception:
                        continue
            
            # Check scripts for references
            script_dir = Path(str(zone_num)) / "script"
            if script_dir.exists():
                for script_file in script_dir.iterdir():
                    if script_file.suffix != ".json":
                        continue
                    try:
                        script_data = self.world.load("script", int(script_file.stem))
                        if script_data:
                            code = script_data.get("code", "")
                            if str(vnum) in code:
                                script_name = script_data.get("name", "Unnamed")
                                script_type = script_data.get("type", "Unknown")
                                associations["📜 Referenced in scripts"].append(f"Zone {zone_num}: {script_name} (type {script_type})")
                    except Exception:
                        continue
        
        # Remove empty categories and deduplicate load probability entries
        for key, items in associations.items():
            if key == "🎯 Load probability":
                # Remove duplicates while preserving order
                seen = set()
                associations[key] = [x for x in items if not (x in seen or seen.add(x))]
        
        return {k: v for k, v in associations.items() if v}
    
    def browse_assembles(self):
        """Browse all assemble recipes across all zones"""
        print("Loading assemble recipes from all zones...")
        
        assembles = []
        for zone_num in self.zones:
            assemble_dir = Path(str(zone_num)) / "assemble"
            if not assemble_dir.exists():
                continue
            
            for assemble_file in assemble_dir.iterdir():
                if assemble_file.suffix != ".json":
                    continue
                try:
                    import json
                    with open(assemble_file, 'r') as f:
                        assemble_data = json.load(f)
                    
                    result_vnum = assemble_data.get('vnum', 0)
                    parts = assemble_data.get('parts', [])
                    cmds = assemble_data.get('cmd', [])
                    keywords = assemble_data.get('keywords', [])
                    
                    assembles.append({
                        'zone': zone_num,
                        'file': assemble_file.stem,
                        'result_vnum': result_vnum,
                        'parts': parts,
                        'cmds': cmds,
                        'keywords': keywords
                    })
                except Exception:
                    continue
        
        print(f"Found {len(assembles)} assemble recipes")
        
        if not assembles:
            print("❌ No assemble recipes found!")
            input("Press Enter to continue...")
            return
        
        # Sort by zone then by result vnum
        assembles.sort(key=lambda x: (x['zone'], x['result_vnum']))
        
        page = 0
        page_size = 10
        
        while True:
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(assembles))
            
            print(f"\n🔧 ASSEMBLE RECIPES (Page {page + 1}/{(len(assembles) - 1) // page_size + 1})")
            print(f"Found {len(assembles)} recipes")
            print("-" * 60)
            
            for i, recipe in enumerate(assembles[start_idx:end_idx], 1):
                result_brief = self.world.obj_brief(recipe['result_vnum'])
                print(f"{i:2d}. [Zone {recipe['zone']}] {result_brief} ({len(recipe['parts'])} parts)")
            
            print("\n0. ← Back to search menu")
            if page > 0:
                print("p. ← Previous page")
            if end_idx < len(assembles):
                print("n. → Next page")
            
            choice = input("\n➤ Select recipe number, n/p for pages, or 0: ").strip().lower()
            
            if choice == "0":
                break
            elif choice == "n" and end_idx < len(assembles):
                page += 1
            elif choice == "p" and page > 0:
                page -= 1
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < (end_idx - start_idx):
                        recipe = assembles[start_idx + idx]
                        self.show_assemble_details(recipe)
                except ValueError:
                    print("❌ Invalid choice!")
                    input("Press Enter to continue...")
    
    def show_assemble_details(self, recipe):
        """Show detailed information about an assemble recipe"""
        while True:
            print(f"\n🔧 ASSEMBLE RECIPE [Zone {recipe['zone']}]")
            print("=" * 60)
            
            result_brief = self.world.obj_brief(recipe['result_vnum'])
            print(f"Result: {result_brief}")
            
            if recipe['cmds']:
                print(f"Commands: {', '.join(str(x) for x in recipe['cmds'])}")
            
            if recipe['keywords']:
                print(f"Keywords: {', '.join(str(x) for x in recipe['keywords'])}")
            
            print(f"\nParts ({len(recipe['parts'])} items):")
            for part_vnum in recipe['parts']:
                part_brief = self.world.obj_brief(part_vnum)
                print(f"  - {part_brief}")
            
            print("\n0. ← Back to recipe list")
            choice = input("➤ Press 0 to return: ").strip()
            if choice == "0" or not choice:
                break


def main():
    search = GlobalSearch()
    search.main_menu()


if __name__ == "__main__":
    main()