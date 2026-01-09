# MUD Analyzer - Project Structure

## Directory Organization

### Root Level Components
```
mud_analyzer/
├── main.py                           # Application entry point
├── menu.py                           # Main menu system
├── config.py                         # Configuration management
├── data_service.py                   # Unified data access layer
├── cache_manager.py                  # Caching system
├── base_explorer.py                  # Base classes for explorers
├── error_handler.py                  # Error handling utilities
├── performance.py                    # Performance monitoring
├── help_system.py                    # Help and documentation
└── status_checker.py                 # Project diagnostics
```

### Feature Modules
```
├── global_search_refactored.py       # Enhanced global search
├── zone_browser_refactored.py        # Enhanced zone browser
├── assembled_items_refactored.py     # Enhanced assembly analysis
├── zone_explorer.py                  # Zone exploration
├── global_search.py                  # Legacy global search
├── zone_browser.py                   # Legacy zone browser
└── assembled_items.py                # Legacy assembly analysis
```

### Core Components
```
core/
└── world_lookup.py                   # Core data access and parsing
```

### Analysis Modules
```
analysis/
├── identify_object.py                # Object analysis and identification
├── identify_mobile.py                # Mobile analysis and identification
└── zone_summary.py                   # Zone reporting and statistics
```

### Utilities
```
utils/
└── spell_lookup.py                   # Spell definitions and utilities

data/
└── spells.json                       # Spell data definitions
```

### Cache System
```
cache/
├── command_index.pkl                 # Command indexing cache
├── entities_mobile.pkl               # Mobile entity cache
└── entities_object.pkl               # Object entity cache
```

## Architectural Patterns

### Unified Data Service Architecture
- **Centralized Access**: Single point for all data operations
- **Shared Caching**: Optimized performance with unified cache management
- **Consistent Interfaces**: Standardized entity handling across modules

### Base Explorer Pattern
- **Code Reuse**: Common functionality in base_explorer.py
- **Standardized Navigation**: Consistent menu patterns and pagination
- **Inheritance Hierarchy**: Specialized explorers extend base functionality

### Refactored Module Structure
- **Legacy Preservation**: Original modules maintained for compatibility
- **Enhanced Versions**: Refactored modules with improved functionality
- **Migration Path**: Clear upgrade path from legacy to enhanced versions

## Core Components Relationships

### Data Flow
1. **world_lookup.py**: Core data parsing and entity extraction
2. **data_service.py**: Unified data access with caching integration
3. **cache_manager.py**: Intelligent caching with persistence
4. **Feature Modules**: Specialized analysis using unified data service

### Menu System
1. **main.py**: Entry point with command-line argument handling
2. **menu.py**: Interactive menu system with feature routing
3. **help_system.py**: Integrated documentation and guidance
4. **status_checker.py**: Setup verification and diagnostics

### Analysis Pipeline
1. **Core Data Access**: world_lookup.py provides raw data parsing
2. **Entity Identification**: analysis/ modules provide detailed entity analysis
3. **Feature Processing**: Specialized modules perform specific analysis tasks
4. **Caching Layer**: Transparent performance optimization

## Module Dependencies

### Core Dependencies
- **world_lookup.py**: Foundation for all data access
- **data_service.py**: Required by all feature modules
- **cache_manager.py**: Used by data_service for performance
- **base_explorer.py**: Extended by interactive modules

### Feature Module Dependencies
- All refactored modules depend on data_service.py
- Interactive modules extend base_explorer.py
- Analysis modules use core/world_lookup.py directly
- Utility modules are standalone with minimal dependencies

## Configuration Management
- **config.py**: Centralized configuration with environment detection
- **Cache Configuration**: Automatic cache directory management
- **Performance Tuning**: Configurable performance parameters
- **Error Handling**: Centralized error management configuration