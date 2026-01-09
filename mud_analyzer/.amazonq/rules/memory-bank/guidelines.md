# MUD Analyzer - Development Guidelines

## Code Quality Standards

### Documentation Standards
- **Module Headers**: All modules start with triple-quoted docstrings explaining purpose and usage
- **Function Documentation**: Complex functions include docstrings with parameter and return descriptions
- **Inline Comments**: Strategic comments explain business logic, especially MUD-specific concepts
- **Type Annotations**: Extensive use of type hints with `from __future__ import annotations`

### Code Formatting Patterns
- **Shebang Lines**: All executable files start with `#!/usr/bin/env python3`
- **Import Organization**: Standard library imports first, then relative imports with explicit paths
- **Line Length**: Generally follows PEP 8 with reasonable line breaks for readability
- **String Formatting**: Consistent use of f-strings for string interpolation

### Error Handling Conventions
- **Defensive Programming**: Extensive use of try-except blocks with graceful degradation
- **Safe Type Conversion**: Custom `safe_int()` and `parse_int()` functions for robust data parsing
- **Null Checks**: Consistent checking for None values and empty collections
- **Error Recovery**: Functions return sensible defaults rather than crashing

## Structural Conventions

### Class Design Patterns
- **Initialization**: Classes initialize with configuration setup and lazy loading patterns
- **Method Organization**: Public interface methods first, followed by private helper methods
- **State Management**: Instance variables for caching with clear naming conventions
- **Resource Management**: Proper cleanup and cache management

### Function Naming Conventions
- **Public Methods**: Descriptive names like `load_all_assembles()`, `analyze_accessibility()`
- **Private Methods**: Underscore prefix like `_ensure_assembles_loaded()`, `_build_zone_command_index()`
- **Helper Functions**: Utility functions with clear purpose like `_safe_listdir()`, `_read_json()`
- **Brief Methods**: Consistent naming pattern for entity descriptions: `obj_brief()`, `mob_brief()`, `room_brief()`

### Variable Naming Standards
- **Cache Variables**: Descriptive names with `_cache` suffix like `_accessibility_cache`, `_part_cache`
- **Configuration**: Clear names like `zone_num`, `vnum`, `spell_map`
- **Collections**: Plural names for lists/sets like `assembles`, `referenced_mobs`, `referenced_objs`
- **Flags**: Boolean variables with clear intent like `all_parts_loadable`, `zone_accessible`

## Semantic Patterns

### Data Loading Patterns
```python
# Lazy loading with cache checking
def _ensure_assembles_loaded(self):
    if not self.assembles:
        print("Loading assembled items data...")
        self.load_all_assembles()

# Cache-first loading pattern
cached_data = cache_manager.load_from_cache("assembled_items")
if cached_data is not None:
    self.assembles = cached_data['assembles']
    return
```

### Menu System Patterns
```python
# Consistent menu structure
while True:
    print(f"\n🔧 ASSEMBLED ITEMS EXPLORER")
    print("=" * 50)
    print("1. ✅ Browse Possible Items")
    print("0. ← Back to Main Menu")
    
    choice = input("\n➤ Select option: ").strip()
    if choice == "0":
        break
```

### Pagination Implementation
```python
# Standard pagination pattern
page = 0
page_size = 12
start_idx = page * page_size
end_idx = min(start_idx + page_size, len(items))

# Navigation controls
if choice == "n" and end_idx < len(items):
    page += 1
elif choice == "p" and page > 0:
    page -= 1
```

### Data Analysis Patterns
```python
# Entity analysis with caching
def analyze_accessibility(self, recipe):
    cache_key = f"{recipe['zone']}_{recipe['result_vnum']}"
    if cache_key in self._accessibility_cache:
        return self._accessibility_cache[cache_key]
    
    # Perform analysis
    analysis = {'zone_accessible': True, 'all_parts_loadable': True}
    self._accessibility_cache[cache_key] = analysis
    return analysis
```

## Internal API Usage Patterns

### World Lookup Integration
```python
# Standard entity brief generation
result_brief = self.world.obj_brief(recipe['result_vnum'])
mob_brief = self.world.mob_brief(current_mobile)
room_brief = self.world.room_brief(arg3)

# Entity loading with fallback
zone_data = self.world.load_zone(zone_num)
if not zone_data or "cmds" not in zone_data:
    return locations_with_rates
```

### Cache Manager Usage
```python
# Save complex data structures
cache_data = {
    'assembles': self.assembles,
    'accessibility': self._accessibility_cache,
    'command_index': self._zone_command_index
}
cache_manager.save_to_cache("assembled_items", cache_data)

# Clear specific caches
cache_manager.clear_cache("assembled_items")
```

### Configuration Access
```python
# Path resolution through config
zone_path = config.project_root / str(zone_num)
assemble_dir = config.project_root / str(zone_num) / "assemble"

# Working directory setup
config.setup_working_directory()
```

## Frequently Used Code Idioms

### Safe Data Extraction
```python
# Safe integer conversion with defaults
vnum = safe_int(assemble_data.get('vnum', 0))
prob = safe_int(cmd.get('prob', 100))

# Safe list comprehension with filtering
parts = [safe_int(p) for p in parts if safe_int(p) > 0]
```

### File System Operations
```python
# Safe directory listing
def _safe_listdir(p: Path) -> List[Path]:
    try:
        return sorted([x for x in p.iterdir() if x.is_file()])
    except Exception:
        return []

# Safe JSON reading
def _read_json(p: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
```

### Status Display Patterns
```python
# Consistent status indicators
status = "✅" if accessibility['all_parts_loadable'] else "❌"
if accessibility['overall_rate'] >= 100:
    status = "✅"
else:
    status = f"⚠️  {accessibility['overall_rate']:.0f}%"

# Progress messages
print(f"✅ Loaded {len(self.assembles)} assembled items from cache")
print(f"Found {len(possible_items)} possible items out of {len(self.assembles)}")
```

### Data Structure Patterns
```python
# Command indexing structure
self._zone_command_index[arg1].append({
    'zone': zone_num,
    'cmd_type': cmd_type,
    'arg1': arg1,
    'prob': prob,
    'mobile_context': current_mobile
})

# Analysis result structure
analysis = {
    'zone_accessible': self.is_zone_accessible(recipe['zone']),
    'all_parts_loadable': True,
    'overall_rate': 100.0,
    'parts': {}
}
```

## Popular Annotations

### Type Hints Usage
```python
from typing import Any, Dict, List, Optional, Set, Tuple
from __future__ import annotations

# Function signatures
def render_resets(world: World, zone_cmds: List[Dict[str, Any]], 
                 referenced_mobs: Set[int], referenced_objs: Set[int]) -> str:

# Class attributes
_cache: Dict[Tuple[str, int], Optional[Dict[str, Any]]] = field(default_factory=dict)
_zone_ranges: List[Tuple[int, int, int]] = field(default_factory=list)
```

### Dataclass Usage
```python
from dataclasses import dataclass, field

@dataclass
class World:
    root: Path
    hint_zone: Optional[int] = None
    _cache: Dict[Tuple[str, int], Optional[Dict[str, Any]]] = field(default_factory=dict)
```

### Error Handling Decorators
```python
from mud_analyzer.error_handler import handle_errors

@handle_errors()
def load_all_assembles(self):
    # Method implementation with automatic error handling
```