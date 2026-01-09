#!/usr/bin/env python3
"""
Unified Data Service - Centralized data access and caching for MUD Analyzer
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import json
from dataclasses import dataclass

from mud_analyzer.core.world_lookup import World
from mud_analyzer.config import config
from mud_analyzer.cache_manager import cache_manager
from mud_analyzer.error_handler import safe_int


@dataclass
class EntityInfo:
    """Unified entity information"""
    vnum: int
    zone: int
    name: str
    entity_type: str
    data: Dict[str, Any]


class DataService:
    """Centralized data access service"""
    
    def __init__(self):
        self.world = World(config.project_root)
        self._zones: Optional[List[int]] = None
        self._command_index: Optional[Dict[int, List[Dict]]] = None
        self._entity_cache: Dict[str, Dict[int, EntityInfo]] = {}
    
    @property
    def zones(self) -> List[int]:
        """Get available zones"""
        if self._zones is None:
            self._zones = []
            for d in config.project_root.iterdir():
                if d.is_dir() and d.name.isdigit():
                    self._zones.append(int(d.name))
            self._zones.sort()
        return self._zones
    
    def get_command_index(self) -> Dict[int, List[Dict]]:
        """Get or build command index for fast lookups"""
        if self._command_index is not None:
            return self._command_index
        
        # Try cache first
        cached = cache_manager.load_from_cache("command_index")
        if cached is not None:
            self._command_index = cached
            return self._command_index
        
        print("Building command index...")
        self._command_index = {}
        
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
                
                if cmd_type == "M":
                    current_mobile = arg1
                elif cmd_type in ("O", "X") and arg1 > 0:
                    # Room loads
                    if arg1 not in self._command_index:
                        self._command_index[arg1] = []
                    self._command_index[arg1].append({
                        'zone': zone_num,
                        'cmd_type': cmd_type,
                        'arg1': arg1,
                        'arg2': arg2,
                        'arg3': arg3,
                        'prob': prob,
                        'mobile_context': None
                    })
                elif cmd_type in ("E", "Z", "G", "Y") and arg1 > 0:
                    # Mobile equipment/inventory loads
                    if arg1 not in self._command_index:
                        self._command_index[arg1] = []
                    self._command_index[arg1].append({
                        'zone': zone_num,
                        'cmd_type': cmd_type,
                        'arg1': arg1,
                        'arg2': arg2,
                        'arg3': arg3,
                        'prob': prob,
                        'mobile_context': current_mobile
                    })
                elif cmd_type in ("P", "Q") and arg1 > 0:
                    # Container loads
                    if arg1 not in self._command_index:
                        self._command_index[arg1] = []
                    self._command_index[arg1].append({
                        'zone': zone_num,
                        'cmd_type': cmd_type,
                        'arg1': arg1,
                        'arg2': arg2,
                        'arg3': arg3,
                        'prob': prob,
                        'mobile_context': None
                    })
        
        cache_manager.save_to_cache("command_index", self._command_index)
        print(f"Indexed {len(self._command_index)} unique items")
        return self._command_index
    
    def get_entities(self, entity_type: str) -> Dict[int, EntityInfo]:
        """Get all entities of a specific type"""
        if entity_type in self._entity_cache:
            return self._entity_cache[entity_type]
        
        # Try cache first
        cache_key = f"entities_{entity_type}"
        cached = cache_manager.load_from_cache(cache_key)
        if cached is not None:
            self._entity_cache[entity_type] = cached
            return cached
        
        print(f"Loading {entity_type} entities...")
        entities = {}
        
        for zone_num in self.zones:
            entity_dir = config.project_root / str(zone_num) / entity_type
            if not entity_dir.exists():
                continue
            
            for entity_file in entity_dir.iterdir():
                if entity_file.suffix != ".json":
                    continue
                
                try:
                    vnum = safe_int(entity_file.stem)
                    if vnum <= 0:
                        continue
                    
                    data = self.world.load(entity_type, vnum)
                    if data:
                        name = self._extract_name(data, entity_type)
                        entities[vnum] = EntityInfo(
                            vnum=vnum,
                            zone=zone_num,
                            name=name,
                            entity_type=entity_type,
                            data=data
                        )
                except Exception:
                    continue
        
        self._entity_cache[entity_type] = entities
        cache_manager.save_to_cache(cache_key, entities)
        print(f"Loaded {len(entities)} {entity_type} entities")
        return entities
    
    def _extract_name(self, data: Dict[str, Any], entity_type: str) -> str:
        """Extract display name from entity data"""
        if entity_type == "object":
            return data.get("short_desc") or data.get("short_descr") or data.get("name") or "Unnamed"
        elif entity_type == "mobile":
            return data.get("short_descr") or data.get("short_desc") or data.get("name") or "Unnamed"
        elif entity_type == "room":
            return data.get("name") or data.get("title") or "Unnamed"
        else:
            return data.get("name") or "Unnamed"
    
    def get_entity_by_vnum(self, vnum: int) -> Optional[EntityInfo]:
        """Get entity info by VNUM, auto-detecting type"""
        entity_type = self.world.detect_entity_type(vnum)
        if not entity_type:
            return None
        
        entities = self.get_entities(entity_type)
        return entities.get(vnum)
    
    def search_all_entities(self, search_term: str) -> List[EntityInfo]:
        """Search across all entity types"""
        results = []
        for entity_type in ["object", "mobile", "room", "script"]:
            try:
                entities = self.search_entities(entity_type, search_term)
                results.extend(entities)
            except Exception:
                continue
    def search_entities(self, entity_type: str, search_term: str, accessible_only: bool = False) -> List[EntityInfo]:
        """Search entities by name"""
        entities = self.get_entities(entity_type)
        search_term = search_term.lower()
        
        results = [
            entity for entity in entities.values()
            if search_term in entity.name.lower()
        ]
        
        if accessible_only:
            results = [entity for entity in results if self.is_entity_accessible(entity)]
        
        return results
    
    def is_entity_accessible(self, entity: EntityInfo) -> bool:
        """Check if an entity is accessible in the game"""
        if entity.entity_type == "object":
            # Objects are accessible if they:
            # 1. Have load locations (zone commands, mobile equipment, etc.), OR
            # 2. Are created by scripts/special procedures, OR
            # 3. Are created by mobiles with special procedures
            locations = self.get_load_locations(entity.vnum)
            if locations:
                return True
            
            # Check if it's created by special procedures or scripts
            if self._is_script_created_object(entity.vnum):
                return True
                
            return False
        elif entity.entity_type == "mobile":
            # Mobiles are accessible if they appear in zone M commands
            for zone_num in self.zones:
                zone_data = self.world.load_zone(zone_num)
                if not zone_data or "cmds" not in zone_data:
                    continue
                
                for cmd in zone_data["cmds"]:
                    if not isinstance(cmd, dict):
                        continue
                    
                    cmd_type = cmd.get("cmd", "")
                    arg1 = safe_int(cmd.get("arg1", 0))
                    
                    if cmd_type == "M" and arg1 == entity.vnum:
                        return True
            return False
        else:
            # For other entity types, assume accessible
            return True
    
    def _is_script_created_object(self, vnum: int) -> bool:
        """Check if an object is created by scripts or special procedures"""
        # Check if any mobile with special procedures might create this object
        mobiles = self.get_entities("mobile")
        for mobile in mobiles.values():
            # Check if mobile has special procedure and is accessible
            if mobile.data.get('spec_proc') and self.is_entity_accessible(mobile):
                # For now, assume any accessible mobile with spec_proc might create objects
                # This could be refined with more specific analysis
                return True
        
        # Check scripts for object creation patterns
        for zone_num in self.zones:
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
                    # Look for this vnum in script text
                    if str(vnum) in script_text and ('obj_to_char' in script_text or 'obj_to_room' in script_text):
                        return True
                except Exception:
                    continue
        
        return False
    
    def get_load_locations(self, vnum: int) -> List[Dict[str, Any]]:
        """Get all locations where an item loads"""
        command_index = self.get_command_index()
        commands = command_index.get(vnum, [])
        
        locations = []
        
        # Check zone commands
        for cmd in commands:
            cmd_type = cmd['cmd_type']
            zone = cmd['zone']
            prob = cmd['prob']
            
            if cmd_type in ("O", "X"):
                location = {
                    'type': 'room',
                    'zone': zone,
                    'location': self.world.room_brief(cmd['arg3']),
                    'probability': prob
                }
            elif cmd_type in ("E", "Z"):
                mobile_vnum = cmd['mobile_context'] if cmd['mobile_context'] else cmd['arg3']
                location = {
                    'type': 'mobile_equipment',
                    'zone': zone,
                    'location': self.world.get_entity_brief(mobile_vnum),
                    'probability': prob
                }
            elif cmd_type in ("G", "Y"):
                mobile_vnum = cmd['mobile_context'] if cmd['mobile_context'] else cmd['arg3']
                location = {
                    'type': 'mobile_inventory',
                    'zone': zone,
                    'location': self.world.get_entity_brief(mobile_vnum),
                    'probability': prob
                }
            elif cmd_type in ("P", "Q"):
                location = {
                    'type': 'container',
                    'zone': zone,
                    'location': self.world.get_entity_brief(cmd['arg3']),
                    'probability': prob
                }
            else:
                continue
            
            locations.append(location)
        
        # Check mobile repops - only if vnum is an object
        entity_type = self.world.detect_entity_type(vnum)
        if entity_type == "object":
            mobiles = self.get_entities("mobile")
            for mobile in mobiles.values():
                repops = mobile.data.get('repops', [])
                for repop in repops:
                    if safe_int(repop.get('vnum', 0)) == vnum:
                        locations.append({
                            'type': 'mobile_equipment',
                            'zone': mobile.zone,
                            'location': self.world.mob_brief(mobile.vnum),
                            'probability': safe_int(repop.get('percent', 100))
                        })
        
        return locations
    
    def clear_cache(self):
        """Clear all cached data"""
        self._zones = None
        self._command_index = None
        self._entity_cache.clear()
        cache_manager.clear_cache()


# Global data service instance
data_service = DataService()