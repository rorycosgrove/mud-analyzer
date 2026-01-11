# MUD Analyzer - Refactored Architecture

## Visual Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    MUD ANALYZER PROJECT                         │
└─────────────────────────────────────────────────────────────────┘

ENTRY POINTS
═════════════════════════════════════════════════════════════════

  Modern API (Recommended)        Legacy CLI (Preserved)
  ┌──────────────────────┐        ┌───────────────────┐
  │ api/rest_server.py   │        │ legacy/main.py    │
  │ (FastAPI)            │        │ (Command Router)  │
  │                      │        │                   │
  │ api/mcp_server.py    │        │ legacy/menu.py    │
  │ (LLM Integration)    │        │ (Interactive CLI) │
  └──────────┬───────────┘        └────────┬──────────┘
             │                             │
             │                             │
BUSINESS LOGIC LAYER
═════════════════════════════════════════════════════════════════
    
    ┌────────────────────────────────────────────────────────┐
    │           mud_analyzer_api/                            │
    │  ┌─────────────┐  ┌──────────┐  ┌────────────────┐   │
    │  │ world_service│  │search    │  │assembly        │   │
    │  │             │  │_service  │  │_service        │   │
    │  └─────────────┘  └──────────┘  └────────────────┘   │
    └────────────────────────────────────────────────────────┘
                          ▲
                          │
LEGACY EXPLORERS (CLI)    │    CORE LOGIC
═════════════════════════════════════════════════════════════════

┌──────────────────┐      │      ┌────────────────────┐
│ legacy/          │      │      │ core/              │
│  ├─ main.py      │      │      │  └─ world_lookup.py│
│  ├─ menu.py      │      │      └────────────────────┘
│  ├─ zone_        │      │              ▲
│  │  explorer.py  │      │              │
│  ├─ zone_        │      │      ┌───────┴────────────┐
│  │  browser.py   │      │      │                    │
│  ├─ global_      │      │      │
│  │  search.py    │      │   analysis/ &      utils/
│  ├─ assembled_   │      │   ┌──────────────────┐
│  │  items.py     │      │   │ identify_        │
│  └─ ...          │      │   │  mobile.py       │
└──────────────────┘      │   │ identify_        │
                          │   │  object.py       │
                          │   │ zone_summary.py  │
                          │   │                  │
                          └───│ spell_lookup.py  │
                              └──────────────────┘

SHARED INFRASTRUCTURE
═════════════════════════════════════════════════════════════════

    ┌────────────────────────────────────────────┐
    │          shared/                           │
    │  ┌────────────┐  ┌──────────────┐         │
    │  │ config.py  │  │error_handler │         │
    │  │ (Paths &   │  │(Validation & │         │
    │  │ Settings)  │  │ Error Mgmt)  │         │
    │  └────────────┘  └──────────────┘         │
    │         ▲                   ▲              │
    │         │                   │              │
    │         └────────┬──────────┘              │
    │                  │                         │
    │         ┌────────▼──────┐                 │
    │         │ cache_manager │                 │
    │         │ (Performance) │                 │
    │         └───────────────┘                 │
    └────────────────────────────────────────────┘

DATA & UTILITIES
═════════════════════════════════════════════════════════════════

    ┌────────────────────────────────────┐
    │ data_service.py                    │
    │ (Unified Data Access with Cache)   │
    └─────────────────────┬──────────────┘
                          │
                ┌─────────┼────────────┐
                │         │            │
           ┌────▼──┐  ┌───▼───┐  ┌────▼────┐
           │mud_lut│  │status  │  │performance
           │.py    │  │_checker│  │.py
           └───────┘  └────────┘  └─────────┘
                │
           ┌────▼──────┐
           │ data/      │
           │ └─ spells  │
           │    .json   │
           └────────────┘


IMPORT FLOW
═════════════════════════════════════════════════════════════════

   api/rest_server.py
   api/mcp_server.py
           │
           ▼
   mud_analyzer_api/
   ├─ core/
   │  ├─ world_service ──┐
   │  ├─ search_service  ├──► core/ (world_lookup.py)
   │  └─ assembly_service ──┤
   │                        │
   └─ models/entities       │
           │                │
           ▼                ▼
   shared/config.py ◄───────┘
   shared/error_handler.py
   shared/cache_manager.py
           │
           ▼
   data_service.py
           │
           ▼
   analysis/ & utils/


KEY FEATURES OF THIS STRUCTURE
═════════════════════════════════════════════════════════════════

✓ CLEAR SEPARATION OF CONCERNS
  - API layer isolated from CLI
  - Business logic decoupled from interfaces
  - Utilities grouped and accessible

✓ IMPROVED NAVIGATION
  - Related modules grouped together
  - Clear naming conventions
  - Logical file hierarchy

✓ BACKWARD COMPATIBLE
  - Legacy CLI preserved in legacy/
  - Original functionality unchanged
  - Can phase out gradually

✓ FUTURE-PROOF
  - Modern API ready for LLM integration
  - Easy to add new API endpoints
  - Simple to extend with new analyzers

✓ TEST-FRIENDLY
  - Modules can be tested independently
  - Mocks easily inject shared dependencies
  - Service layer well-defined


USAGE PATTERNS
═════════════════════════════════════════════════════════════════

For new development, prefer:
  from mud_analyzer_api.core.world_service import WorldService
  from mud_analyzer_api.models.entities import SearchRequest

For core utilities, use:
  from mud_analyzer.shared.config import config
  from mud_analyzer.shared.error_handler import validate_vnum
  from mud_analyzer.core.world_lookup import World

For legacy compatibility, still available:
  from mud_analyzer.legacy.zone_explorer import ZoneExplorer
  from mud_analyzer.legacy.menu import MudAnalyzerMenu
