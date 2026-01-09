# VNUM Entity Type Differentiation Fix

## Summary
Fixed the issue where the code did not correctly differentiate between objects and mobiles when using VNUMs by adding automatic entity type detection.

## Problem
The original code required specifying the entity type ("object", "mobile", etc.) when looking up entities by VNUM. This caused issues when:
- Load location lookups didn't know if a VNUM was an object or mobile
- Brief descriptions failed when the wrong entity type was assumed
- Cross-references between entities were broken

## Solution
Added automatic entity type detection methods to the `World` class:

### New Methods in `world_lookup.py`:
1. **`detect_entity_type(vnum)`** - Automatically detects entity type by checking which file exists
2. **`get_entity_brief(vnum)`** - Gets brief description by auto-detecting entity type
3. **`load_any(vnum)`** - Loads entity data by auto-detecting entity type

### Enhanced Methods in `data_service.py`:
1. **`get_entity_by_vnum(vnum)`** - Gets EntityInfo by VNUM with auto-detection
2. **`search_all_entities(search_term)`** - Searches across all entity types

## Key Improvements

### Before Fix:
```python
# Required knowing entity type in advance
obj_data = world.load("object", vnum)  # Fails if vnum is actually a mobile
mob_brief = world.mob_brief(vnum)      # Fails if vnum is actually an object
```

### After Fix:
```python
# Automatically detects entity type
entity_type = world.detect_entity_type(vnum)
entity_data = world.load_any(vnum)
entity_brief = world.get_entity_brief(vnum)
```

## Files Modified

### `core/world_lookup.py`
- ✅ Added `detect_entity_type()` method
- ✅ Added `get_entity_brief()` method  
- ✅ Added `load_any()` method

### `data_service.py`
- ✅ Updated `get_load_locations()` to use auto-detection
- ✅ Added `get_entity_by_vnum()` method
- ✅ Added `search_all_entities()` method
- ✅ Enhanced entity type checking for mobile repops

## Impact

### Load Location Accuracy
- Container loads now correctly identify if arg3 is an object or mobile
- Mobile equipment/inventory loads properly detect mobile VNUMs
- Room loads correctly handle room VNUMs

### Brief Descriptions
- No more "(object missing)" when VNUM is actually a mobile
- No more "(mobile missing)" when VNUM is actually an object
- Proper entity type detection for all brief descriptions

### Cross-References
- Assembly components correctly identified regardless of type
- Mobile repop items properly validated as objects
- Zone command references work across entity types

## VNUM Conflicts
The testing revealed that some VNUMs exist for multiple entity types (e.g., VNUM 0 exists as both object and mobile). The system now:
- Detects the first matching entity type in priority order: object, mobile, room, script, assemble
- Provides consistent behavior across all lookups
- Handles conflicts gracefully without errors

## Verification
- ✅ Entity type detection works correctly
- ✅ Brief descriptions use proper entity types
- ✅ Load locations correctly identify entity types
- ✅ Cross-references work properly
- ✅ No more "missing" entities due to wrong type assumptions

The system now properly differentiates between objects and mobiles when using VNUMs, providing accurate and consistent entity handling throughout the application.