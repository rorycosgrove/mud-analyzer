"""
REST API Client for MUD Analyzer
Provides a Python interface to the REST API endpoints
"""

import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class SearchResult:
    """Search result from API"""
    vnum: int
    zone: int
    name: str
    entity_type: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        return cls(**data)


@dataclass
class ZoneInfo:
    """Zone information from API"""
    zone_num: int
    name: str
    author: str
    object_count: int
    mobile_count: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZoneInfo":
        return cls(**data)


import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class MUDAnalyzerClient:
    """
    REST API Client for MUD Analyzer
    
    Example:
        >>> client = MUDAnalyzerClient("http://localhost:8000")
        >>> zones = client.get_zones()
        >>> results = client.search("sword")
        >>> objects = client.search_objects("dragon")
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: int = 30):
        """
        Initialize the client
        
        Args:
            base_url: Base URL of the API server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
        kwargs.setdefault('timeout', self.timeout)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            raise MUDAnalyzerClientError(f"API request failed: {e}")
    
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET request"""
        return self._request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """POST request"""
        return self._request("POST", endpoint, **kwargs)
    
    def health(self) -> bool:
        """Check if API is healthy"""
        try:
            response = self.get("api/health")
            return response.get("status") == "ok"
        except:
            return False
    
    def get_zones(self, skip: int = 0, limit: int = 100) -> List[ZoneInfo]:
        """
        Get list of all zones
        
        Args:
            skip: Number of zones to skip
            limit: Maximum number of zones to return
        
        Returns:
            List of zone information
        """
        data = self.get("zones", params={"skip": skip, "limit": limit})
        # API returns list directly
        if isinstance(data, list):
            zones = data
        else:
            zones = data.get("zones", [])
        return [ZoneInfo.from_dict(z) for z in zones]
    
    def get_zone(self, zone_num: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific zone
        
        Args:
            zone_num: Zone number
        
        Returns:
            Zone details
        """
        return self.get(f"zones/{zone_num}")
    
    def search(
        self,
        query: str,
        entity_type: Optional[str] = "object",
        skip: int = 0,
        limit: int = 50
    ) -> List[SearchResult]:
        """
        Search for objects and mobiles
        
        Args:
            query: Search query
            entity_type: Filter by type ("object", "mobile", "room", "script")
            skip: Number of results to skip (not used by API)
            limit: Maximum results to return
        
        Returns:
            List of search results
        """
        # Default to "object" if not specified
        if not entity_type:
            entity_type = "object"
        
        data = self.post("search", json={
            "query": query, 
            "entity_type": entity_type,
            "limit": limit
        })
        # API returns list directly
        if isinstance(data, list):
            results = data
        else:
            results = data.get("results", [])
        return [SearchResult.from_dict(r) for r in results]
    
    def search_objects(self, query: str, skip: int = 0, limit: int = 50) -> List[SearchResult]:
        """Search for objects only"""
        return self.search(query, entity_type="object", skip=skip, limit=limit)
    
    def search_mobiles(self, query: str, skip: int = 0, limit: int = 50) -> List[SearchResult]:
        """Search for mobiles only"""
        return self.search(query, entity_type="mobile", skip=skip, limit=limit)
    
    def get_object(self, vnum: int) -> Dict[str, Any]:
        """
        Get detailed information about an object
        
        Args:
            vnum: Object virtual number
        
        Returns:
            Object details
        """
        return self.get(f"objects/{vnum}")
    
    def get_mobile(self, vnum: int) -> Dict[str, Any]:
        """
        Get detailed information about a mobile
        
        Args:
            vnum: Mobile virtual number
        
        Returns:
            Mobile details
        """
        return self.get(f"mobiles/{vnum}")
    
    def find_assemblies(
        self,
        obj_vnum: int,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Find item assemblies containing a specific object
        
        Args:
            obj_vnum: Object virtual number
            skip: Number of results to skip
            limit: Maximum results to return
        
        Returns:
            Assembly information
        """
        return self.post(
            "assemblies",
            json={"object_vnum": obj_vnum, "skip": skip, "limit": limit}
        )
    
    def get_docs_url(self) -> str:
        """Get OpenAPI documentation URL"""
        return f"{self.base_url}/docs"
    
    def close(self) -> None:
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class MUDAnalyzerClientError(Exception):
    """Client error"""
    pass
