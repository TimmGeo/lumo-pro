#!/usr/bin/env python3
"""
Calculate Lumo Score percentage for each route.

This script calculates what percentage of each route passes through "bright" areas
(based on light_score + vibrancy_score from hexagon data) and adds this as a
property to each route GeoJSON file.
"""

import json
import os
from pathlib import Path
from shapely.geometry import Point, LineString, shape, mapping
from shapely.ops import transform
from shapely.strtree import STRtree
import pyproj
from collections import defaultdict

# Configuration - paths relative to script location
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent
ROUTES_DIR = DATA_DIR / "routes"
LUMO_SCORE_FILE = DATA_DIR / "lumo_score.geojson"
BRIGHT_THRESHOLD = 0.5  # Threshold for considering an area "bright" (light_score + vibrancy_score)

def load_geojson(filepath):
    """Load a GeoJSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_geojson(data, filepath):
    """Save data as GeoJSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def create_spatial_index(hexagons):
    """
    Create an R-tree spatial index for fast point-in-polygon queries.
    Returns a tuple of (STRtree index, list of geometries, list of properties).
    """
    geometries = []
    properties = []
    
    for feature in hexagons['features']:
        geom = shape(feature['geometry'])
        props = feature['properties']
        geometries.append(geom)
        properties.append(props)
    
    # Create STRtree for efficient spatial queries
    tree = STRtree(geometries)
    
    return tree, geometries, properties

def get_hexagon_for_point(point, spatial_index):
    """
    Find which hexagon contains a given point using R-tree index.
    Returns the hexagon properties or None.
    
    Args:
        point: Shapely Point geometry
        spatial_index: Tuple of (STRtree, geometries list, properties list)
    """
    tree, geometries, properties = spatial_index
    
    # Query the R-tree for potential matches
    possible_matches = tree.query(point)
    
    # Check which geometry actually contains the point
    for idx in possible_matches:
        geom = geometries[idx]
        if geom.contains(point) or geom.touches(point):
            return properties[idx]
    
    return None

def sample_points_along_line(line_geom, sample_distance=50):
    """
    Sample points along a LineString at regular intervals.
    sample_distance: distance in meters between samples.
    """
    # Project to a metric CRS for distance calculations
    wgs84 = pyproj.CRS('EPSG:4326')
    # Use Swiss coordinate system (CH1903+ / LV95) for accurate distance
    ch1903 = pyproj.CRS('EPSG:2056')
    project_to_metric = pyproj.Transformer.from_crs(wgs84, ch1903, always_xy=True).transform
    project_to_wgs84 = pyproj.Transformer.from_crs(ch1903, wgs84, always_xy=True).transform
    
    # Transform to metric
    line_metric = transform(project_to_metric, line_geom)
    
    # Sample points
    points = []
    length = line_metric.length
    distance = 0
    
    while distance < length:
        point_metric = line_metric.interpolate(distance)
        point_wgs84 = transform(project_to_wgs84, point_metric)
        points.append(point_wgs84)
        distance += sample_distance
    
    # Always include the end point
    if length > 0:
        end_point_metric = line_metric.interpolate(length)
        end_point_wgs84 = transform(project_to_wgs84, end_point_metric)
        if end_point_wgs84.distance(Point(line_geom.coords[-1])) > 1e-6:
            points.append(end_point_wgs84)
    
    return points

def calculate_lumo_score_percentage(route_geom, spatial_index, sample_distance=50):
    """
    Calculate what percentage of a route passes through bright areas.
    
    Args:
        route_geom: Shapely LineString geometry of the route
        spatial_index: Tuple of (STRtree, geometries list, properties list) from hexagons
        sample_distance: Distance in meters between sample points
    
    Returns:
        Percentage (0-100) of route that is bright
    """
    if route_geom.geom_type != 'LineString':
        return 0.0
    
    # Sample points along the route
    sample_points = sample_points_along_line(route_geom, sample_distance)
    
    if not sample_points:
        return 0.0
    
    bright_count = 0
    total_count = 0
    
    for point in sample_points:
        hexagon = get_hexagon_for_point(point, spatial_index)
        if hexagon:
            total_count += 1
            # Calculate brightness: light_score + vibrancy_score
            light_score = hexagon.get('light_score', 0.0) or 0.0
            vibrancy_score = hexagon.get('vibrancy_score', 0.0) or 0.0
            combined_brightness = light_score + vibrancy_score
            
            if combined_brightness >= BRIGHT_THRESHOLD:
                bright_count += 1
    
    if total_count == 0:
        return 0.0
    
    percentage = (bright_count / total_count) * 100
    return round(percentage, 2)

def process_route_file(route_file, spatial_index):
    """Process a single route file and add lumo_score_percentage."""
    print(f"Processing {route_file.name}...")
    
    route_data = load_geojson(route_file)
    
    for feature in route_data.get('features', []):
        if feature['geometry']['type'] == 'LineString':
            route_geom = shape(feature['geometry'])
            
            # Calculate lumo score percentage
            lumo_percentage = calculate_lumo_score_percentage(route_geom, spatial_index)
            
            # Add to properties
            if 'properties' not in feature:
                feature['properties'] = {}
            
            feature['properties']['lumo_score_percentage'] = lumo_percentage
            
            print(f"  Route {route_file.stem}: {lumo_percentage}% bright")
    
    # Save updated route file
    save_geojson(route_data, route_file)
    return route_data

def main():
    """Main function to process all routes."""
    print("=" * 60)
    print("Route Lumo Score Calculator")
    print("=" * 60)
    
    # Check if files exist
    if not LUMO_SCORE_FILE.exists():
        print(f"Error: {LUMO_SCORE_FILE} not found!")
        return
    
    if not ROUTES_DIR.exists():
        print(f"Error: {ROUTES_DIR} not found!")
        return
    
    # Load hexagon data
    print(f"\nLoading hexagon data from {LUMO_SCORE_FILE}...")
    lumo_data = load_geojson(LUMO_SCORE_FILE)
    print(f"Loaded {len(lumo_data['features'])} hexagons")
    
    # Create spatial index
    print("Creating spatial index...")
    spatial_index = create_spatial_index(lumo_data)
    print(f"Index created with {len(spatial_index[1])} hexagons")
    
    # Find all route files
    route_files = sorted(ROUTES_DIR.glob("*.geojson"))
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
            route_data = process_route_file(route_file, spatial_index)
            route_name = route_file.stem
            
            # Extract result for summary
            for feature in route_data.get('features', []):
                if 'lumo_score_percentage' in feature.get('properties', {}):
                    results[route_name] = feature['properties']['lumo_score_percentage']
        except Exception as e:
            print(f"  Error processing {route_file.name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for route_name, percentage in sorted(results.items()):
        print(f"  {route_name}: {percentage}% bright")
    
    print(f"\n✓ Processed {len(results)} routes successfully!")
    print(f"  Bright threshold: {BRIGHT_THRESHOLD} (light_score + vibrancy_score)")

if __name__ == "__main__":
    main()

