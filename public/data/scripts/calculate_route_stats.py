#!/usr/bin/env python3
"""
Calculate comprehensive route statistics for each route.

This script calculates:
- Route length in meters and kilometers
- Expected walk duration (based on average walking speed)
- POI counts along the route (restaurants, bars, cafes, etc.)
- POI frequency (e.g., "one restaurant every X minutes")
"""

import json
import os
from pathlib import Path
from shapely.geometry import shape, Point
from shapely.ops import transform
from shapely.strtree import STRtree
import pyproj

# Configuration - paths relative to script location
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent
ROUTES_DIR = DATA_DIR / "routes_wgs84"
POIS_FILE = DATA_DIR / "vibrancy_points.geojson"

# Constants
AVERAGE_WALKING_SPEED_KMH = 5.0  # Average walking speed: 5 km/h
AVERAGE_WALKING_SPEED_MS = AVERAGE_WALKING_SPEED_KMH / 3.6  # Convert to m/s
POI_BUFFER_DISTANCE = 50  # Distance in meters to consider POIs "along" the route

def load_geojson(filepath):
    """Load a GeoJSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_geojson(data, filepath):
    """Save data as GeoJSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def calculate_route_length(route_geom):
    """Calculate route length in meters."""
    # Project to a metric CRS for accurate distance
    wgs84 = pyproj.CRS('EPSG:4326')
    # Use Swiss coordinate system (CH1903+ / LV95) for accurate distance
    ch1903 = pyproj.CRS('EPSG:2056')
    project_to_metric = pyproj.Transformer.from_crs(wgs84, ch1903, always_xy=True).transform
    
    # Transform to metric and calculate length
    line_metric = transform(project_to_metric, route_geom)
    return line_metric.length

def calculate_walk_duration(length_meters):
    """Calculate expected walk duration in minutes."""
    if length_meters <= 0:
        return 0
    
    # Duration in seconds
    duration_seconds = length_meters / AVERAGE_WALKING_SPEED_MS
    
    # Convert to minutes (round to nearest minute)
    duration_minutes = round(duration_seconds / 60)
    
    return max(1, duration_minutes)  # At least 1 minute

def format_duration(minutes):
    """Format duration as human-readable string."""
    if minutes < 60:
        return f"{minutes} min"
    else:
        hours = minutes // 60
        mins = minutes % 60
        if mins == 0:
            return f"{hours} h"
        else:
            return f"{hours} h {mins} min"

def load_pois():
    """Load POI data and create spatial index."""
    if not POIS_FILE.exists():
        print(f"Warning: {POIS_FILE} not found, skipping POI calculations")
        return None, None
    
    pois_data = load_geojson(POIS_FILE)
    pois = []
    poi_types = {}
    
    for feature in pois_data.get('features', []):
        if feature['geometry']['type'] == 'MultiPoint' and feature['geometry']['coordinates']:
            coords = feature['geometry']['coordinates'][0]
            poi_point = Point(coords[0], coords[1])
            poi_type = feature['properties'].get('Type', 'Unknown')
            pois.append((poi_point, poi_type))
            
            # Count by type
            poi_types[poi_type] = poi_types.get(poi_type, 0) + 1
    
    # Create spatial index
    if pois:
        spatial_index = STRtree([poi[0] for poi in pois])
        return pois, spatial_index
    
    return None, None

def find_pois_along_route(route_geom, pois, spatial_index):
    """
    Find POIs within buffer distance of the route.
    
    Returns a dictionary with counts by POI type.
    """
    if not pois or not spatial_index:
        return {}
    
    # Project route to metric CRS for buffer calculation
    wgs84 = pyproj.CRS('EPSG:4326')
    ch1903 = pyproj.CRS('EPSG:2056')
    project_to_metric = pyproj.Transformer.from_crs(wgs84, ch1903, always_xy=True).transform
    project_to_wgs84 = pyproj.Transformer.from_crs(ch1903, wgs84, always_xy=True).transform
    
    # Transform route to metric
    route_metric = transform(project_to_metric, route_geom)
    
    # Create buffer around route (in meters)
    route_buffer = route_metric.buffer(POI_BUFFER_DISTANCE)
    
    # Transform buffer back to WGS84 for spatial queries
    route_buffer_wgs84 = transform(project_to_wgs84, route_buffer)
    
    # Find POIs within buffer
    poi_counts = {}
    
    # Query spatial index with buffer
    found_indices = spatial_index.query(route_buffer_wgs84)
    
    # Get all POI geometries from the list
    poi_geoms = [poi[0] for poi in pois]
    
    for idx in found_indices:
        if idx < len(poi_geoms):
            poi_point = poi_geoms[idx]
            # Check if POI is actually within buffer
            if route_buffer_wgs84.contains(poi_point) or route_buffer_wgs84.touches(poi_point):
                poi_type = pois[idx][1]
                poi_counts[poi_type] = poi_counts.get(poi_type, 0) + 1
    
    return poi_counts

def calculate_poi_frequency(poi_counts, walk_duration_minutes):
    """
    Calculate frequency of POIs along the route.
    
    Returns a dictionary with formatted frequency strings.
    """
    frequencies = {}
    
    for poi_type, count in poi_counts.items():
        if count > 0 and walk_duration_minutes > 0:
            # Calculate average time between POIs
            avg_minutes_between = walk_duration_minutes / count
            
            if avg_minutes_between < 1:
                frequencies[poi_type] = f"every {int(avg_minutes_between * 60)} sec"
            elif avg_minutes_between < 60:
                frequencies[poi_type] = f"every {int(avg_minutes_between)} min"
            else:
                hours = int(avg_minutes_between // 60)
                mins = int(avg_minutes_between % 60)
                if mins == 0:
                    frequencies[poi_type] = f"every {hours} h"
                else:
                    frequencies[poi_type] = f"every {hours} h {mins} min"
        else:
            frequencies[poi_type] = None
    
    return frequencies

def calculate_route_stats(route_geom, pois, spatial_index):
    """
    Calculate comprehensive statistics for a route.
    
    Returns a dictionary with:
    - length_meters: Route length in meters
    - length_km: Route length in kilometers (rounded to 2 decimals)
    - walk_duration_minutes: Expected walk duration in minutes
    - walk_duration_formatted: Formatted duration string
    - poi_counts: Dictionary of POI counts by type
    - poi_frequencies: Dictionary of POI frequencies by type
    """
    if route_geom.geom_type != 'LineString':
        return {
            'length_meters': 0,
            'length_km': 0.0,
            'walk_duration_minutes': 0,
            'walk_duration_formatted': '0 min',
            'poi_counts': {},
            'poi_frequencies': {}
        }
    
    # Calculate length
    length_meters = calculate_route_length(route_geom)
    length_km = round(length_meters / 1000, 2)
    
    # Calculate walk duration
    walk_duration_minutes = calculate_walk_duration(length_meters)
    walk_duration_formatted = format_duration(walk_duration_minutes)
    
    # Find POIs along route
    poi_counts = find_pois_along_route(route_geom, pois, spatial_index) if pois and spatial_index else {}
    
    # Calculate POI frequencies
    poi_frequencies = calculate_poi_frequency(poi_counts, walk_duration_minutes) if poi_counts else {}
    
    return {
        'length_meters': round(length_meters, 0),
        'length_km': length_km,
        'walk_duration_minutes': walk_duration_minutes,
        'walk_duration_formatted': walk_duration_formatted,
        'poi_counts': poi_counts,
        'poi_frequencies': poi_frequencies
    }

def process_route_file(route_file, pois, spatial_index):
    """Process a single route file and add statistics."""
    print(f"Processing {route_file.name}...")
    
    route_data = load_geojson(route_file)
    
    for feature in route_data.get('features', []):
        if feature['geometry']['type'] == 'LineString':
            route_geom = shape(feature['geometry'])
            
            # Calculate route statistics
            stats = calculate_route_stats(route_geom, pois, spatial_index)
            
            # Add to properties
            if 'properties' not in feature:
                feature['properties'] = {}
            
            # Add/update statistics
            feature['properties']['route_length_meters'] = int(stats['length_meters'])
            feature['properties']['route_length_km'] = stats['length_km']
            feature['properties']['walk_duration_minutes'] = stats['walk_duration_minutes']
            feature['properties']['walk_duration_formatted'] = stats['walk_duration_formatted']
            
            # Add POI counts and frequencies
            feature['properties']['poi_counts'] = stats['poi_counts']
            feature['properties']['poi_frequencies'] = stats['poi_frequencies']
            
            # Create summary string
            poi_summary = ", ".join([f"{count} {poi_type}" for poi_type, count in stats['poi_counts'].items()])
            if poi_summary:
                print(f"  Route {route_file.stem}: {stats['length_km']} km, {stats['walk_duration_formatted']}, POIs: {poi_summary}")
            else:
                print(f"  Route {route_file.stem}: {stats['length_km']} km, {stats['walk_duration_formatted']}, No POIs")
    
    # Save updated route file
    save_geojson(route_data, route_file)
    return route_data

def main():
    """Main function to process all routes."""
    print("=" * 60)
    print("Route Statistics Calculator")
    print("=" * 60)
    
    if not ROUTES_DIR.exists():
        print(f"Error: {ROUTES_DIR} not found!")
        return
    
    # Load POIs
    print("\nLoading POI data...")
    pois, spatial_index = load_pois()
    if pois:
        print(f"  Loaded {len(pois)} POIs")
        poi_types = {}
        for _, poi_type in pois:
            poi_types[poi_type] = poi_types.get(poi_type, 0) + 1
        print(f"  POI types: {', '.join([f'{count} {ptype}' for ptype, count in poi_types.items()])}")
    else:
        print("  No POI data available")
    
    # Find all route files (both fast _f and bright _b routes)
    route_files = sorted(ROUTES_DIR.glob("*_f.geojson")) + sorted(ROUTES_DIR.glob("*_b.geojson"))
    print(f"\nFound {len(route_files)} route files to process")
    
    if not route_files:
        print("No route files found!")
        return
    
    # Process each route file
    print("\nProcessing routes...")
    print("-" * 60)
    
    results = {}
    for route_file in route_files:
        try:
            route_data = process_route_file(route_file, pois, spatial_index)
            route_name = route_file.stem
            
            # Extract result for summary
            for feature in route_data.get('features', []):
                if 'route_length_km' in feature.get('properties', {}):
                    props = feature['properties']
                    poi_counts = props.get('poi_counts', {})
                    total_pois = sum(poi_counts.values())
                    results[route_name] = {
                        'length_km': props.get('route_length_km', 0),
                        'duration': props.get('walk_duration_formatted', '0 min'),
                        'total_pois': total_pois
                    }
        except Exception as e:
            print(f"  Error processing {route_file.name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for route_name, stats in sorted(results.items()):
        print(f"  {route_name}: {stats['length_km']} km, {stats['duration']}, {stats['total_pois']} POIs")
    
    print(f"\n✓ Processed {len(results)} routes successfully!")
    print(f"  Average walking speed: {AVERAGE_WALKING_SPEED_KMH} km/h")
    print(f"  POI buffer distance: {POI_BUFFER_DISTANCE} m")

if __name__ == "__main__":
    main()

