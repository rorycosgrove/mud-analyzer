"""
World Service - Core world data access and management
"""

import json
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from functools import lru_cache

from ..models.entities import (
    ObjectEntity, MobileEntity, ZoneInfo, ZoneSummary, 
    LoadLocation, LoadLocationType, AccessibilityStatus, EntityType
)
from ..config import Config


class WorldService:
    """Service for accessing MUD world data"""
    
    def __init__(self, config: Config):
        self.config = config
        self._zone_cache: Dict[int, Dict[str, Any]] = {}
        self._entity_cache: Dict[str, Dict[int, Any]] = {}
    
    async def get_zones(self) -> List[ZoneInfo]:
        """Get list of all available zones"""
        zones = []
        
        for zone_dir in self.config.world_root.iterdir():
            if zone_dir.is_dir() and zone_dir.name.isdigit():
                zone_num = int(zone_dir.name)
                zone_file = zone_dir / f"{zone_num}.json"
                
                if zone_file.exists():
                    try:
                        zone_data = await self._load_json(zone_file)
                        zones.append(ZoneInfo(
                            number=zone_num,
                            name=zone_data.get("name", f"Zone {zone_num}"),
                            author=zone_data.get("author", "Unknown"),
                            level_range=zone_data.get("level_range"),
                            description=zone_data.get("description")
                        ))
                    except Exception:
                        continue
        
        return sorted(zones, key=lambda z: z.number)
    
    async def get_zone_details(self, zone_number: int) -> Dict[str, Any]:
        """Get detailed zone information"""
        if zone_number in self._zone_cache:
            return self._zone_cache[zone_number]
        
        zone_path = self.config.get_zone_path(zone_number)
        zone_file = zone_path / f"{zone_number}.json"
        
        if not zone_file.exists():
            raise ValueError(f"Zone {zone_number} not found")
        
        zone_data = await self._load_json(zone_file)
        self._zone_cache[zone_number] = zone_data
        return zone_data
    
    async def get_object_details(self, vnum: int) -> ObjectEntity:
        """Get detailed object information"""
        zone_num = await self._find_entity_zone(vnum, "object")
        if not zone_num:
            raise ValueError(f"Object {vnum} not found")
        
        obj_path = self.config.get_zone_path(zone_num) / "object" / f"{vnum}.json"
        obj_data = await self._load_json(obj_path)
        
        return ObjectEntity(
            vnum=vnum,
            zone=zone_num,
            name=obj_data.get("short_desc", f"Object {vnum}"),
            type_flag=obj_data.get("type_flag", 0),
            short_desc=obj_data.get("short_desc", ""),
            description=obj_data.get("description"),
            weight=obj_data.get("weight", 0),
            cost=obj_data.get("cost", 0),
            accessible=await self._check_object_accessibility(vnum)
        )
    
    async def get_mobile_details(self, vnum: int) -> MobileEntity:
        """Get detailed mobile information"""
        zone_num = await self._find_entity_zone(vnum, "mobile")
        if not zone_num:
            raise ValueError(f"Mobile {vnum} not found")
        
        mob_path = self.config.get_zone_path(zone_num) / "mobile" / f"{vnum}.json"
        mob_data = await self._load_json(mob_path)
        
        return MobileEntity(
            vnum=vnum,
            zone=zone_num,
            name=mob_data.get("short_descr", f"Mobile {vnum}"),
            level=mob_data.get("level", 1),
            alignment=mob_data.get("alignment", 0),
            race=mob_data.get("race"),
            short_desc=mob_data.get("short_descr", ""),
            long_desc=mob_data.get("long_descr"),
            spec_proc=mob_data.get("spec_proc"),
            accessible=await self._check_mobile_accessibility(vnum)
        )
    
    async def get_load_locations(self, vnum: int) -> List[LoadLocation]:
        """Get all locations where an entity loads"""
        locations = []
        
        # Check zone commands
        for zone_info in await self.get_zones():
            try:
                zone_data = await self.get_zone_details(zone_info.number)
                commands = zone_data.get("cmds", [])
                
                current_mobile = None
                for cmd in commands:
                    if not isinstance(cmd, dict):
                        continue
                    
                    cmd_type = cmd.get("cmd", "")
                    arg1 = cmd.get("arg1", 0)
                    arg3 = cmd.get("arg3", 0)
                    prob = cmd.get("prob", 100)
                    
                    if cmd_type == "M":
                        current_mobile = arg1
                    elif cmd_type in ("O", "X") and arg1 == vnum:
                        locations.append(LoadLocation(
                            type=LoadLocationType.ROOM,
                            zone=zone_info.number,
                            location=f"Room {arg3}",
                            probability=prob
                        ))
                    elif cmd_type in ("E", "Z", "G", "Y") and arg1 == vnum:
                        locations.append(LoadLocation(
                            type=LoadLocationType.MOBILE_EQUIPMENT,
                            zone=zone_info.number,
                            location=f"Mobile {current_mobile or arg3}",
                            probability=prob
                        ))
            except Exception:
                continue
        
        return locations
    
    async def get_zone_summary(self, zone_number: int) -> ZoneSummary:
        """Get zone summary statistics"""
        zone_path = self.config.get_zone_path(zone_number)
        
        # Get zone info
        zones = await self.get_zones()
        zone_info = next((z for z in zones if z.number == zone_number), None)
        if not zone_info:
            raise ValueError(f"Zone {zone_number} not found")
        
        # Count entities
        entity_counts = {}
        accessible_counts = {}
        
        for entity_type in ["object", "mobile", "room", "script"]:
            entity_dir = zone_path / entity_type
            if entity_dir.exists():
                count = len([f for f in entity_dir.iterdir() if f.suffix == ".json"])
                entity_counts[entity_type] = count
                # For now, assume all are accessible (could be refined)
                accessible_counts[entity_type] = count
            else:
                entity_counts[entity_type] = 0
                accessible_counts[entity_type] = 0
        
        total_entities = sum(entity_counts.values())
        total_accessible = sum(accessible_counts.values())
        accessibility_rate = total_accessible / total_entities if total_entities > 0 else 0.0
        
        return ZoneSummary(
            zone=zone_info,
            entity_counts=entity_counts,
            accessible_counts=accessible_counts,
            total_entities=total_entities,
            accessibility_rate=accessibility_rate
        )
    
    async def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON file asynchronously"""
        def _load():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return await asyncio.get_event_loop().run_in_executor(None, _load)
    
    async def _find_entity_zone(self, vnum: int, entity_type: str) -> Optional[int]:
        """Find which zone contains an entity"""
        # Try heuristic first (vnum // 100)
        zone_guess = vnum // 100
        zone_path = self.config.get_zone_path(zone_guess)
        entity_file = zone_path / entity_type / f"{vnum}.json"
        
        if entity_file.exists():
            return zone_guess
        
        # Search all zones
        for zone_info in await self.get_zones():
            zone_path = self.config.get_zone_path(zone_info.number)
            entity_file = zone_path / entity_type / f"{vnum}.json"
            if entity_file.exists():
                return zone_info.number
        
        return None
    
    async def _check_object_accessibility(self, vnum: int) -> AccessibilityStatus:
        """Check if an object is accessible"""
        locations = await self.get_load_locations(vnum)
        return AccessibilityStatus.ACCESSIBLE if locations else AccessibilityStatus.INACCESSIBLE
    
    async def _check_mobile_accessibility(self, vnum: int) -> AccessibilityStatus:
        """Check if a mobile is accessible"""
        # Check if mobile appears in any zone M commands
        for zone_info in await self.get_zones():
            try:
                zone_data = await self.get_zone_details(zone_info.number)
                commands = zone_data.get("cmds", [])
                
                for cmd in commands:
                    if isinstance(cmd, dict) and cmd.get("cmd") == "M" and cmd.get("arg1") == vnum:
                        return AccessibilityStatus.ACCESSIBLE
            except Exception:
                continue
        
        return AccessibilityStatus.INACCESSIBLE