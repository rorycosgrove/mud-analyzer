#!/usr/bin/env python3
"""
REST API Client Examples
Demonstrates how to use the REST API client
"""

from rest_client import MUDAnalyzerClient, MUDAnalyzerClientError


def example_basic_usage():
    """Basic usage example"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60)
    
    with MUDAnalyzerClient("http://localhost:8000") as client:
        # Check if API is healthy
        if not client.health():
            print("❌ API is not responding")
            return
        
        print("✅ API is healthy\n")
        
        # Get all zones
        print("📍 Getting zones...")
        zones = client.get_zones(limit=5)
        for zone in zones:
            print(f"  Zone {zone.zone_num}: {zone.name} by {zone.author}")


def example_search():
    """Search example"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Search")
    print("="*60)
    
    with MUDAnalyzerClient("http://localhost:8000") as client:
        # Search for objects
        print("🔍 Searching for 'sword'...")
        results = client.search_objects("sword", limit=10)
        
        if results:
            for result in results:
                print(f"  VNUM {result.vnum}: {result.name} (Zone {result.zone})")
        else:
            print("  No results found")
        
        # Search for mobiles
        print("\n🔍 Searching for 'dragon'...")
        results = client.search_mobiles("dragon", limit=10)
        
        if results:
            for result in results:
                print(f"  VNUM {result.vnum}: {result.name} (Zone {result.zone})")
        else:
            print("  No results found")


def example_zone_details():
    """Zone details example"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Zone Details")
    print("="*60)
    
    with MUDAnalyzerClient("http://localhost:8000") as client:
        try:
            # Get first zone
            zones = client.get_zones(limit=1)
            if zones:
                zone = zones[0]
                print(f"📍 Getting details for Zone {zone.zone_num}...")
                
                details = client.get_zone(zone.zone_num)
                print(f"\n  Zone: {details.get('name', 'N/A')}")
                print(f"  Author: {details.get('author', 'N/A')}")
                print(f"  Objects: {details.get('object_count', 0)}")
                print(f"  Mobiles: {details.get('mobile_count', 0)}")
        except Exception as e:
            print(f"Error: {e}")


def example_entity_details():
    """Entity details example"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Entity Details")
    print("="*60)
    
    with MUDAnalyzerClient("http://localhost:8000") as client:
        # Search for an object first
        print("🔍 Searching for 'potion'...")
        results = client.search_objects("potion", limit=1)
        
        if results:
            obj = results[0]
            print(f"\n📦 Getting details for object VNUM {obj.vnum}...")
            
            details = client.get_object(obj.vnum)
            print(f"  Name: {details.get('name', 'N/A')}")
            print(f"  Short: {details.get('short_description', 'N/A')}")
            print(f"  Zone: {details.get('zone', 'N/A')}")
            print(f"  Weight: {details.get('weight', 'N/A')}")
            
            # Try to find assemblies
            print(f"\n🔗 Finding assemblies with VNUM {obj.vnum}...")
            assemblies = client.find_assemblies(obj.vnum, limit=5)
            assembly_list = assemblies.get("assemblies", [])
            
            if assembly_list:
                for assembly in assembly_list:
                    print(f"  {assembly.get('name', 'Unknown')}")
            else:
                print("  No assemblies found")
        else:
            print("No objects found")


def example_batch_search():
    """Batch search example"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Batch Search")
    print("="*60)
    
    with MUDAnalyzerClient("http://localhost:8000") as client:
        queries = ["sword", "shield", "armor", "spell"]
        
        for query in queries:
            print(f"\n🔍 Searching for '{query}'...")
            results = client.search_objects(query, limit=3)
            
            if results:
                count = len(results)
                print(f"  Found {count} result(s):")
                for result in results[:3]:
                    print(f"    - {result.name} (VNUM {result.vnum})")
            else:
                print(f"  No results found")


def example_pagination():
    """Pagination example"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Pagination")
    print("="*60)
    
    with MUDAnalyzerClient("http://localhost:8000") as client:
        print("📍 Getting zones with pagination...\n")
        
        # Get first page
        page_size = 5
        for page in range(0, 3):
            skip = page * page_size
            print(f"Page {page + 1}:")
            zones = client.get_zones(skip=skip, limit=page_size)
            
            if not zones:
                print("  No more zones")
                break
            
            for zone in zones:
                print(f"  - Zone {zone.zone_num}: {zone.name}")
            print()


def example_api_docs():
    """API documentation example"""
    print("\n" + "="*60)
    print("EXAMPLE 7: API Documentation")
    print("="*60)
    
    with MUDAnalyzerClient("http://localhost:8000") as client:
        docs_url = client.get_docs_url()
        print(f"\n📚 OpenAPI Documentation available at:")
        print(f"   {docs_url}")
        print(f"\nOpen this URL in your browser to explore the API interactively.")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("🏰 MUD ANALYZER - REST API CLIENT EXAMPLES")
    print("="*60)
    print("\nMake sure the API server is running:")
    print("  python ../mud_analyzer/launch_servers.py --rest")
    
    try:
        example_basic_usage()
        example_search()
        example_zone_details()
        example_entity_details()
        example_batch_search()
        example_pagination()
        example_api_docs()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60 + "\n")
        
    except MUDAnalyzerClientError as e:
        print(f"\n❌ Client Error: {e}")
        print("\nMake sure the REST API server is running:")
        print("  cd ../mud_analyzer")
        print("  python launch_servers.py --rest")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
