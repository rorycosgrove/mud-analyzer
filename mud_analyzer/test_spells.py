#!/usr/bin/env python3
"""
Test spell loading functionality
"""

import sys
from pathlib import Path
import os

# Add parent directory to path and change working directory
sys.path.insert(0, str(Path(__file__).parent.parent))
os.chdir(Path(__file__).parent.parent)

from mud_analyzer.utils.spell_lookup import load_spell_name_map, spell_name


def test_spell_loading():
    print("🧪 Testing Spell Loading")
    print("=" * 30)
    
    # Load spell map
    spell_map = load_spell_name_map()
    
    print(f"📊 Total spells loaded: {len(spell_map)}")
    
    if spell_map:
        print("\n🔍 Sample spells:")
        for i, (spell_id, name) in enumerate(list(spell_map.items())[:10]):
            print(f"  {spell_id}: {name}")
        
        if len(spell_map) > 10:
            print(f"  ... and {len(spell_map) - 10} more")
        
        # Test spell_name function
        print(f"\n🧙 Test lookups:")
        test_ids = [1, 5, 10, 999999]
        for test_id in test_ids:
            result = spell_name(test_id, spell_map)
            print(f"  spell_name({test_id}) = '{result}'")
    
    else:
        print("❌ No spells loaded!")
        
        # Check file locations
        print("\n🔍 Checking file locations:")
        data_path = Path("mud_analyzer/data/spells.json")
        cwd_path = Path("spells.json")
        
        print(f"  {data_path}: {'✅ EXISTS' if data_path.exists() else '❌ NOT FOUND'}")
        print(f"  {cwd_path}: {'✅ EXISTS' if cwd_path.exists() else '❌ NOT FOUND'}")


if __name__ == "__main__":
    test_spell_loading()