#!/usr/bin/env python3
"""
Project Status Checker - Verify MUD Analyzer setup and diagnose issues
"""

import sys
from pathlib import Path
import json

# Add parent directory to path for package imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mud_analyzer.shared.config import config


class ProjectStatusChecker:
    """Check project setup and diagnose common issues"""
    
    def __init__(self):
        config.setup_working_directory()
        self.issues = []
        self.warnings = []
        self.stats = {}
    
    def run_full_check(self):
        """Run comprehensive project status check"""
        print("🔍 MUD ANALYZER PROJECT STATUS CHECK")
        print("=" * 60)
        
        self.check_directory_structure()
        self.check_zone_files()
        self.check_cache_status()
        self.check_dependencies()
        
        self.show_summary()
    
    def check_directory_structure(self):
        """Check basic directory structure"""
        print("\n📁 Checking directory structure...")
        
        # Check if we're in the right place
        current_dir = Path.cwd()
        print(f"   Current directory: {current_dir}")
        
        # Look for zone directories
        zone_dirs = [d for d in current_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        
        if not zone_dirs:
            self.issues.append("No zone directories found (numbered folders like 100, 200, etc.)")
        else:
            print(f"   ✅ Found {len(zone_dirs)} zone directories")
            self.stats['zone_count'] = len(zone_dirs)
        
        # Check mud_analyzer directory
        analyzer_dir = current_dir / "mud_analyzer"
        if not analyzer_dir.exists():
            self.issues.append("mud_analyzer directory not found")
        else:
            print("   ✅ mud_analyzer directory found")
    
    def check_zone_files(self):
        """Check zone file structure and content"""
        print("\n🏰 Checking zone files...")
        
        current_dir = Path.cwd()
        zone_dirs = sorted([d for d in current_dir.iterdir() if d.is_dir() and d.name.isdigit()])
        
        if not zone_dirs:
            return
        
        total_entities = {'room': 0, 'mobile': 0, 'object': 0, 'script': 0, 'assemble': 0}
        zones_with_data = 0
        
        for zone_dir in zone_dirs[:10]:  # Check first 10 zones
            zone_num = int(zone_dir.name)
            has_data = False
            
            # Check zone.json
            zone_file = zone_dir / f"{zone_num}.json"
            if zone_file.exists():
                try:
                    with open(zone_file, 'r') as f:
                        zone_data = json.load(f)
                    has_data = True
                except Exception as e:
                    self.warnings.append(f"Zone {zone_num}: Invalid zone.json - {e}")
            
            # Check entity directories
            for entity_type in ['room', 'mobile', 'object', 'script', 'assemble']:
                entity_dir = zone_dir / entity_type
                if entity_dir.exists():
                    entity_files = [f for f in entity_dir.iterdir() if f.suffix == '.json']
                    total_entities[entity_type] += len(entity_files)
                    if entity_files:
                        has_data = True
            
            if has_data:
                zones_with_data += 1
        
        print(f"   ✅ Zones with data: {zones_with_data}/{len(zone_dirs)}")
        
        for entity_type, count in total_entities.items():
            if count > 0:
                print(f"   📊 {entity_type.title()}s: {count}")
                self.stats[f'{entity_type}_count'] = count
        
        if zones_with_data == 0:
            self.issues.append("No zones contain valid data files")
        elif zones_with_data < len(zone_dirs) / 2:
            self.warnings.append(f"Only {zones_with_data}/{len(zone_dirs)} zones contain data")
    
    def check_cache_status(self):
        """Check cache directory and files"""
        print("\n💾 Checking cache status...")
        
        cache_dir = Path("mud_analyzer/cache")
        if not cache_dir.exists():
            print("   ℹ️ No cache directory (will be created on first run)")
            return
        
        cache_files = list(cache_dir.glob("*.pkl"))
        if cache_files:
            print(f"   ✅ Found {len(cache_files)} cache files")
            for cache_file in cache_files:
                size_mb = cache_file.stat().st_size / (1024 * 1024)
                print(f"      - {cache_file.name}: {size_mb:.1f} MB")
        else:
            print("   ℹ️ No cache files (will be created on first run)")
    
    def check_dependencies(self):
        """Check Python dependencies and modules"""
        print("\n🐍 Checking dependencies...")
        
        try:
            import json
            print("   ✅ json module available")
        except ImportError:
            self.issues.append("json module not available")
        
        try:
            from pathlib import Path
            print("   ✅ pathlib module available")
        except ImportError:
            self.issues.append("pathlib module not available")
        
        # Check MUD Analyzer modules
        try:
            from mud_analyzer.core.world_lookup import World
            print("   ✅ MUD Analyzer core modules available")
        except ImportError as e:
            self.issues.append(f"MUD Analyzer modules not available: {e}")
    
    def show_summary(self):
        """Show summary of check results"""
        print("\n" + "=" * 60)
        print("📋 STATUS SUMMARY")
        print("=" * 60)
        
        if not self.issues and not self.warnings:
            print("✅ ALL CHECKS PASSED!")
            print("   Your MUD Analyzer setup appears to be working correctly.")
        else:
            if self.issues:
                print("❌ CRITICAL ISSUES FOUND:")
                for issue in self.issues:
                    print(f"   • {issue}")
            
            if self.warnings:
                print("\n⚠️ WARNINGS:")
                for warning in self.warnings:
                    print(f"   • {warning}")
        
        if self.stats:
            print(f"\n📊 PROJECT STATISTICS:")
            if 'zone_count' in self.stats:
                print(f"   🏰 Zones: {self.stats['zone_count']}")
            
            entity_types = ['room', 'mobile', 'object', 'script', 'assemble']
            for entity_type in entity_types:
                key = f'{entity_type}_count'
                if key in self.stats:
                    icon = {'room': '🏠', 'mobile': '👹', 'object': '📦', 'script': '📜', 'assemble': '🔧'}[entity_type]
                    print(f"   {icon} {entity_type.title()}s: {self.stats[key]}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if self.issues:
            print("   • Fix critical issues before using MUD Analyzer")
            print("   • Check that you're in the correct AddictMUD world directory")
            print("   • Verify zone files are properly formatted JSON")
        else:
            print("   • Run MUD Analyzer with 'python mud_analyzer/main.py'")
            print("   • Use the help system (option 7) for usage guidance")
            print("   • Start with Zone Browser to explore available content")


def main():
    checker = ProjectStatusChecker()
    checker.run_full_check()
    input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()