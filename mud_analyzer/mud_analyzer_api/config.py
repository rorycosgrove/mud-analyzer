"""
Configuration for MUD Analyzer API
"""

from pathlib import Path
from typing import Optional
from pydantic import BaseSettings


class Config(BaseSettings):
    """Application configuration"""
    
    # World data paths
    world_root: Path = Path.cwd()
    cache_dir: Path = Path.cwd() / "cache"
    
    # API settings
    api_host: str = "localhost"
    api_port: int = 8000
    debug: bool = False
    
    # Performance settings
    cache_ttl: int = 3600  # 1 hour
    max_search_results: int = 1000
    
    class Config:
        env_prefix = "MUD_ANALYZER_"
        case_sensitive = False
    
    def setup_directories(self):
        """Ensure required directories exist"""
        self.cache_dir.mkdir(exist_ok=True)
        
    @property
    def zones_path(self) -> Path:
        """Path to zones directory"""
        return self.world_root
    
    def get_zone_path(self, zone_number: int) -> Path:
        """Get path to specific zone"""
        return self.world_root / str(zone_number)