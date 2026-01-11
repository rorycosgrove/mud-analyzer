#!/usr/bin/env python3
"""
MUD Analyzer REST API Server
FastAPI-based REST API for MUD world data analysis
"""

import sys
from pathlib import Path

# Add parent directory to path so imports work from any location
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio

from mud_analyzer_api.config import Config
from mud_analyzer_api.core.world_service import WorldService
from mud_analyzer_api.core.search_service import SearchService
from mud_analyzer_api.core.assembly_service import AssemblyService
from mud_analyzer_api.models.entities import (
    SearchRequest, SearchResult, AssemblyRequest, AssemblyItem,
    ObjectEntity, MobileEntity, ZoneInfo, ZoneSummary, LoadLocation,
    EntityType
)

# Initialize services
config = Config()
config.setup_directories()

world_service = WorldService(config)
search_service = SearchService(world_service)
assembly_service = AssemblyService(world_service)

# Create FastAPI app
app = FastAPI(
    title="MUD Analyzer API",
    description="REST API for AddictMUD world data analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "MUD Analyzer API",
        "version": "1.0.0",
        "description": "REST API for AddictMUD world data analysis"
    }


@app.get("/zones", response_model=List[ZoneInfo])
async def get_zones():
    """Get list of all available zones"""
    try:
        return await world_service.get_zones()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/zones/{zone_number}", response_model=ZoneSummary)
async def get_zone_summary(zone_number: int):
    """Get summary for a specific zone"""
    try:
        return await world_service.get_zone_summary(zone_number)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/objects/{vnum}", response_model=ObjectEntity)
async def get_object(vnum: int):
    """Get detailed information about a specific object"""
    try:
        return await world_service.get_object_details(vnum)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mobiles/{vnum}", response_model=MobileEntity)
async def get_mobile(vnum: int):
    """Get detailed information about a specific mobile"""
    try:
        return await world_service.get_mobile_details(vnum)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/load-locations/{vnum}", response_model=List[LoadLocation])
async def get_load_locations(vnum: int):
    """Get load locations for an entity"""
    try:
        return await world_service.get_load_locations(vnum)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/objects", response_model=List[SearchResult])
async def search_objects(
    query: str = Query(..., description="Search query"),
    accessible_only: bool = Query(False, description="Only show accessible objects"),
    limit: int = Query(50, description="Maximum number of results"),
    zones: Optional[List[int]] = Query(None, description="Filter by zone numbers")
):
    """Search for objects"""
    try:
        request = SearchRequest(
            query=query,
            entity_type=EntityType.OBJECT,
            accessible_only=accessible_only,
            limit=limit,
            zone_filter=zones
        )
        return await search_service.search_entities(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/mobiles", response_model=List[SearchResult])
async def search_mobiles(
    query: str = Query(..., description="Search query"),
    accessible_only: bool = Query(False, description="Only show accessible mobiles"),
    limit: int = Query(50, description="Maximum number of results"),
    zones: Optional[List[int]] = Query(None, description="Filter by zone numbers")
):
    """Search for mobiles"""
    try:
        request = SearchRequest(
            query=query,
            entity_type=EntityType.MOBILE,
            accessible_only=accessible_only,
            limit=limit,
            zone_filter=zones
        )
        return await search_service.search_entities(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/assemblies", response_model=List[AssemblyItem])
async def get_assemblies(
    accessible_only: bool = Query(True, description="Only show accessible assemblies"),
    min_success_rate: float = Query(0.0, description="Minimum success rate"),
    zones: Optional[List[int]] = Query(None, description="Filter by zone numbers")
):
    """Get assembled and script-created items"""
    try:
        request = AssemblyRequest(
            accessible_only=accessible_only,
            min_success_rate=min_success_rate,
            zone_filter=zones
        )
        return await assembly_service.analyze_assemblies(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=List[SearchResult])
async def search_entities(request: SearchRequest):
    """Search for entities with full request body"""
    try:
        return await search_service.search_entities(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assemblies/analyze", response_model=List[AssemblyItem])
async def analyze_assemblies(request: AssemblyRequest):
    """Analyze assemblies with full request body"""
    try:
        return await assembly_service.analyze_assemblies(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🏰 MUD ANALYZER REST API SERVER")
    print("="*60)
    print(f"\n📍 Starting server on http://127.0.0.1:8000")
    print(f"📚 OpenAPI Docs: http://127.0.0.1:8000/docs")
    print(f"📖 ReDoc: http://127.0.0.1:8000/redoc\n")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
    uvicorn.run(
        "api_server:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug
    )