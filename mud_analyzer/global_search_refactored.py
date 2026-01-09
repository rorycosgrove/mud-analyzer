#!/usr/bin/env python3
"""
Global Search - Refactored version using unified data service
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for package imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mud_analyzer.base_explorer import BaseExplorer, MenuMixin
from mud_analyzer.data_service import data_service, EntityInfo
from mud_analyzer.analysis.identify_object import format_object_identify
from mud_analyzer.analysis.identify_mobile import format_mobile_identify
from mud_analyzer.utils.spell_lookup import load_spell_name_map
from mud_analyzer.error_handler import handle_errors, log_error


class GlobalSearch(BaseExplorer, MenuMixin):
    """Refactored global search using unified data service"""
    
    def __init__(self):
        super().__init__()
        try:
            self.spell_map = load_spell_name_map()
        except Exception as e:
            log_error(f"Failed to load spell map: {e}")
            self.spell_map = {}
        self._current_results: List[EntityInfo] = []
        self._current_type = ""
    
    def get_items(self) -> List[Dict[str, Any]]:
        """Convert EntityInfo to dict format for base class compatibility"""
        return [
            {
                'vnum': entity.vnum,
                'zone': entity.zone,
                'name': entity.name,
                'type': entity.entity_type,
                'data': entity.data,
                'entity': entity
            }
            for entity in self._current_results
        ]
    
    def format_item(self, item: Dict[str, Any]) -> str:
        """Format search result for display"""
        entity = item['entity']
        if entity.entity_type == "object":
            obj_type = entity.data.get("type_flag", "?")
            return f"[Zone {entity.zone}] [{entity.vnum}] {entity.name} (Type {obj_type})"
        elif entity.entity_type == "mobile":
            level = entity.data.get("level", "?")
            return f"[Zone {entity.zone}] [{entity.vnum}] {entity.name} (Level {level})"
        else:
            return f"[Zone {entity.zone}] [{entity.vnum}] {entity.name}"
    
    @handle_errors(show_traceback=False)
    def show_item_details(self, item: Dict[str, Any]) -> None:
        """Show detailed item information"""
        entity = item['entity']
        
        while True:
            try:
                if entity.entity_type == "object":
                    print(f"\n📦 OBJECT [Zone {entity.zone}] [{entity.vnum}]")
                    print("=" * 60)
                    # Add vnum to data for identification
                    obj_data = entity.data.copy()
                    obj_data['vnum'] = entity.vnum
                    output = format_object_identify(obj_data, self.spell_map)
                    print(output)
                elif entity.entity_type == "mobile":
                    print(f"\n👹 MOBILE [Zone {entity.zone}] [{entity.vnum}]")
                    print("=" * 60)
                    output = format_mobile_identify(entity.data, data_service.world)
                    print(output)
                
                # Show load locations
                self._show_associations(entity.vnum)
                
                print("\n0. ← Back to search results")
                choice = input("➤ Press 0 to return: ").strip()
                if choice == "0" or not choice:
                    break
            except Exception as e:
                log_error(f"Error showing item details: {e}")
                input("Press Enter to continue...")
                break
    
    def _show_associations(self, vnum: int) -> None:
        """Show where item loads and associations"""
        locations = data_service.get_load_locations(vnum)
        
        if not locations:
            print("\nℹ️ No load locations found")
            return
        
        print(f"\n🔗 LOAD LOCATIONS:")
        print("-" * 30)
        
        # Group by type
        by_type = {}
        for loc in locations:
            loc_type = loc['type']
            if loc_type not in by_type:
                by_type[loc_type] = []
            by_type[loc_type].append(loc)
        
        type_icons = {
            'room': '🏠',
            'mobile_equipment': '👹',
            'mobile_inventory': '🎒',
            'container': '📦'
        }
        
        for loc_type, locs in by_type.items():
            icon = type_icons.get(loc_type, '📍')
            print(f"\n{icon} {loc_type.replace('_', ' ').title()}:")
            for loc in locs[:5]:  # Limit to 5 per type
                print(f"  - {loc['location']} ({loc['probability']}%)")
            if len(locs) > 5:
                print(f"  ... and {len(locs) - 5} more")
    
    def search_objects(self) -> None:
        """Search for objects"""
        search_term = input("\n🔍 Enter object name to search for (or 'back' to return): ").strip()
        if not search_term or search_term.lower() in ['back', 'b']:
            return
        
        try:
            print("Searching objects...")
            self._current_results = data_service.search_entities("object", search_term)
            self._current_type = "object"
            
            print(f"Found {len(self._current_results)} matches")
            
            if self._current_results:
                self.display_items(f"📦 OBJECT SEARCH RESULTS: '{search_term}'", self.get_items())
            else:
                print(f"❌ No objects found matching '{search_term}'")
                input("Press Enter to continue...")
        except Exception as e:
            log_error(f"Error searching objects: {e}")
            input("Press Enter to continue...")
    
    def search_mobiles(self) -> None:
        """Search for mobiles"""
        search_term = input("\n🔍 Enter mobile name to search for (or 'back' to return): ").strip()
        if not search_term or search_term.lower() in ['back', 'b']:
            return
        
        try:
            print("Searching mobiles...")
            self._current_results = data_service.search_entities("mobile", search_term)
            self._current_type = "mobile"
            
            print(f"Found {len(self._current_results)} matches")
            
            if self._current_results:
                self.display_items(f"👹 MOBILE SEARCH RESULTS: '{search_term}'", self.get_items())
            else:
                print(f"❌ No mobiles found matching '{search_term}'")
                input("Press Enter to continue...")
        except Exception as e:
            log_error(f"Error searching mobiles: {e}")
            input("Press Enter to continue...")
    
    def rebuild_cache(self) -> None:
        """Rebuild search cache"""
        try:
            print("Rebuilding search index...")
            data_service.clear_cache()
            print("✅ Search index rebuilt!")
        except Exception as e:
            log_error(f"Error rebuilding cache: {e}")
        input("Press Enter to continue...")
    
    @handle_errors(show_traceback=False)
    def main_menu(self) -> None:
        """Main menu for global search"""
        menu_options = {
            "1": ("📦 Search Objects", self.search_objects),
            "2": ("👹 Search Mobiles", self.search_mobiles),
            "3": ("🔄 Rebuild Search Index", self.rebuild_cache),
            "0": ("← Back to Main Menu", lambda: None)
        }
        
        self.run_menu_loop("🔍 GLOBAL SEARCH", menu_options)


@handle_errors(show_traceback=False)
def main():
    try:
        search = GlobalSearch()
        search.main_menu()
    except Exception as e:
        log_error(f"Failed to start global search: {e}")


if __name__ == "__main__":
    main()