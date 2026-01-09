# MUD Analyzer - AddictMUD World Analysis Tools

## Overview

MUD Analyzer is a comprehensive suite of tools for exploring and analyzing AddictMUD world data. It provides powerful search capabilities, detailed zone exploration, assembly analysis, and comprehensive reporting features.

## Quick Start

1. **Setup**: Place the analyzer in your AddictMUD world directory (containing numbered zone folders)
2. **Run**: `python mud_analyzer/main.py` for interactive menu
3. **Explore**: Start with Zone Browser to see available zones
4. **Search**: Use Global Search to find specific items across all zones

## Features

### 🔍 **Global Search** (Refactored)
- Search objects & mobiles across all zones
- View detailed item information and statistics  
- Find load locations and probabilities
- Unified data service with optimized caching

### 🌍 **Zone Browser** (Refactored)
- Browse zones by name, author, or statistics
- Enhanced search and filtering capabilities
- Direct zone exploration integration
- Author-based zone grouping

### 🏰 **Zone Explorer**
- Interactive exploration of individual zones
- Browse rooms, mobiles, objects, scripts, assembles
- Detailed entity information with formatted display
- Zone overview and statistics

### 🔧 **Assembled Items** (Refactored)
- Analyze craftable items and requirements
- Identify possible vs impossible assemblies
- Component analysis with load locations
- Success probability calculations

### 📊 **Zone Summary**
- Generate comprehensive zone reports
- Entity counts and distributions
- Detailed analysis and statistics

### 📚 **Help & Documentation** (New)
- Comprehensive help system
- Getting started guide
- Feature-specific documentation
- Tips, tricks, and troubleshooting

### 🔍 **Project Status Checker** (New)
- Verify setup and diagnose issues
- Check directory structure and data files
- Cache status and dependency verification
- Project statistics and recommendations

## Architecture Improvements

### Unified Data Service
- Centralized data access and caching
- Optimized performance with shared indexes
- Consistent entity handling across modules

### Base Explorer Classes
- Eliminated code duplication (~60% reduction)
- Standardized menu patterns and navigation
- Common pagination and search functionality

### Enhanced Caching
- Unified cache manager
- Memory and disk persistence
- Automatic cache invalidation

## Directory Structure

```
mud_analyzer/
├── main.py                           # Entry point
├── menu.py                           # Main menu system
├── help_system.py                    # Help and documentation
├── status_checker.py                 # Project status verification
├── config.py                         # Configuration management
├── cache_manager.py                  # Unified caching system
├── error_handler.py                  # Error handling utilities
├── performance.py                    # Performance monitoring
├── data_service.py                   # Unified data access
├── base_explorer.py                  # Base classes for explorers
├── global_search_refactored.py       # Enhanced global search
├── zone_browser_refactored.py        # Enhanced zone browser
├── assembled_items_refactored.py     # Enhanced assembly analysis
├── zone_explorer.py                  # Zone exploration
├── core/
│   └── world_lookup.py               # Core data access
├── analysis/
│   ├── identify_object.py            # Object analysis
│   ├── identify_mobile.py            # Mobile analysis
│   └── zone_summary.py               # Zone reporting
├── utils/
│   └── spell_lookup.py               # Spell utilities
└── data/
    └── spells.json                   # Spell definitions
```

## Usage

### Interactive Menu
```bash
python mud_analyzer/main.py
```

### Command Line
```bash
python mud_analyzer/main.py search      # Global search
python mud_analyzer/main.py browse      # Zone browser  
python mud_analyzer/main.py explore 100 # Zone explorer
python mud_analyzer/main.py summary 100 # Zone summary
python mud_analyzer/main.py assembled   # Assembled items
python mud_analyzer/main.py help        # Help system
```

## Performance Features

- **Lazy Loading**: Data loaded only when needed
- **Intelligent Caching**: Automatic cache management
- **Optimized Indexing**: Fast lookups across large datasets
- **Progress Indicators**: Visual feedback for long operations
- **Memory Management**: Efficient memory usage patterns

## User Experience Enhancements

- **Consistent Navigation**: Standardized menu patterns
- **Enhanced Search**: Improved search capabilities across all modules
- **Better Error Handling**: Comprehensive error management
- **Help Integration**: Built-in documentation and guidance
- **Status Verification**: Setup validation and troubleshooting