#!/usr/bin/env python3
"""
Configuration module for MUD Analyzer
Centralizes path management and settings
"""

from pathlib import Path
import os


class Config:
    """Configuration settings for MUD Analyzer"""
    
    def __init__(self):
        # Determine project root (where zone directories are located)
        self.project_root = self._find_project_root()
        
        # Cache directory for performance optimization
        self.cache_dir = Path(__file__).parent / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache validity period (1 week)
        self.cache_validity_seconds = 7 * 24 * 3600
        
        # Pagination settings
        self.default_page_size = 10
        self.zone_browser_page_size = 15
        
        # Search settings
        self.max_search_results = 100
        self.max_associations_per_type = 5
    
    def _find_project_root(self):
        """Find the project root directory containing zone data"""
        # Start from the mud_analyzer directory
        current = Path(__file__).parent
        
        # Go up one level to find zone directories
        parent = current.parent
        
        # Check if parent contains numbered zone directories
        if self._has_zone_directories(parent):
            return parent
        
        # Fallback to current working directory
        cwd = Path.cwd()
        if self._has_zone_directories(cwd):
            return cwd
        
        # Default to parent directory
        return parent
    
    def _has_zone_directories(self, path):
        """Check if a directory contains zone directories (numbered folders)"""
        try:
            zone_dirs = [d for d in path.iterdir() 
                        if d.is_dir() and d.name.isdigit()]
            return len(zone_dirs) > 0
        except (OSError, PermissionError):
            return False
    
    def setup_working_directory(self):
        """Set the working directory to project root"""
        os.chdir(self.project_root)
    
    def get_zone_path(self, zone_num):
        """Get path to a specific zone directory"""
        return self.project_root / str(zone_num)
    
    def get_cache_file(self, cache_name):
        """Get path to a cache file"""
        return self.cache_dir / f"{cache_name}.pkl"


# Global configuration instance
config = Config()