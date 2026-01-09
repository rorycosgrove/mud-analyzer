#!/usr/bin/env python3
"""
Test VNUM entity type detection
"""

import sys
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_vnum_detection():
    """Test that VNUMs are correctly differentiated between objects and mobiles"""
    from mud_analyzer.core.world_lookup import World
    from mud_analyzer.data_service import data_service
    from mud_analyzer.config import config
    
    print("🧪 Testing VNUM entity type detection...")
    
    # Setup
    config.setup_working_directory()
    world = World(config.project_root)
    
    # Find some test VNUMs
    test_vnums = []
    for zone_num in data_service.zones[:3]:  # Test first 3 zones
        zone_dir = config.project_root / str(zone_num)
        
        # Find an object VNUM
        obj_dir = zone_dir / "object"
        if obj_dir.exists():
            for obj_file in list(obj_dir.glob("*.json"))[:2]:
                vnum = int(obj_file.stem)
                test_vnums.append((vnum, "object", zone_num))
        
        # Find a mobile VNUM
        mob_dir = zone_dir / "mobile"
        if mob_dir.exists():
            for mob_file in list(mob_dir.glob("*.json"))[:2]:
                vnum = int(mob_file.stem)
                test_vnums.append((vnum, "mobile", zone_num))
        
        if len(test_vnums) >= 6:
            break
    
    if not test_vnums:
        print("⚠️ No test VNUMs found")
        return True
    
    print(f"📋 Testing {len(test_vnums)} VNUMs...")
    
    success_count = 0
    for vnum, expected_type, zone in test_vnums:
        # Test entity type detection
        detected_type = world.detect_entity_type(vnum)
        
        if detected_type == expected_type:
            print(f"✅ VNUM {vnum}: detected as {detected_type}")
            success_count += 1
        else:
            print(f"❌ VNUM {vnum}: expected {expected_type}, got {detected_type}")
        
        # Test brief description
        brief = world.get_entity_brief(vnum)
        if f"[{vnum}]" in brief and "unknown entity type" not in brief:
            print(f"   Brief: {brief[:60]}...")
        else:
            print(f"   ⚠️ Brief failed: {brief}")
        
        # Test data loading
        data = world.load_any(vnum)
        if data:
            print(f"   ✅ Data loaded successfully")
        else:
            print(f"   ❌ Failed to load data")
    
    print(f"\\n📊 Results: {success_count}/{len(test_vnums)} VNUMs correctly detected")
    return success_count == len(test_vnums)

def test_data_service_vnum():
    """Test data service VNUM methods"""
    from mud_analyzer.data_service import data_service
    
    print("\\n🧪 Testing data service VNUM methods...")
    
    # Get some test VNUMs
    objects = data_service.get_entities("object")
    mobiles = data_service.get_entities("mobile")
    
    if not objects and not mobiles:
        print("⚠️ No entities found for testing")
        return True
    
    test_cases = []
    if objects:
        test_cases.extend(list(objects.items())[:2])
    if mobiles:
        test_cases.extend(list(mobiles.items())[:2])
    
    success_count = 0
    for vnum, expected_entity in test_cases:
        # Test get_entity_by_vnum
        entity = data_service.get_entity_by_vnum(vnum)
        
        if entity and entity.vnum == vnum and entity.entity_type == expected_entity.entity_type:
            print(f"✅ VNUM {vnum}: correctly retrieved as {entity.entity_type}")
            success_count += 1
        else:
            print(f"❌ VNUM {vnum}: failed to retrieve correctly")
    
    print(f"📊 Results: {success_count}/{len(test_cases)} VNUMs correctly retrieved")
    return success_count == len(test_cases)

def main():
    """Run VNUM detection tests"""
    print("🏰 MUD Analyzer - VNUM Entity Type Detection Test")
    print("=" * 60)
    
    tests = [
        ("VNUM Detection Test", test_vnum_detection),
        ("Data Service VNUM Test", test_data_service_vnum),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n🔍 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All VNUM detection tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())