#!/usr/bin/env python3
"""
Test script to verify the fixes work correctly
"""

import sys
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported without errors"""
    try:
        from mud_analyzer.config import config
        print("✅ Config module imported successfully")
        
        from mud_analyzer.error_handler import handle_errors, log_error
        print("✅ Error handler module imported successfully")
        
        from mud_analyzer.cache_manager import cache_manager
        print("✅ Cache manager module imported successfully")
        
        from mud_analyzer.data_service import data_service
        print("✅ Data service module imported successfully")
        
        from mud_analyzer.base_explorer import BaseExplorer
        print("✅ Base explorer module imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration setup"""
    try:
        from mud_analyzer.config import config
        
        # Test project root detection
        print(f"Project root: {config.project_root}")
        
        # Test cache directory creation
        print(f"Cache directory: {config.cache_dir}")
        print(f"Cache directory exists: {config.cache_dir.exists()}")
        
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_error_handling():
    """Test error handling functionality"""
    try:
        from mud_analyzer.error_handler import safe_int, safe_str, validate_vnum
        
        # Test safe conversions
        assert safe_int("123") == 123
        assert safe_int("invalid", 42) == 42
        assert safe_str(None, "default") == "default"
        
        # Test validation
        assert validate_vnum("100") == 100
        
        print("✅ Error handling functions work correctly")
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing MUD Analyzer fixes...")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Config Tests", test_config),
        ("Error Handling Tests", test_error_handling),
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
        print("🎉 All tests passed! The fixes are working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())