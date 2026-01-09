"""
Assembly Service - Assembled and script-created items analysis
"""

import json
from typing import List, Dict, Any
from pathlib import Path

from ..models.entities import AssemblyRequest, AssemblyItem, AccessibilityStatus
from ..core.world_service import WorldService


class AssemblyService:
    """Service for analyzing assembled and script-created items"""
    
    def __init__(self, world_service: WorldService):
        self.world_service = world_service
    
    async def analyze_assemblies(self, request: AssemblyRequest) -> List[AssemblyItem]:
        """Analyze assembled items based on request criteria"""
        results = []
        
        # Get traditional assembled items
        assembled_items = await self._get_assembled_items()
        results.extend(assembled_items)
        
        # Get script-created items
        script_items = await self._get_script_created_items()
        results.extend(script_items)
        
        # Apply filters
        if request.accessible_only:
            results = [item for item in results if item.accessible]
        
        if request.min_success_rate > 0:
            results = [item for item in results if item.success_rate >= request.min_success_rate]
        
        if request.zone_filter:
            results = [item for item in results if item.zone in request.zone_filter]
        
        # Sort by success rate (descending)
        results.sort(key=lambda x: x.success_rate, reverse=True)
        
        return results
    
    async def _get_assembled_items(self) -> List[AssemblyItem]:
        """Get traditional assembled items"""
        items = []
        zones = await self.world_service.get_zones()
        
        for zone in zones:
            zone_path = self.world_service.config.get_zone_path(zone.number)
            assemble_dir = zone_path / "assemble"
            
            if not assemble_dir.exists():
                continue
            
            for assemble_file in assemble_dir.iterdir():
                if assemble_file.suffix != ".json":
                    continue
                
                try:
                    assemble_data = await self.world_service._load_json(assemble_file)
                    
                    result_vnum = assemble_data.get("vnum", 0)
                    parts = assemble_data.get("parts", [])
                    
                    if result_vnum > 0 and parts:
                        # Get result item name
                        try:
                            result_obj = await self.world_service.get_object_details(result_vnum)
                            result_name = result_obj.name
                        except:
                            result_name = f"Object {result_vnum}"
                        
                        # Calculate accessibility and success rate
                        accessibility_info = await self._analyze_assembly_accessibility(parts)
                        
                        items.append(AssemblyItem(
                            result_vnum=result_vnum,
                            result_name=result_name,
                            zone=zone.number,
                            parts=parts,
                            success_rate=accessibility_info["success_rate"],
                            accessible=accessibility_info["accessible"],
                            creation_method="assembly",
                            requirements=f"Assemble {len(parts)} parts"
                        ))
                
                except Exception:
                    continue
        
        return items
    
    async def _get_script_created_items(self) -> List[AssemblyItem]:
        """Get script-created items"""
        items = []
        
        # Known script-created items (can be expanded)
        known_items = [
            {
                "result_vnum": 19002,
                "result_name": "the Armor of the Gods",
                "zone": 180,
                "creator_vnum": 18226,
                "creator_name": "Kharas",
                "requirements": "Bring Kharas his hammer and materials"
            }
        ]
        
        for item_info in known_items:
            # Check if creator is accessible
            try:
                creator = await self.world_service.get_mobile_details(item_info["creator_vnum"])
                accessible = creator.accessible == AccessibilityStatus.ACCESSIBLE
            except:
                accessible = False
            
            items.append(AssemblyItem(
                result_vnum=item_info["result_vnum"],
                result_name=item_info["result_name"],
                zone=item_info["zone"],
                parts=[],  # Script items don't have traditional parts
                success_rate=100.0 if accessible else 0.0,
                accessible=accessible,
                creation_method="script",
                requirements=item_info["requirements"]
            ))
        
        # Look for additional script-created items
        additional_items = await self._find_script_created_items()
        items.extend(additional_items)
        
        return items
    
    async def _find_script_created_items(self) -> List[AssemblyItem]:
        """Find additional script-created items by analyzing special procedures"""
        items = []
        zones = await self.world_service.get_zones()
        
        for zone in zones:
            zone_path = self.world_service.config.get_zone_path(zone.number)
            
            # Find mobiles with special procedures
            mobile_dir = zone_path / "mobile"
            if not mobile_dir.exists():
                continue
            
            for mob_file in mobile_dir.iterdir():
                if mob_file.suffix != ".json":
                    continue
                
                try:
                    mob_data = await self.world_service._load_json(mob_file)
                    spec_proc = mob_data.get("spec_proc")
                    
                    if spec_proc:
                        vnum = int(mob_file.stem)
                        
                        # Check if mobile is accessible
                        try:
                            mobile = await self.world_service.get_mobile_details(vnum)
                            if mobile.accessible != AccessibilityStatus.ACCESSIBLE:
                                continue
                        except:
                            continue
                        
                        # Look for objects in same zone that don't have load locations
                        object_dir = zone_path / "object"
                        if object_dir.exists():
                            for obj_file in object_dir.iterdir():
                                if obj_file.suffix != ".json":
                                    continue
                                
                                try:
                                    obj_vnum = int(obj_file.stem)
                                    
                                    # Check if object has load locations
                                    locations = await self.world_service.get_load_locations(obj_vnum)
                                    if not locations:
                                        # Might be script-created
                                        try:
                                            obj = await self.world_service.get_object_details(obj_vnum)
                                            items.append(AssemblyItem(
                                                result_vnum=obj_vnum,
                                                result_name=obj.name,
                                                zone=zone.number,
                                                parts=[],
                                                success_rate=100.0,
                                                accessible=True,
                                                creation_method="script",
                                                requirements=f"Interact with {mob_data.get('short_descr', 'mobile')}"
                                            ))
                                        except:
                                            continue
                                
                                except:
                                    continue
                
                except Exception:
                    continue
        
        return items
    
    async def _analyze_assembly_accessibility(self, parts: List[int]) -> Dict[str, Any]:
        """Analyze accessibility of assembly parts"""
        if not parts:
            return {"accessible": False, "success_rate": 0.0}
        
        overall_rate = 1.0
        all_accessible = True
        
        for part_vnum in parts:
            try:
                locations = await self.world_service.get_load_locations(part_vnum)
                
                if not locations:
                    all_accessible = False
                    overall_rate = 0.0
                    break
                
                # Get best probability for this part
                best_prob = max(loc.probability for loc in locations)
                overall_rate *= (best_prob / 100.0)
                
            except Exception:
                all_accessible = False
                overall_rate = 0.0
                break
        
        return {
            "accessible": all_accessible,
            "success_rate": overall_rate * 100.0
        }