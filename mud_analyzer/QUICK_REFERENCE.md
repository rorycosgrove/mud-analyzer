# MUD Analyzer - Refactoring Quick Reference

## What Changed?

✅ **Project reorganized** into 3 new logical directories:
- `api/` - Modern API servers (REST + MCP)
- `legacy/` - Interactive CLI (preserved)
- `shared/` - Shared utilities (config, errors, cache)

## Directory Changes

### Moved to `legacy/` (10 files)
```
main.py, menu.py, base_explorer.py, help_system.py,
zone_explorer.py, zone_browser.py*, global_search.py*,
script_created_items.py, assembled_items.py*
(*) = renamed from "refactored" version
```

### Moved to `api/` (2 files)
```
rest_server.py (was: api_server.py)
mcp_server.py
```

### Moved to `shared/` (3 files)
```
config.py, error_handler.py, cache_manager.py
```

## Import Changes

### Pattern
```python
# OLD
from mud_analyzer.config import config
from mud_analyzer.error_handler import ...
from mud_analyzer.cache_manager import ...

# NEW
from mud_analyzer.shared.config import config
from mud_analyzer.shared.error_handler import ...
from mud_analyzer.shared.cache_manager import ...

# Legacy
from mud_analyzer.legacy.menu import MudAnalyzerMenu
from mud_analyzer.legacy.zone_explorer import ZoneExplorer
```

## Running the Project

### Modern API (Recommended)
```bash
python api/rest_server.py          # REST API
python api/mcp_server.py            # MCP Server
```

### Legacy CLI
```bash
python legacy/main.py               # Interactive menu
python legacy/main.py menu          # Direct menu launch
python legacy/main.py search        # Global search
python legacy/main.py browse        # Zone browser
```

## New Documentation Files

- `PROJECT_STRUCTURE.md` - Detailed architecture
- `ARCHITECTURE.md` - Visual diagrams and design
- `REFACTORING_SUMMARY.md` - Complete change list

## Files NOT Moved (Still in Root)

These remain at project root:
- `data_service.py` - Unified data access
- `status_checker.py` - Diagnostics
- `mud_lut.py`, `mud_lut_new.py` - Lookup tables
- `performance.py` - Profiling

## Key Benefits

| Before | After |
|--------|-------|
| 30+ Python files in root | Organized into categories |
| Mixed concerns | Clear separation |
| Hard to navigate | Logical hierarchy |
| CLI-centric | API-first ready |

## Verification

✅ All imports tested and working
✅ File structure validated
✅ No code changes (structure only)
✅ Backward compatible

## Questions?

See documentation files:
- For detailed structure: `PROJECT_STRUCTURE.md`
- For visual architecture: `ARCHITECTURE.md`
- For all changes: `REFACTORING_SUMMARY.md`

---

**Status**: ✅ Complete
**Date**: January 10, 2026
**Impact**: Structure improvement only, no functionality changes
