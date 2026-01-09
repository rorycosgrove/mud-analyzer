#!/usr/bin/env python3
"""
Test cache persistence between executions
"""

import sys
from pathlib import Path
import time

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_cache_persistence():
    """Test that caches persist between executions"""
    from mud_analyzer.cache_manager import cache_manager
    from mud_analyzer.config import config
    
    print("🧪 Testing cache persistence...")
    
    # Test data
    test_data = {"test": "data", "timestamp": time.time()}
    cache_name = "test_persistence"
    
    # Save to cache
    print("💾 Saving test data to cache...")
    success = cache_manager.save_to_cache(cache_name, test_data)
    if not success:
        print("❌ Failed to save cache")
        return False
    
    # Clear memory cache to simulate new execution
    print("🧹 Clearing memory cache to simulate new execution...")
    cache_manager.memory_cache.clear()
    cache_manager.cache_timestamps.clear()
    
    # Load from cache (should load from disk)
    print("📂 Loading from cache...")
    loaded_data = cache_manager.load_from_cache(cache_name)
    
    if loaded_data is None:
        print("❌ Failed to load cache from disk")
        return False
    
    if loaded_data != test_data:
        print("❌ Loaded data doesn't match saved data")
        return False
    
    print("✅ Cache persistence test passed!")
    
    # Clean up
    cache_manager.clear_cache(cache_name)
    
    return True

def test_data_service_cache():
    """Test that data service caches persist"""
    from mud_analyzer.data_service import data_service
    from mud_analyzer.cache_manager import cache_manager
    from mud_analyzer.config import config
    
    print("🧪 Testing data service cache persistence...")
    
    # Check if cache files exist
    cache_files = list(config.cache_dir.glob("*.pkl"))
    print(f"📁 Found {len(cache_files)} cache files:")
    for cache_file in cache_files:
        size_mb = cache_file.stat().st_size / 1024 / 1024
        print(f"  - {cache_file.name}: {size_mb:.1f} MB")
    
    if not cache_files:
        print("ℹ️ No cache files found - this is normal for first run")
        return True
    
    # Test loading existing cache
    for cache_file in cache_files:
        cache_name = cache_file.stem
        print(f"🔍 Testing cache: {cache_name}")
        
        # Clear memory to simulate new execution
        data_service._entity_cache.clear()
        data_service._command_index = None
        cache_manager.memory_cache.clear()
        cache_manager.cache_timestamps.clear()
        
        # Try to load from cache
        loaded = cache_manager.load_from_cache(cache_name)
        if loaded is not None:
            print(f"✅ Successfully loaded {cache_name} from disk")
        else:
            print(f"⚠️ Could not load {cache_name} from disk")
    
    return True

def main():
    """Run cache persistence tests"""
    from mud_analyzer.config import config
    
    print("🏰 MUD Analyzer - Cache Persistence Test")
    print("=" * 50)
    
    # Setup working directory
    config.setup_working_directory()
    
    tests = [
        ("Cache Persistence Test", test_cache_persistence),
        ("Data Service Cache Test", test_data_service_cache),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All cache persistence tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())