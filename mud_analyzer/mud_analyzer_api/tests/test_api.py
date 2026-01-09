"""
Test suite for MUD Analyzer API
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from mud_analyzer_api.config import Config
from mud_analyzer_api.core.world_service import WorldService
from mud_analyzer_api.core.search_service import SearchService
from mud_analyzer_api.core.assembly_service import AssemblyService
from mud_analyzer_api.models.entities import (
    SearchRequest, EntityType, AssemblyRequest,
    ObjectEntity, MobileEntity, AccessibilityStatus
)


@pytest.fixture
def config():
    """Test configuration"""
    return Config(
        world_root=Path("/test/world"),
        cache_dir=Path("/test/cache"),
        debug=True
    )


@pytest.fixture
def world_service(config):
    """Test world service"""
    return WorldService(config)


@pytest.fixture
def search_service(world_service):
    """Test search service"""
    return SearchService(world_service)


@pytest.fixture
def assembly_service(world_service):
    """Test assembly service"""
    return AssemblyService(world_service)


class TestWorldService:
    """Test world service functionality"""
    
    @pytest.mark.asyncio
    async def test_get_zones(self, world_service):
        """Test getting zone list"""
        with patch.object(world_service.config.world_root, 'iterdir') as mock_iterdir:
            # Mock zone directories
            zone_dir = Mock()
            zone_dir.is_dir.return_value = True
            zone_dir.name = "100"
            
            zone_file = Mock()
            zone_file.exists.return_value = True
            zone_dir.__truediv__.return_value = zone_file
            
            mock_iterdir.return_value = [zone_dir]
            
            # Mock JSON loading
            with patch.object(world_service, '_load_json', new_callable=AsyncMock) as mock_load:
                mock_load.return_value = {
                    "name": "Test Zone",
                    "author": "Test Author"
                }
                
                zones = await world_service.get_zones()
                
                assert len(zones) == 1
                assert zones[0].number == 100
                assert zones[0].name == "Test Zone"
                assert zones[0].author == "Test Author"
    
    @pytest.mark.asyncio
    async def test_get_object_details(self, world_service):
        """Test getting object details"""
        with patch.object(world_service, '_find_entity_zone', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = 100
            
            with patch.object(world_service, '_load_json', new_callable=AsyncMock) as mock_load:
                mock_load.return_value = {
                    "short_desc": "a test sword",
                    "type_flag": 5,
                    "weight": 10,
                    "cost": 100
                }
                
                with patch.object(world_service, '_check_object_accessibility', new_callable=AsyncMock) as mock_check:
                    mock_check.return_value = AccessibilityStatus.ACCESSIBLE
                    
                    obj = await world_service.get_object_details(10001)
                    
                    assert obj.vnum == 10001
                    assert obj.zone == 100
                    assert obj.name == "a test sword"
                    assert obj.type_flag == 5
                    assert obj.accessible == AccessibilityStatus.ACCESSIBLE
    
    @pytest.mark.asyncio
    async def test_get_mobile_details(self, world_service):
        """Test getting mobile details"""
        with patch.object(world_service, '_find_entity_zone', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = 100
            
            with patch.object(world_service, '_load_json', new_callable=AsyncMock) as mock_load:
                mock_load.return_value = {
                    "short_descr": "a test guard",
                    "level": 25,
                    "alignment": 0,
                    "spec_proc": "guard_proc"
                }
                
                with patch.object(world_service, '_check_mobile_accessibility', new_callable=AsyncMock) as mock_check:
                    mock_check.return_value = AccessibilityStatus.ACCESSIBLE
                    
                    mob = await world_service.get_mobile_details(10001)
                    
                    assert mob.vnum == 10001
                    assert mob.zone == 100
                    assert mob.name == "a test guard"
                    assert mob.level == 25
                    assert mob.spec_proc == "guard_proc"
                    assert mob.accessible == AccessibilityStatus.ACCESSIBLE


class TestSearchService:
    """Test search service functionality"""
    
    @pytest.mark.asyncio
    async def test_search_objects(self, search_service):
        """Test object search"""
        request = SearchRequest(
            query="sword",
            entity_type=EntityType.OBJECT,
            limit=10
        )
        
        with patch.object(search_service.world_service, 'get_zones', new_callable=AsyncMock) as mock_zones:
            mock_zones.return_value = [Mock(number=100)]
            
            with patch.object(search_service, '_search_objects', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = [
                    Mock(entity=Mock(accessible=AccessibilityStatus.ACCESSIBLE), relevance_score=0.9)
                ]
                
                results = await search_service.search_entities(request)
                
                assert len(results) == 1
                mock_search.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_search_with_accessibility_filter(self, search_service):
        """Test search with accessibility filter"""
        request = SearchRequest(
            query="sword",
            entity_type=EntityType.OBJECT,
            accessible_only=True,
            limit=10
        )
        
        with patch.object(search_service, '_search_objects', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                Mock(entity=Mock(accessible=AccessibilityStatus.ACCESSIBLE)),
                Mock(entity=Mock(accessible=AccessibilityStatus.INACCESSIBLE))
            ]
            
            results = await search_service.search_entities(request)
            
            assert len(results) == 1
            assert results[0].entity.accessible == AccessibilityStatus.ACCESSIBLE


class TestAssemblyService:
    """Test assembly service functionality"""
    
    @pytest.mark.asyncio
    async def test_analyze_assemblies(self, assembly_service):
        """Test assembly analysis"""
        request = AssemblyRequest(
            accessible_only=True,
            min_success_rate=50.0
        )
        
        with patch.object(assembly_service, '_get_assembled_items', new_callable=AsyncMock) as mock_assembled:
            mock_assembled.return_value = [
                Mock(accessible=True, success_rate=75.0),
                Mock(accessible=False, success_rate=25.0)
            ]
            
            with patch.object(assembly_service, '_get_script_created_items', new_callable=AsyncMock) as mock_script:
                mock_script.return_value = [
                    Mock(accessible=True, success_rate=100.0)
                ]
                
                results = await assembly_service.analyze_assemblies(request)
                
                assert len(results) == 2  # Only accessible items with success_rate >= 50%
                assert all(item.accessible for item in results)
                assert all(item.success_rate >= 50.0 for item in results)
    
    @pytest.mark.asyncio
    async def test_get_script_created_items(self, assembly_service):
        """Test script-created items detection"""
        with patch.object(assembly_service.world_service, 'get_mobile_details', new_callable=AsyncMock) as mock_mobile:
            mock_mobile.return_value = Mock(accessible=AccessibilityStatus.ACCESSIBLE)
            
            with patch.object(assembly_service, '_find_script_created_items', new_callable=AsyncMock) as mock_find:
                mock_find.return_value = []
                
                items = await assembly_service._get_script_created_items()
                
                assert len(items) >= 1  # At least the known Armor of the Gods
                armor_item = next((item for item in items if item.result_vnum == 19002), None)
                assert armor_item is not None
                assert armor_item.result_name == "the Armor of the Gods"
                assert armor_item.creation_method == "script"


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_search_workflow(self, world_service, search_service):
        """Test complete search workflow"""
        # This would require actual test data files
        # For now, just test that the services integrate properly
        
        request = SearchRequest(
            query="test",
            entity_type=EntityType.OBJECT,
            accessible_only=False,
            limit=5
        )
        
        # Mock the underlying data access
        with patch.object(world_service, 'get_zones', new_callable=AsyncMock) as mock_zones:
            mock_zones.return_value = []
            
            results = await search_service.search_entities(request)
            assert isinstance(results, list)


if __name__ == "__main__":
    pytest.main([__file__])