#!/usr/bin/env python3
"""
Interactive Zone Explorer - Menu-based zone exploration system
"""

import sys
from pathlib import Path
import os

# Add parent directory to path and change working directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from mud_analyzer.core.world_lookup import World
from mud_analyzer.analysis.identify_object import format_object_identify
from mud_analyzer.analysis.identify_mobile import format_mobile_identify
from mud_analyzer.utils.spell_lookup import load_spell_name_map
from mud_analyzer.shared.config import config
from mud_analyzer.shared.error_handler import handle_errors, log_error, validate_zone_num


class ZoneExplorer:
    def __init__(self, zone_num: int):
        try:
            config.setup_working_directory()
            self.zone_num = validate_zone_num(zone_num)
            self.world = World(config.project_root)
            self.world.set_hint_zone(self.zone_num)
            self.spell_map = load_spell_name_map()
            
            # Load zone data
            self.zone_data = self.world.load_zone(self.zone_num)
            if not self.zone_data:
                raise FileNotFoundError(f"Zone {self.zone_num} not found!")
        except Exception as e:
            log_error(f"Failed to initialize zone explorer: {e}")
            raise
    
    def show_header(self):
        name = self.zone_data.get("name", "Unknown Zone")
        author = self.zone_data.get("author", "Unknown")
        print(f"\n{'='*60}")
        print(f"🏰 ZONE {self.zone_num}: {name}")
        print(f"👤 Author: {author}")
        print(f"{'='*60}")
    
    @handle_errors(show_traceback=False)
    def main_menu(self):
        while True:
            try:
                self.show_header()
                print("\n📋 MAIN MENU")
                print("1. 📊 Zone Overview")
                print("2. 🏠 Browse Rooms")
                print("3. 👹 Browse Mobiles")
                print("4. 📦 Browse Objects")
                print("5. 📜 Browse Scripts")
                print("6. 🔧 Browse Assembles")
                print("0. 🚪 Exit")
                
                choice = input("\n➤ Select option: ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    self.show_overview()
                elif choice == "2":
                    self.browse_rooms()
                elif choice == "3":
                    self.browse_mobiles()
                elif choice == "4":
                    self.browse_objects()
                elif choice == "5":
                    self.browse_scripts()
                elif choice == "6":
                    self.browse_assembles()
                else:
                    print("❌ Invalid choice! Please select 0-6.")
                    input("Press Enter to continue...")
            except KeyboardInterrupt:
                print("\n⚠️ Returning to menu...")
            except Exception as e:
                log_error(f"Menu error: {e}")
                input("Press Enter to continue...")
    
    def show_overview(self):
        print(f"\n📊 ZONE {self.zone_num} OVERVIEW")
        print("-" * 40)
        
        # Count entities
        zone_dir = config.project_root / str(self.zone_num)
        counts = {}
        for subdir in ["room", "mobile", "object", "script", "assemble"]:
            path = zone_dir / subdir
            if path.exists():
                counts[subdir] = len([f for f in path.iterdir() if f.is_file() and f.suffix == ".json"])
            else:
                counts[subdir] = 0
        
        print(f"🏠 Rooms: {counts['room']}")
        print(f"👹 Mobiles: {counts['mobile']}")
        print(f"📦 Objects: {counts['object']}")
        print(f"📜 Scripts: {counts['script']}")
        print(f"🔧 Assembles: {counts['assemble']}")
        
        # Zone details
        print(f"\n📋 Details:")
        print(f"   Lifespan: {self.zone_data.get('lifespan', 'Unknown')}")
        print(f"   Reset Mode: {self.zone_data.get('reset_mode', 'Unknown')}")
        print(f"   Top VNUM: {self.zone_data.get('top', 'Unknown')}")
        
        input("\nPress Enter to continue...")
    
    def browse_rooms(self):
        zone_dir = config.project_root / str(self.zone_num) / "room"
        if not zone_dir.exists():
            print("❌ No rooms found!")
            input("Press Enter to continue...")
            return
        
        rooms = sorted([f for f in zone_dir.iterdir() if f.suffix == ".json"])
        if not rooms:
            print("❌ No room files found!")
            input("Press Enter to continue...")
            return
        
        page = 0
        page_size = 10
        
        while True:
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(rooms))
            
            print(f"\n🏠 ROOMS IN ZONE {self.zone_num} (Page {page + 1}/{(len(rooms) - 1) // page_size + 1})")
            print("-" * 40)
            
            for i, room_file in enumerate(rooms[start_idx:end_idx], 1):
                vnum = int(room_file.stem)
                room_data = self.world.load("room", vnum)
                name = room_data.get("name", "Unnamed") if room_data else "Error loading"
                print(f"{i:2d}. [{vnum}] {name}")
            
            print("\n0. ← Back to main menu")
            if page > 0:
                print("p. ← Previous page")
            if end_idx < len(rooms):
                print("n. → Next page")
            
            choice = input("➤ Select room number, n/p for pages, or 0: ").strip().lower()
            
            if choice == "0":
                break
            elif choice == "n" and end_idx < len(rooms):
                page += 1
            elif choice == "p" and page > 0:
                page -= 1
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < (end_idx - start_idx):
                        vnum = int(rooms[start_idx + idx].stem)
                        self.show_room_details(vnum)
                except ValueError:
                    print("❌ Invalid choice!")
                    input("Press Enter to continue...")
    
    def show_room_details(self, vnum: int):
        room_data = self.world.load("room", vnum)
        if not room_data:
            print(f"❌ Room {vnum} not found!")
            input("Press Enter to continue...")
            return
        
        print(f"\n🏠 ROOM [{vnum}]")
        print("=" * 50)
        print(f"Name: {room_data.get('name', 'Unnamed')}")
        
        desc = room_data.get('description', '')
        if desc:
            print(f"\nDescription:")
            print(f"  {desc}")
        
        # Show exits
        exits = room_data.get('exits', {})
        if exits:
            print(f"\nExits:")
            for direction, exit_data in exits.items():
                if isinstance(exit_data, dict):
                    to_room = exit_data.get('to_room', 'Unknown')
                    print(f"  {direction}: → Room {to_room}")
        
        input("\nPress Enter to continue...")
    
    def browse_mobiles(self):
        zone_dir = config.project_root / str(self.zone_num) / "mobile"
        if not zone_dir.exists():
            print("❌ No mobiles found!")
            input("Press Enter to continue...")
            return
        
        mobiles = sorted([f for f in zone_dir.iterdir() if f.suffix == ".json"])
        if not mobiles:
            print("❌ No mobile files found!")
            input("Press Enter to continue...")
            return
        
        page = 0
        page_size = 10
        
        while True:
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(mobiles))
            
            print(f"\n👹 MOBILES IN ZONE {self.zone_num} (Page {page + 1}/{(len(mobiles) - 1) // page_size + 1})")
            print("-" * 40)
            
            for i, mob_file in enumerate(mobiles[start_idx:end_idx], 1):
                vnum = int(mob_file.stem)
                mob_data = self.world.load("mobile", vnum)
                if mob_data:
                    short = mob_data.get("short_descr", "Unnamed")
                    level = mob_data.get("level", "?")
                    print(f"{i:2d}. [{vnum}] {short} (Level {level})")
                else:
                    print(f"{i:2d}. [{vnum}] Error loading")
            
            print("\n0. ← Back to main menu")
            if page > 0:
                print("p. ← Previous page")
            if end_idx < len(mobiles):
                print("n. → Next page")
            
            choice = input("➤ Select mobile number, n/p for pages, or 0: ").strip().lower()
            
            if choice == "0":
                break
            elif choice == "n" and end_idx < len(mobiles):
                page += 1
            elif choice == "p" and page > 0:
                page -= 1
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < (end_idx - start_idx):
                        vnum = int(mobiles[start_idx + idx].stem)
                        self.show_mobile_details(vnum)
                except ValueError:
                    print("❌ Invalid choice!")
                    input("Press Enter to continue...")
    
    def show_mobile_details(self, vnum: int):
        mob_data = self.world.load("mobile", vnum)
        if not mob_data:
            print(f"❌ Mobile {vnum} not found!")
            input("Press Enter to continue...")
            return
        
        print(f"\n👹 MOBILE [{vnum}]")
        print("=" * 50)
        output = format_mobile_identify(mob_data, self.world)
        print(output)
        input("Press Enter to continue...")
    
    def browse_objects(self):
        zone_dir = config.project_root / str(self.zone_num) / "object"
        if not zone_dir.exists():
            print("❌ No objects found!")
            input("Press Enter to continue...")
            return
        
        objects = sorted([f for f in zone_dir.iterdir() if f.suffix == ".json"])
        if not objects:
            print("❌ No object files found!")
            input("Press Enter to continue...")
            return
        
        page = 0
        page_size = 10
        
        while True:
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(objects))
            
            print(f"\n📦 OBJECTS IN ZONE {self.zone_num} (Page {page + 1}/{(len(objects) - 1) // page_size + 1})")
            print("-" * 40)
            
            for i, obj_file in enumerate(objects[start_idx:end_idx], 1):
                vnum = int(obj_file.stem)
                obj_data = self.world.load("object", vnum)
                if obj_data:
                    short = obj_data.get("short_desc", "Unnamed")
                    obj_type = obj_data.get("type_flag", "?")
                    print(f"{i:2d}. [{vnum}] {short} (Type {obj_type})")
                else:
                    print(f"{i:2d}. [{vnum}] Error loading")
            
            print("\n0. ← Back to main menu")
            if page > 0:
                print("p. ← Previous page")
            if end_idx < len(objects):
                print("n. → Next page")
            
            choice = input("➤ Select object number, n/p for pages, or 0: ").strip().lower()
            
            if choice == "0":
                break
            elif choice == "n" and end_idx < len(objects):
                page += 1
            elif choice == "p" and page > 0:
                page -= 1
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < (end_idx - start_idx):
                        vnum = int(objects[start_idx + idx].stem)
                        self.show_object_details(vnum)
                except ValueError:
                    print("❌ Invalid choice!")
                    input("Press Enter to continue...")
    
    def show_object_details(self, vnum: int):
        obj_data = self.world.load("object", vnum)
        if not obj_data:
            print(f"❌ Object {vnum} not found!")
            input("Press Enter to continue...")
            return
        
        print(f"\n📦 OBJECT [{vnum}]")
        print("=" * 50)
        output = format_object_identify(obj_data, self.spell_map)
        print(output)
        input("Press Enter to continue...")
    
    def browse_scripts(self):
        zone_dir = config.project_root / str(self.zone_num) / "script"
        if not zone_dir.exists():
            print("❌ No scripts found!")
            input("Press Enter to continue...")
            return
        
        scripts = sorted([f for f in zone_dir.iterdir() if f.suffix == ".json"])
        if not scripts:
            print("❌ No script files found!")
            input("Press Enter to continue...")
            return
        
        page = 0
        page_size = 10
        
        while True:
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(scripts))
            
            print(f"\n📜 SCRIPTS IN ZONE {self.zone_num} (Page {page + 1}/{(len(scripts) - 1) // page_size + 1})")
            print("-" * 40)
            
            for i, script_file in enumerate(scripts[start_idx:end_idx], 1):
                vnum = int(script_file.stem)
                script_data = self.world.load("script", vnum)
                if script_data:
                    name = script_data.get("name", "Unnamed")
                    script_type = script_data.get("type", "?")
                    print(f"{i:2d}. [{vnum}] {name} (Type {script_type})")
                else:
                    print(f"{i:2d}. [{vnum}] Error loading")
            
            print("\n0. ← Back to main menu")
            if page > 0:
                print("p. ← Previous page")
            if end_idx < len(scripts):
                print("n. → Next page")
            
            choice = input("➤ Select script number, n/p for pages, or 0: ").strip().lower()
            
            if choice == "0":
                break
            elif choice == "n" and end_idx < len(scripts):
                page += 1
            elif choice == "p" and page > 0:
                page -= 1
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < (end_idx - start_idx):
                        vnum = int(scripts[start_idx + idx].stem)
                        self.show_script_details(vnum)
                except ValueError:
                    print("❌ Invalid choice!")
                    input("Press Enter to continue...")
    
    def show_script_details(self, vnum: int):
        script_data = self.world.load("script", vnum)
        if not script_data:
            print(f"❌ Script {vnum} not found!")
            input("Press Enter to continue...")
            return
        
        print(f"\n📜 SCRIPT [{vnum}]")
        print("=" * 50)
        print(f"Name: {script_data.get('name', 'Unnamed')}")
        print(f"Type: {script_data.get('type', 'Unknown')}")
        print(f"Trigger: {script_data.get('trigger_type', 'Unknown')}")
        
        code = script_data.get('code', '')
        if code:
            lines = code.splitlines()
            print(f"\nCode ({len(lines)} lines):")
            
            page = 0
            page_size = 20
            
            while True:
                start_idx = page * page_size
                end_idx = min(start_idx + page_size, len(lines))
                
                print(f"\n--- Page {page + 1}/{(len(lines) - 1) // page_size + 1} ---")
                for i, line in enumerate(lines[start_idx:end_idx], start_idx + 1):
                    print(f"{i:3d}: {line}")
                
                if end_idx >= len(lines):
                    break
                
                choice = input("\nPress Enter for next page, 'q' to quit: ").strip().lower()
                if choice == 'q':
                    break
                page += 1
        
        input("\nPress Enter to continue...")
    
    def browse_assembles(self):
        zone_dir = config.project_root / str(self.zone_num) / "assemble"
        if not zone_dir.exists():
            print("❌ No assembles found!")
            input("Press Enter to continue...")
            return
        
        assembles = sorted([f for f in zone_dir.iterdir() if f.suffix == ".json"])
        if not assembles:
            print("❌ No assemble files found!")
            input("Press Enter to continue...")
            return
        
        page = 0
        page_size = 5
        
        while True:
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(assembles))
            
            print(f"\n🔧 ASSEMBLES IN ZONE {self.zone_num} (Page {page + 1}/{(len(assembles) - 1) // page_size + 1})")
            print("-" * 40)
            
            for i, assemble_file in enumerate(assembles[start_idx:end_idx], 1):
                try:
                    import json
                    with open(assemble_file, 'r') as f:
                        assemble_data = json.load(f)
                    
                    result_vnum = assemble_data.get('vnum', 'Unknown')
                    parts = assemble_data.get('parts', [])
                    print(f"\n{i}. 📋 Recipe: {assemble_file.stem}")
                    print(f"   Result: {self.world.obj_brief(result_vnum)}")
                    print(f"   Parts ({len(parts)} items):")
                    for part in parts:
                        print(f"     - {self.world.obj_brief(part)}")
                except Exception:
                    print(f"\n{i}. ❌ Error loading {assemble_file.name}")
            
            print("\n0. ← Back to main menu")
            if page > 0:
                print("p. ← Previous page")
            if end_idx < len(assembles):
                print("n. → Next page")
            
            choice = input("\n➤ n/p for pages, or 0: ").strip().lower()
            
            if choice == "0":
                break
            elif choice == "n" and end_idx < len(assembles):
                page += 1
            elif choice == "p" and page > 0:
                page -= 1
            else:
                print("❌ Invalid choice!")
                input("Press Enter to continue...")
    
    def search_objects(self):
        search_term = input("\n🔍 Enter object name to search for: ").strip().lower()
        if not search_term:
            print("❌ No search term entered!")
            input("Press Enter to continue...")
            return
        
        zone_dir = config.project_root / str(self.zone_num) / "object"
        if not zone_dir.exists():
            print("❌ No objects found in this zone!")
            input("Press Enter to continue...")
            return
        
        objects = sorted([f for f in zone_dir.iterdir() if f.suffix == ".json"])
        matches = []
        
        print(f"\n🔎 Searching for '{search_term}' in {len(objects)} objects...")
        
        for obj_file in objects:
            vnum = int(obj_file.stem)
            obj_data = self.world.load("object", vnum)
            if obj_data:
                short = obj_data.get("short_desc", "").lower()
                name = obj_data.get("name", "").lower()
                if search_term in short or search_term in name:
                    matches.append((vnum, obj_data))
        
        if not matches:
            print(f"❌ No objects found matching '{search_term}'")
            input("Press Enter to continue...")
            return
        
        page = 0
        page_size = 10
        
        while True:
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(matches))
            
            print(f"\n🔍 SEARCH RESULTS: '{search_term}' (Page {page + 1}/{(len(matches) - 1) // page_size + 1})")
            print(f"Found {len(matches)} matches")
            print("-" * 50)
            
            for i, (vnum, obj_data) in enumerate(matches[start_idx:end_idx], 1):
                short = obj_data.get("short_desc", "Unnamed")
                obj_type = obj_data.get("type_flag", "?")
                print(f"{i:2d}. [{vnum}] {short} (Type {obj_type})")
            
            print("\n0. ← Back to main menu")
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
                        vnum = matches[start_idx + idx][0]
                        self.show_object_details(vnum)
                except ValueError:
                    print("❌ Invalid choice!")
                    input("Press Enter to continue...")


@handle_errors(show_traceback=False)
def main():
    if len(sys.argv) != 2:
        print("Usage: python zone_explorer.py <zone_number>")
        sys.exit(1)
    
    try:
        zone_num = int(sys.argv[1])
        explorer = ZoneExplorer(zone_num)
        explorer.main_menu()
    except ValueError:
        print("❌ Zone number must be an integer!")
        sys.exit(1)
    except Exception as e:
        log_error(f"Failed to start zone explorer: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()