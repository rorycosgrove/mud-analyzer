# MUD Analyzer - Technology Stack

## Programming Language
- **Python 3**: Core language for all components
- **Version**: Python 3.6+ (uses pathlib, f-strings, type hints)
- **Standard Library**: Extensive use of built-in modules

## Core Dependencies

### Standard Library Modules
- **pathlib**: Modern path handling and file operations
- **pickle**: Cache serialization and persistence
- **json**: Data format handling for spell definitions
- **os/sys**: System integration and environment management
- **re**: Regular expression pattern matching
- **collections**: Data structure utilities (defaultdict, Counter)
- **time**: Performance monitoring and cache validity
- **argparse**: Command-line argument parsing (implied usage)

### File System Integration
- **Cross-platform**: Uses pathlib for OS-agnostic file operations
- **Directory Detection**: Automatic project root discovery
- **Cache Management**: Persistent cache storage with pickle

## Architecture Technologies

### Data Processing
- **Text Parsing**: Custom parsers for MUD data formats
- **Entity Extraction**: Pattern-based data extraction from zone files
- **Indexing**: In-memory indexing for fast lookups
- **Caching**: Multi-level caching with memory and disk persistence

### User Interface
- **Console Interface**: Text-based interactive menus
- **Pagination**: Built-in pagination for large datasets
- **Progress Indicators**: Visual feedback for long operations
- **Error Handling**: Comprehensive error management with user-friendly messages

### Performance Optimization
- **Lazy Loading**: Data loaded only when needed
- **Intelligent Caching**: Automatic cache invalidation and refresh
- **Memory Management**: Efficient data structure usage
- **Batch Processing**: Optimized bulk operations

## Development Commands

### Basic Usage
```bash
# Interactive menu (default)
python mud_analyzer/main.py

# Direct feature access
python mud_analyzer/main.py search      # Global search
python mud_analyzer/main.py browse      # Zone browser
python mud_analyzer/main.py explore 100 # Zone explorer
python mud_analyzer/main.py summary 100 # Zone summary
python mud_analyzer/main.py assembled   # Assembled items
python mud_analyzer/main.py help        # Help system
```

### Cache Management
```bash
# Clear all caches
python mud_analyzer/main.py clear-cache
```

### Testing
```bash
# Run specific tests
python mud_analyzer/test_cache_persistence.py
python mud_analyzer/test_fixes.py
python mud_analyzer/test_spells.py
python mud_analyzer/test_vnum_detection.py
```

## Configuration Management

### Automatic Setup
- **Project Root Detection**: Automatically finds zone directories
- **Cache Directory**: Auto-creates cache directory structure
- **Working Directory**: Sets appropriate working directory

### Configurable Parameters
```python
# Cache settings
cache_validity_seconds = 3600  # 1 hour cache validity

# Pagination settings
default_page_size = 10
zone_browser_page_size = 15

# Search limits
max_search_results = 100
max_associations_per_type = 5
```

## Build System
- **No Build Required**: Pure Python implementation
- **Package Structure**: Standard Python package with __init__.py files
- **Entry Point**: main.py serves as application entry point
- **Module Imports**: Relative imports within package structure

## Data Formats

### Input Data
- **Zone Files**: Custom MUD data format (text-based)
- **Spell Data**: JSON format for spell definitions
- **Configuration**: Python-based configuration

### Cache Data
- **Pickle Format**: Binary serialization for performance
- **Index Files**: Optimized lookup structures
- **Entity Caches**: Preprocessed entity data

## Development Environment
- **IDE Support**: Standard Python development environment
- **Debugging**: Built-in error handling and logging
- **Testing**: Custom test scripts for validation
- **Documentation**: Inline documentation and help system

## Deployment
- **Standalone**: No external dependencies beyond Python standard library
- **Portable**: Self-contained package structure
- **Installation**: Simple file copy to target directory
- **Requirements**: Python 3.6+ on target system