# Armor of the Gods - Creation Guide

## Discovery Summary

The **Armor of the Gods** (VNUM: 19002) is a legendary item created through a special procedure, not traditional assembly. Here's what we discovered:

### Item Details
- **Name**: the Armor of the Gods
- **VNUM**: 19002
- **Zone**: 190 (but created in zone 180)
- **Type**: Armor (type 9)
- **Min Level**: 25
- **Weight**: 15

### Creation Method
- **Creator**: Kharas (VNUM: 18226) in Zone 180
- **Method**: Special procedure `mob_kharas`
- **Requirements**: Bring Kharas his hammer and materials
- **Status**: ✅ Possible to create

### Kharas Details
- **Location**: Zone 180
- **Description**: "Kharas was once a great metalsmith that forged mighty silver weapons. He would still make silver weapons for anybody except he has lost his hammer and only has one arm."
- **Level**: 39
- **Special Procedure**: mob_kharas

## Enhanced Assembled Items Functionality

The MUD Analyzer has been enhanced to detect and analyze script-created items like the Armor of the Gods:

### New Features Added

1. **Script-Created Items Detection**
   - Analyzes special procedures on mobiles
   - Scans scripts for item creation patterns
   - Identifies items created outside traditional assembly system

2. **Enhanced Assembled Items Explorer**
   - New menu option: "Browse All Creatable Items" - shows both assembled and script-created items
   - New menu option: "Browse Script-Created Items" - shows only script-created items
   - Unified display format with creation type indicators

3. **Detailed Investigation Tools**
   - "Investigate creator" option shows mobile/script details
   - Special procedure information display
   - Creator zone and method tracking

### How to Use

1. Run MUD Analyzer: `python main.py`
2. Select "5. 🔧 Assembled Items Explorer"
3. Choose from new options:
   - Option 4: "🔧 Browse All Creatable Items" (includes script items)
   - Option 5: "⚙️ Browse Script-Created Items" (script items only)

### Technical Implementation

- **New Module**: `script_created_items.py` - Dedicated script item analysis
- **Enhanced Module**: `assembled_items_refactored.py` - Integrated both types
- **Detection Logic**: 
  - Scans for special procedures on mobiles
  - Analyzes script text for item creation patterns
  - Maintains known items database (expandable)

### Known Script-Created Items

Currently detected:
1. **Armor of the Gods** (19002) - Created by Kharas (18226) via mob_kharas special procedure

The system is designed to be expandable - additional script-created items can be added as they're discovered.

## Usage Examples

### Finding the Armor of the Gods
```
Main Menu → 5. Assembled Items Explorer → 5. Browse Script-Created Items → 1. Armor of the Gods
```

### Investigating Kharas
```
Script-Created Items → Select Armor of the Gods → i. Investigate creator
```

### Viewing All Creatable Items
```
Main Menu → 5. Assembled Items Explorer → 4. Browse All Creatable Items
```

This enhancement makes the MUD Analyzer the first tool to comprehensively track ALL methods of item creation in AddictMUD, not just traditional assemblies!