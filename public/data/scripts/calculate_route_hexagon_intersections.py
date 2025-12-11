#!/usr/bin/env python3
"""
Calculate which hexagons intersect with each route.

This script calculates which hexagons from lumo_score.geojson intersect with
each route (both fast and bright routes) and saves the intersection data as
JSON files that can be loaded by the frontend for animation.
"""

import json
import os
from pathlib import Path
from shapely.geometry import shape, LineString
from shapely.strtree import STRtree
from collections import defaultdict

# Configuration - paths relative to script location
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent
ROUTES_WGS84_DIR = DATA_DIR / "routes_wgs84"
LUMO_SCORE_FILE = DATA_DIR / "lumo_score.geojson"
OUTPUT_DIR = DATA_DIR / "route_intersections"

def load_geojson(filepath):
    """Load a GeoJSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Save data as JSON file."""
    os.makedirs(filepath.parent, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def create_hexagon_index(hexagons):
    """
    Create an R-tree spatial index for fast line-polygon intersection queries.
    Returns a tuple of (STRtree index, list of geometries, list of hexagon IDs).
    """
    geometries = []
    hex_ids = []
    
    for feature in hexagons['features']:
        if feature['geometry']['type'] == 'Polygon':
            geom = shape(feature['geometry'])
            geometries.append(geom)
            # Use the 'id' property as identifier
            hex_id = feature['properties'].get('id', feature['properties'].get('fid'))
            hex_ids.append(hex_id)
    
    tree = STRtree(geometries)
    return tree, geometries, hex_ids

def find_intersecting_hexagons(route_line, hex_tree, hex_geoms, hex_ids):
    """
    Find all hexagons that intersect with the route line.
    Returns a list of hexagon IDs.
    """
    intersecting_ids = []
    
    # Query the spatial index for potential intersections
    candidates = hex_tree.query(route_line)
    
    for idx in candidates:
        hex_geom = hex_geoms[idx]
        hex_id = hex_ids[idx]
        
        # Check if the route line intersects with this hexagon
        if route_line.intersects(hex_geom):
            intersecting_ids.append(hex_id)
    
    return intersecting_ids

def process_route_file(route_file, hex_tree, hex_geoms, hex_ids, route_type):
    """
    Process a single route file and find intersecting hexagons.
    route_type should be 'fast' or 'bright'.
    """
    route_data = load_geojson(route_file)
    
    intersecting_hex_ids = []
    
    for feature in route_data['features']:
        if feature['geometry']['type'] == 'LineString':
            coords = feature['geometry']['coordinates']
            route_line = LineString(coords)
            
            # Find intersecting hexagons
            hex_ids_for_route = find_intersecting_hexagons(
                route_line, hex_tree, hex_geoms, hex_ids
            )
            intersecting_hex_ids.extend(hex_ids_for_route)
    
    # Remove duplicates while preserving order
    unique_hex_ids = list(dict.fromkeys(intersecting_hex_ids))
    
    return unique_hex_ids

def main():
    """Main function to process all routes."""
    print("Loading hexagon data...")
    hexagons = load_geojson(LUMO_SCORE_FILE)
    print(f"Loaded {len(hexagons['features'])} hexagons")
    
    print("Creating spatial index...")
    hex_tree, hex_geoms, hex_ids = create_hexagon_index(hexagons)
    print("Spatial index created")
    
    # Get all route files
    route_files = sorted(ROUTES_WGS84_DIR.glob("*_f.geojson"))
    print(f"Found {len(route_files)} fast route files")
    
    # Process each route
    for route_file in route_files:
        route_name = route_file.stem  # e.g., "2_3_f"
        base_name = route_name[:-2]  # Remove "_f" suffix
        
        print(f"\nProcessing {route_name}...")
        
        # Process fast route
        fast_route_file = route_file
        fast_hex_ids = process_route_file(
            fast_route_file, hex_tree, hex_geoms, hex_ids, 'fast'
        )
        print(f"  Fast route: {len(fast_hex_ids)} intersecting hexagons")
        
        # Process bright route
        bright_route_file = ROUTES_WGS84_DIR / f"{base_name}_b.geojson"
        bright_hex_ids = []
        if bright_route_file.exists():
            bright_hex_ids = process_route_file(
                bright_route_file, hex_tree, hex_geoms, hex_ids, 'bright'
            )
            print(f"  Bright route: {len(bright_hex_ids)} intersecting hexagons")
        else:
            print(f"  Bright route: file not found")
        
        # Save intersection data
        output_data = {
            'route_name': base_name,
            'fast_hex_ids': fast_hex_ids,
            'bright_hex_ids': bright_hex_ids,
            'fast_count': len(fast_hex_ids),
            'bright_count': len(bright_hex_ids),
        }
        
        output_file = OUTPUT_DIR / f"{base_name}.json"
        save_json(output_data, output_file)
        print(f"  Saved to {output_file.name}")
    
    print(f"\n✓ Processing complete! Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
