"""
Data models for MUD Analyzer API
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class EntityType(str, Enum):
    OBJECT = "object"
    MOBILE = "mobile"
    ROOM = "room"
    SCRIPT = "script"


class AccessibilityStatus(str, Enum):
    ACCESSIBLE = "accessible"
    INACCESSIBLE = "inaccessible"
    UNKNOWN = "unknown"


class LoadLocationType(str, Enum):
    ROOM = "room"
    MOBILE_EQUIPMENT = "mobile_equipment"
    MOBILE_INVENTORY = "mobile_inventory"
    CONTAINER = "container"
    SCRIPT = "script"


class BaseEntity(BaseModel):
    """Base entity model"""
    vnum: int
    zone: int
    name: str
    entity_type: EntityType
    accessible: AccessibilityStatus = AccessibilityStatus.UNKNOWN


class ObjectEntity(BaseEntity):
    """Object entity model"""
    entity_type: EntityType = EntityType.OBJECT
    type_flag: int
    short_desc: str
    description: Optional[str] = None
    weight: int = 0
    cost: int = 0
    item_flags: List[str] = Field(default_factory=list)
    wear_flags: List[str] = Field(default_factory=list)
    applies: List[Dict[str, Any]] = Field(default_factory=list)


class MobileEntity(BaseEntity):
    """Mobile entity model"""
    entity_type: EntityType = EntityType.MOBILE
    level: int
    alignment: int
    race: Optional[str] = None
    short_desc: str
    long_desc: Optional[str] = None
    spec_proc: Optional[str] = None


class LoadLocation(BaseModel):
    """Load location information"""
    type: LoadLocationType
    zone: int
    location: str
    probability: float
    context: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    """Search request model"""
    query: str
    entity_type: EntityType
    accessible_only: bool = False
    limit: int = 50
    zone_filter: Optional[List[int]] = None


class AssemblyItem(BaseModel):
    """Assembly item model"""
    result_vnum: int
    result_name: str
    zone: int
    parts: List[int]
    success_rate: float
    accessible: bool
    creation_method: str = "assembly"
    requirements: Optional[str] = None


class AssemblyRequest(BaseModel):
    """Assembly analysis request"""
    accessible_only: bool = True
    min_success_rate: float = 0.0
    zone_filter: Optional[List[int]] = None


class ZoneInfo(BaseModel):
    """Zone information"""
    number: int
    name: str
    author: str
    level_range: Optional[str] = None
    description: Optional[str] = None


class ZoneSummary(BaseModel):
    """Zone summary statistics"""
    zone: ZoneInfo
    entity_counts: Dict[str, int]
    accessible_counts: Dict[str, int]
    total_entities: int
    accessibility_rate: float


class SearchResult(BaseModel):
    """Search result model"""
    entity: Union[ObjectEntity, MobileEntity]
    load_locations: List[LoadLocation] = Field(default_factory=list)
    relevance_score: float = 1.0