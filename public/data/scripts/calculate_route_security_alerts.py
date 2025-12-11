#!/usr/bin/env python3
"""
Calculate route security alerts - identify route segments that intersect
with hexagons below the median combined_score (unsafe areas).

This script:
1. Loads the hexagon median value
2. For each route pair, identifies hexagons below the median
3. Finds route segments (line segments) that intersect with these unsafe hexagons
4. Outputs JSON files with route segment indices that should be colored red
"""

import json
from pathlib import Path
from shapely.geometry import LineString, Polygon, Point
from shapely.strtree import STRtree
import statistics

# Configuration - paths relative to script location
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent
LUMO_SCORE_FILE = DATA_DIR / "lumo_score.geojson"
MEDIAN_FILE = DATA_DIR / "hexagon_median.json"
ROUTES_DIR = DATA_DIR / "routes_wgs84"
OUTPUT_DIR = DATA_DIR / "route_security_alerts"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_geojson(filepath):
    """Load a GeoJSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Save data as JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_median():
    """Load the hexagon median value."""
    if not MEDIAN_FILE.exists():
        print(f"Error: Median file not found at {MEDIAN_FILE}")
        print("Please run calculate_hexagon_median.py first")
        return None
    
    with open(MEDIAN_FILE, 'r', encoding='utf-8') as f:
        median_data = json.load(f)
        return median_data.get('median_score')

def get_hexagon_id(properties):
    """Get hexagon ID from properties (try 'id' first, then 'fid')."""
    return properties.get('id') or properties.get('fid')

def main():
    """Main function to calculate route security alerts."""
    print("Loading hexagon data and median...")
    
    # Load median
    median_score = load_median()
    if median_score is None:
        return
    print(f"Using median score: {median_score}")
    
    # Load hexagon data
    hexagons = load_geojson(LUMO_SCORE_FILE)
    print(f"Loaded {len(hexagons['features'])} hexagons")
    
    # Build spatial index for unsafe hexagons (below median)
    unsafe_hexagons = []
    unsafe_hexagon_geoms = []
    unsafe_hexagon_ids = set()
    
    for feature in hexagons['features']:
        score = feature['properties'].get('combined_score', 0)
        if score > 0 and score < median_score:
            hex_id = get_hexagon_id(feature['properties'])
            if hex_id is not None:
                geom = Polygon(feature['geometry']['coordinates'][0])
                unsafe_hexagons.append({
                    'id': hex_id,
                    'geometry': geom,
                    'score': score
                })
                unsafe_hexagon_geoms.append(geom)
                unsafe_hexagon_ids.add(hex_id)
    
    print(f"Found {len(unsafe_hexagons)} unsafe hexagons (below median)")
    
    if len(unsafe_hexagons) == 0:
        print("No unsafe hexagons found, nothing to process")
        return
    
    # Build spatial index for fast lookup
    unsafe_tree = STRtree(unsafe_hexagon_geoms)
    
    # Process all route files
    route_files = list(ROUTES_DIR.glob("*.geojson"))
    print(f"\nProcessing {len(route_files)} route files...")
    
    processed_count = 0
    
    # Group route files by route pair (e.g., 1_7_f and 1_7_b -> 1_7)
    route_pairs = {}
    for route_file in route_files:
        name = route_file.stem  # e.g., "1_7_f" or "1_7_b"
        # Extract route pair name (remove _f or _b suffix)
        if name.endswith('_f'):
            route_pair = name[:-2]
            route_type = 'fast'
        elif name.endswith('_b'):
            route_pair = name[:-2]
            route_type = 'bright'
        else:
            continue  # Skip files that don't match the pattern
        
        if route_pair not in route_pairs:
            route_pairs[route_pair] = {}
        route_pairs[route_pair][route_type] = route_file
    
    print(f"Found {len(route_pairs)} route pairs")
    
    for route_pair, files in route_pairs.items():
        print(f"\nProcessing route pair: {route_pair}")
        
        alerts = {
            'fast': {'unsafe_segments': [], 'unsafe_hex_count': 0},
            'bright': {'unsafe_segments': [], 'unsafe_hex_count': 0}
        }
        
        for route_type, route_file in files.items():
            try:
                route_data = load_geojson(route_file)
                
                if not route_data.get('features') or len(route_data['features']) == 0:
                    print(f"  No {route_type} route found in {route_file.name}")
                    continue
                
                route_feature = route_data['features'][0]
                route_coords = route_feature['geometry']['coordinates']
                
                if not route_coords or len(route_coords) < 2:
                    print(f"  Invalid {route_type} route coordinates")
                    continue
                
                route_line = LineString(route_coords)
                
                # Find unsafe hexagons that intersect this route
                intersecting_unsafe = []
                for unsafe_hex in unsafe_hexagons:
                    hex_geom = unsafe_hex['geometry']
                    # Use multiple intersection checks to be thorough
                    if (route_line.intersects(hex_geom) or 
                        route_line.crosses(hex_geom) or
                        route_line.within(hex_geom) or
                        hex_geom.contains(route_line) or
                        route_line.touches(hex_geom)):
                        intersecting_unsafe.append(unsafe_hex)
                
                print(f"  {route_type} route: {len(intersecting_unsafe)} unsafe hexagons intersect")
                alerts[route_type]['unsafe_hex_count'] = len(intersecting_unsafe)
                
                if len(intersecting_unsafe) == 0:
                    continue
                
                # For each unsafe hexagon, find which route segments intersect
                # Use the actual intersection geometry to identify all affected segments
                unsafe_segment_indices = set()
                
                # Method 1: Check each segment against all intersecting unsafe hexagons
                for i in range(len(route_coords) - 1):
                    segment = LineString([route_coords[i], route_coords[i + 1]])
                    
                    # Check this segment against all unsafe hexagons
                    for unsafe_hex in intersecting_unsafe:
                        hex_geom = unsafe_hex['geometry']
                        
                        # Multiple intersection checks to catch all cases
                        try:
                            if (segment.intersects(hex_geom) or 
                                segment.crosses(hex_geom) or
                                segment.within(hex_geom) or
                                hex_geom.contains(segment) or
                                segment.touches(hex_geom) or
                                hex_geom.intersects(segment)):
                                # Mark this segment index
                                unsafe_segment_indices.add(i)
                                # Also mark adjacent segments to ensure continuity
                                if i + 1 < len(route_coords) - 1:
                                    unsafe_segment_indices.add(i + 1)
                                if i > 0:
                                    unsafe_segment_indices.add(i - 1)
                                break  # Found intersection, no need to check other hexagons for this segment
                        except:
                            # If any check fails, still mark the segment if basic intersect works
                            try:
                                if segment.intersects(hex_geom):
                                    unsafe_segment_indices.add(i)
                                    if i + 1 < len(route_coords) - 1:
                                        unsafe_segment_indices.add(i + 1)
                                    if i > 0:
                                        unsafe_segment_indices.add(i - 1)
                                    break
                            except:
                                pass
                
                # Method 2: Check if any route coordinates are inside unsafe hexagons
                # This catches cases where the route passes through the center of a hexagon
                for i, coord in enumerate(route_coords):
                    point = Point(coord)
                    for unsafe_hex in intersecting_unsafe:
                        hex_geom = unsafe_hex['geometry']
                        try:
                            if (hex_geom.contains(point) or 
                                point.within(hex_geom) or
                                hex_geom.touches(point)):
                                # Mark this point and adjacent segments
                                if i < len(route_coords) - 1:
                                    unsafe_segment_indices.add(i)
                                if i > 0:
                                    unsafe_segment_indices.add(i - 1)
                                break
                        except:
                            pass
                
                # Method 3: For each unsafe hexagon, ensure we catch all segments
                # by checking if segments are within or touch the hexagon boundary
                for unsafe_hex in intersecting_unsafe:
                    hex_geom = unsafe_hex['geometry']
                    hex_boundary = hex_geom.boundary if hasattr(hex_geom, 'boundary') else hex_geom
                    
                    # Check each segment one more time with boundary check
                    for i in range(len(route_coords) - 1):
                        segment = LineString([route_coords[i], route_coords[i + 1]])
                        try:
                            # Check if segment touches or is within the hexagon
                            if (segment.intersects(hex_boundary) or
                                segment.intersects(hex_geom) or
                                segment.touches(hex_geom)):
                                unsafe_segment_indices.add(i)
                                # Mark adjacent for continuity
                                if i + 1 < len(route_coords) - 1:
                                    unsafe_segment_indices.add(i + 1)
                                if i > 0:
                                    unsafe_segment_indices.add(i - 1)
                        except:
                            pass
                
                alerts[route_type]['unsafe_segments'] = sorted(list(unsafe_segment_indices))
                print(f"  {route_type} route: {len(unsafe_segment_indices)} unsafe segments identified")
                
            except Exception as e:
                print(f"  ✗ Error processing {route_type} route: {e}")
                continue
        
        # Save alerts for this route pair
        output_file = OUTPUT_DIR / f"{route_pair}.json"
        save_json(alerts, output_file)
        print(f"  ✓ Saved alerts to {output_file.name}")
        processed_count += 1
    
    print(f"\n✓ Processed {processed_count} routes")
    print(f"✓ Security alerts saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
