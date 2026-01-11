#!/usr/bin/env python3
"""
Script-Created Items Explorer - Find items created by special procedures and scripts
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Set
import json
import re

# Add parent directory to path for package imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mud_analyzer.legacy.base_explorer import BaseExplorer, MenuMixin
from mud_analyzer.data_service import data_service
from mud_analyzer.shared.config import config
from mud_analyzer.shared.error_handler import handle_errors, safe_int


class ScriptCreatedItemsExplorer(BaseExplorer, MenuMixin):
    """Explorer for items created by scripts and special procedures"""
    
    def __init__(self):
        super().__init__()
        self._script_items: List[Dict[str, Any]] = []
        self._loaded = False
    
    def get_items(self) -> List[Dict[str, Any]]:
        """Get script-created items"""
        if not self._loaded:
            self._load_script_items()
        return self._script_items
    
    @handle_errors()
    def _load_script_items(self) -> None:
        """Load script-created items from all zones"""
        print("Analyzing scripts and special procedures for item creation...")
        
        self._script_items = []
        
        # Find mobiles with special procedures
        mobiles = data_service.get_entities("mobile")
        spec_proc_mobs = []
        
        for mobile in mobiles.values():
            spec_proc = mobile.data.get('spec_proc')
            if spec_proc and spec_proc.strip():
                spec_proc_mobs.append({
                    'vnum': mobile.vnum,
                    'zone': mobile.zone,
                    'name': mobile.name,
                    'spec_proc': spec_proc
                })
        
        # Find scripts that might create items
        script_creators = []
        for zone_num in data_service.zones:
            script_dir = config.project_root / str(zone_num) / "script"
            if not script_dir.exists():
                continue
            
            for script_file in script_dir.iterdir():
                if script_file.suffix != ".json":
                    continue
                
                try:
                    with open(script_file, 'r') as f:
                        script_data = json.load(f)
                    
                    script_text = script_data.get('script', '')
                    if self._script_creates_items(script_text):
                        script_creators.append({
                            'vnum': safe_int(script_file.stem),
                            'zone': zone_num,
                            'name': script_data.get('name', 'Unnamed Script'),
                            'type': script_data.get('type', 'unknown'),
                            'trigger_type': script_data.get('trigger_type', 'unknown'),
                            'script': script_text
                        })
                except Exception:
                    continue
        
        # Known script-created items (hardcoded examples)
        known_items = [
            {
                'result_vnum': 19002,
                'result_name': 'the Armor of the Gods',
                'creator_type': 'special_procedure',
                'creator_vnum': 18226,
                'creator_name': 'Kharas',
                'creator_zone': 180,
                'method': 'mob_kharas special procedure',
                'requirements': 'Bring Kharas his hammer and materials',
                'accessibility': 'possible'  # Will be checked dynamically
            }
        ]
        
        # Add known items and check their accessibility
        for item in known_items:
            creator_vnum = item.get('creator_vnum')
            if creator_vnum:
                creator_entity = data_service.get_entity_by_vnum(creator_vnum)
                if creator_entity:
                    item['accessibility'] = 'possible' if data_service.is_entity_accessible(creator_entity) else 'impossible'
                else:
                    item['accessibility'] = 'impossible'
            self._script_items.append(item)
        
        # Add items from special procedure analysis
        for mob in spec_proc_mobs:
            # Check if this mobile is accessible
            mob_entity = data_service.get_entity_by_vnum(mob['vnum'])
            if mob_entity and data_service.is_entity_accessible(mob_entity):
                # Look for objects that might be created by this mobile
                # This is a heuristic - could be improved with more analysis
                created_items = self._find_potential_spec_proc_items(mob)
                self._script_items.extend(created_items)
        
        # Add items from script analysis
        for script in script_creators:
            created_items = self._analyze_script_items(script)
            self._script_items.extend(created_items)
        
        self._script_items.sort(key=lambda x: (x.get('creator_zone', 0), x.get('result_vnum', 0)))
        self._loaded = True
        print(f"Found {len(self._script_items)} script-created items")
    
    def _script_creates_items(self, script_text: str) -> bool:
        """Check if script text contains item creation logic"""
        if not script_text:
            return False
        
        creation_patterns = [
            r'obj_to_char',
            r'obj_to_room',
            r'load_obj',
            r'create_obj',
            r'make_obj',
            r'give.*obj',
            r'drop.*obj'
        ]
        
        for pattern in creation_patterns:
            if re.search(pattern, script_text, re.IGNORECASE):
                return True
        
        return False
    
    def _find_potential_spec_proc_items(self, mob: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find potential items created by special procedure mobiles"""
        items = []
        
        # Look for objects in the same zone that don't have normal load locations
        # but might be created by this special procedure mobile
        zone_objects = []
        zone_num = mob['zone']
        object_dir = config.project_root / str(zone_num) / "object"
        
        if object_dir.exists():
            for obj_file in object_dir.iterdir():
                if obj_file.suffix != ".json":
                    continue
                
                try:
                    vnum = safe_int(obj_file.stem)
                    if vnum > 0:
                        # Check if this object has normal load locations
                        locations = data_service.get_load_locations(vnum)
                        if not locations:
                            # No normal load locations - might be script created
                            obj_name = data_service.world.obj_brief(vnum)
                            items.append({
                                'result_vnum': vnum,
                                'result_name': obj_name,
                                'creator_type': 'special_procedure',
                                'creator_vnum': mob['vnum'],
                                'creator_name': mob['name'],
                                'creator_zone': mob['zone'],
                                'method': f"{mob['spec_proc']} special procedure",
                                'requirements': f"Interact with {mob['name']}",
                                'accessibility': 'possible'
                            })
                except Exception:
                    continue
        
        return items
    
    def _analyze_script_items(self, script: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze what items a script might create"""
        items = []
        script_text = script.get('script', '')
        
        # Look for vnum patterns in script
        vnum_patterns = re.findall(r'\b(\d{4,5})\b', script_text)
        
        for vnum_str in vnum_patterns:
            vnum = safe_int(vnum_str)
            if vnum > 0:
                # Check if this vnum is an object
                entity_type = data_service.world.detect_entity_type(vnum)
                if entity_type == "object":
                    obj_name = data_service.world.obj_brief(vnum)
                    items.append({
                        'result_vnum': vnum,
                        'result_name': obj_name,
                        'creator_type': 'script',
                        'creator_vnum': script['vnum'],
                        'creator_name': script['name'],
                        'creator_zone': script['zone'],
                        'method': f"Script {script['vnum']} (type {script['type']})",
                        'requirements': 'Script trigger conditions',
                        'accessibility': 'unknown'
                    })
        
        return items
    
    def format_item(self, item: Dict[str, Any]) -> str:
        """Format script-created item for display"""
        status = "✅" if item.get('accessibility') == 'possible' else "❓"
        name = item.get('result_name', 'Unknown Item')
        if len(name) > 50:
            name = name[:47] + "..."
        
        creator_zone = item.get('creator_zone', 0)
        creator_type = item.get('creator_type', 'unknown')
        
        return f"{status:8} [Z{creator_zone:3d}] {name:<50} ({creator_type})"
    
    def show_item_details(self, item: Dict[str, Any]) -> None:
        """Show detailed script-created item information"""
        while True:
            print(f"\n🔧 SCRIPT-CREATED ITEM DETAILS")
            print("=" * 80)
            print(f"📦 Result Item: {item.get('result_name', 'Unknown')}")
            print(f"🔢 Result VNUM: {item.get('result_vnum', 'Unknown')}")
            print(f"🏠 Creator Zone: {item.get('creator_zone', 'Unknown')}")
            print(f"👤 Creator: {item.get('creator_name', 'Unknown')}")
            print(f"🔢 Creator VNUM: {item.get('creator_vnum', 'Unknown')}")
            print(f"⚙️  Creation Method: {item.get('method', 'Unknown')}")
            print(f"📋 Requirements: {item.get('requirements', 'Unknown')}")
            
            accessibility = item.get('accessibility', 'unknown')
            if accessibility == 'possible':
                print("✅ STATUS: Item can be created")
            elif accessibility == 'impossible':
                print("❌ STATUS: Item cannot be created")
            else:
                print("❓ STATUS: Creation method needs investigation")
            
            print("\n" + "=" * 80)
            print("0. ← Back to list")
            print("i. 🔍 Investigate creator")
            choice = input("➤ Press 0 to return or i to investigate: ").strip().lower()
            if choice == "0" or not choice:
                break
            elif choice == "i":
                self._investigate_creator(item)
    
    def _investigate_creator(self, item: Dict[str, Any]) -> None:
        """Investigate the creator of the item"""
        creator_vnum = item.get('creator_vnum')
        creator_type = item.get('creator_type')
        
        print(f"\n🔍 INVESTIGATING CREATOR")
        print("=" * 50)
        
        if creator_type == 'special_procedure':
            # Show mobile details
            mobile_data = data_service.world.load("mobile", creator_vnum)
            if mobile_data:
                print(f"Mobile: {data_service.world.mob_brief(creator_vnum)}")
                print(f"Special Procedure: {mobile_data.get('spec_proc', 'None')}")
                print(f"Description: {mobile_data.get('description', 'No description')}")
        elif creator_type == 'script':
            # Show script details
            script_data = data_service.world.load("script", creator_vnum)
            if script_data:
                print(f"Script: {data_service.world.script_brief(creator_vnum)}")
                print(f"Type: {script_data.get('type', 'Unknown')}")
                print(f"Trigger: {script_data.get('trigger_type', 'Unknown')}")
                script_text = script_data.get('script', '')
                if script_text:
                    print(f"Script Preview: {script_text[:200]}...")
        
        input("\nPress Enter to continue...")
    
    def _get_searchable_text(self, item: Dict[str, Any]) -> str:
        """Get searchable text for script-created items"""
        return item.get('result_name', '')
    
    def browse_all_items(self) -> None:
        """Browse all script-created items"""
        items = self.get_items()
        self.display_items("🔧 ALL SCRIPT-CREATED ITEMS", items)
    
    def browse_by_creator_type(self) -> None:
        """Browse items by creator type"""
        while True:
            print(f"\n🔧 BROWSE BY CREATOR TYPE")
            print("=" * 50)
            print("1. Special Procedures")
            print("2. Scripts")
            print("0. ← Back")
            
            choice = input("\n➤ Select option: ").strip()
            if choice == "0":
                break
            elif choice == "1":
                items = [item for item in self.get_items() if item.get('creator_type') == 'special_procedure']
                self.display_items("🔧 SPECIAL PROCEDURE ITEMS", items)
            elif choice == "2":
                items = [item for item in self.get_items() if item.get('creator_type') == 'script']
                self.display_items("🔧 SCRIPT ITEMS", items)
    
    def search_items_menu(self) -> None:
        """Search script-created items"""
        items = self.get_items()
        matches = self.search_items(items, "item name")
        if matches:
            self.display_items("🔍 SEARCH RESULTS", matches)
    
    def reload_data(self) -> None:
        """Reload all data"""
        data_service.clear_cache()
        self._loaded = False
        self._script_items = []
        print("✅ Data reloaded!")
        input("Press Enter to continue...")
    
    def main_menu(self) -> None:
        """Main menu for script-created items explorer"""
        menu_options = {
            "1": ("📋 Browse All Items", self.browse_all_items),
            "2": ("⚙️  Browse by Creator Type", self.browse_by_creator_type),
            "3": ("🔍 Search Items", self.search_items_menu),
            "4": ("🔄 Reload Data", self.reload_data),
            "0": ("← Back to Main Menu", lambda: None)
        }
        
        self.run_menu_loop("🔧 SCRIPT-CREATED ITEMS EXPLORER", menu_options)


def main():
    explorer = ScriptCreatedItemsExplorer()
    explorer.main_menu()


if __name__ == "__main__":
    main()