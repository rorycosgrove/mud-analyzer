"""
Search Service - Entity search and filtering
"""

import asyncio
from typing import List, Dict, Any
from pathlib import Path

from ..models.entities import SearchRequest, SearchResult, ObjectEntity, MobileEntity, AccessibilityStatus
from ..core.world_service import WorldService


class SearchService:
    """Service for searching MUD entities"""
    
    def __init__(self, world_service: WorldService):
        self.world_service = world_service
    
    async def search_entities(self, request: SearchRequest) -> List[SearchResult]:
        """Search for entities based on request criteria"""
        results = []
        
        if request.entity_type.value == "object":
            results = await self._search_objects(request)
        elif request.entity_type.value == "mobile":
            results = await self._search_mobiles(request)
        
        # Apply filters
        if request.accessible_only:
            results = [r for r in results if r.entity.accessible == AccessibilityStatus.ACCESSIBLE]
        
        if request.zone_filter:
            results = [r for r in results if r.entity.zone in request.zone_filter]
        
        # Apply limit
        results = results[:request.limit]
        
        return results
    
    async def _search_objects(self, request: SearchRequest) -> List[SearchResult]:
        """Search for objects"""
        results = []
        query_lower = request.query.lower()
        
        zones = await self.world_service.get_zones()
        
        for zone in zones:
            zone_path = self.world_service.config.get_zone_path(zone.number)
            object_dir = zone_path / "object"
            
            if not object_dir.exists():
                continue
            
            for obj_file in object_dir.iterdir():
                if obj_file.suffix != ".json":
                    continue
                
                try:
                    vnum = int(obj_file.stem)
                    obj_data = await self.world_service._load_json(obj_file)
                    
                    # Check if matches search query
                    searchable_text = " ".join([
                        obj_data.get("short_desc", ""),
                        obj_data.get("name", ""),
                        obj_data.get("description", "")
                    ]).lower()
                    
                    if query_lower in searchable_text:
                        entity = ObjectEntity(
                            vnum=vnum,
                            zone=zone.number,
                            name=obj_data.get("short_desc", f"Object {vnum}"),
                            type_flag=obj_data.get("type_flag", 0),
                            short_desc=obj_data.get("short_desc", ""),
                            description=obj_data.get("description"),
                            weight=obj_data.get("weight", 0),
                            cost=obj_data.get("cost", 0),
                            accessible=await self.world_service._check_object_accessibility(vnum)
                        )
                        
                        load_locations = await self.world_service.get_load_locations(vnum)
                        
                        results.append(SearchResult(
                            entity=entity,
                            load_locations=load_locations,
                            relevance_score=self._calculate_relevance(query_lower, searchable_text)
                        ))
                
                except Exception:
                    continue
        
        # Sort by relevance
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results
    
    async def _search_mobiles(self, request: SearchRequest) -> List[SearchResult]:
        """Search for mobiles"""
        results = []
        query_lower = request.query.lower()
        
        zones = await self.world_service.get_zones()
        
        for zone in zones:
            zone_path = self.world_service.config.get_zone_path(zone.number)
            mobile_dir = zone_path / "mobile"
            
            if not mobile_dir.exists():
                continue
            
            for mob_file in mobile_dir.iterdir():
                if mob_file.suffix != ".json":
                    continue
                
                try:
                    vnum = int(mob_file.stem)
                    mob_data = await self.world_service._load_json(mob_file)
                    
                    # Check if matches search query
                    searchable_text = " ".join([
                        mob_data.get("short_descr", ""),
                        mob_data.get("name", ""),
                        mob_data.get("long_descr", "")
                    ]).lower()
                    
                    if query_lower in searchable_text:
                        entity = MobileEntity(
                            vnum=vnum,
                            zone=zone.number,
                            name=mob_data.get("short_descr", f"Mobile {vnum}"),
                            level=mob_data.get("level", 1),
                            alignment=mob_data.get("alignment", 0),
                            race=mob_data.get("race"),
                            short_desc=mob_data.get("short_descr", ""),
                            long_desc=mob_data.get("long_descr"),
                            spec_proc=mob_data.get("spec_proc"),
                            accessible=await self.world_service._check_mobile_accessibility(vnum)
                        )
                        
                        results.append(SearchResult(
                            entity=entity,
                            load_locations=[],  # Mobiles don't have load locations
                            relevance_score=self._calculate_relevance(query_lower, searchable_text)
                        ))
                
                except Exception:
                    continue
        
        # Sort by relevance
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results
    
    def _calculate_relevance(self, query: str, text: str) -> float:
        """Calculate relevance score for search results"""
        if query == text:
            return 1.0
        
        if text.startswith(query):
            return 0.9
        
        if query in text:
            return 0.7
        
        # Count word matches
        query_words = query.split()
        text_words = text.split()
        matches = sum(1 for word in query_words if word in text_words)
        
        if matches > 0:
            return 0.5 + (matches / len(query_words)) * 0.2
        
        return 0.1