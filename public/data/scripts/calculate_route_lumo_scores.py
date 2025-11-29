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
BRIGHT_THRESHOLD = 0.1  # Lower threshold for considering an area "bright" (light_score + vibrancy_score)
MIN_SCORE = 60.0  # Minimum score percentage (will scale up if needed)
MAX_SCORE = 100.0  # Maximum score percentage

# Global variables for normalization (set in main())
BASE_MIN = 0.0
BASE_MAX = 100.0

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

def calculate_lumo_score_percentage(route_geom, spatial_index, route_length_meters=None, sample_distance=50):
    """
    Calculate what percentage of a route passes through bright areas.
    Uses weighted scoring that considers both brightness and route characteristics.
    
    Args:
        route_geom: Shapely LineString geometry of the route
        spatial_index: Tuple of (STRtree, geometries list, properties list) from hexagons
        route_length_meters: Length of route in meters (for travel time weighting)
        sample_distance: Distance in meters between sample points
    
    Returns:
        Percentage (0-100) of route that is bright, scaled to ensure minimum score
    """
    if route_geom.geom_type != 'LineString':
        return MIN_SCORE
    
    # Sample points along the route
    sample_points = sample_points_along_line(route_geom, sample_distance)
    
    if not sample_points:
        return MIN_SCORE
    
    # Calculate weighted scores (not just binary bright/not bright)
    total_score = 0.0
    total_weight = 0.0
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
            
            # Weighted scoring: higher brightness = higher contribution
            # Normalize brightness to 0-1 scale (assuming max is around 5-10)
            normalized_brightness = min(combined_brightness / 5.0, 1.0)
            
            # Weight by brightness level (not just binary)
            weight = 1.0 + (normalized_brightness * 2.0)  # Weight ranges from 1.0 to 3.0
            score = normalized_brightness * 100.0
            
            total_score += score * weight
            total_weight += weight
            
            if combined_brightness >= BRIGHT_THRESHOLD:
                bright_count += 1
    
    if total_count == 0:
        return MIN_SCORE
    
    # Calculate base percentage from weighted average
    if total_weight > 0:
        base_percentage = total_score / total_weight
    else:
        base_percentage = (bright_count / total_count) * 100
    
    # Add travel time bonus (longer routes get slight boost)
    travel_time_bonus = 0.0
    if route_length_meters:
        # Routes longer than 2km get a small bonus (up to 5%)
        if route_length_meters > 2000:
            travel_time_bonus = min((route_length_meters - 2000) / 10000.0 * 5.0, 5.0)
    
    # Scale to ensure scores are in 60-100% range
    # Normalize base_percentage using the actual min/max found across all routes
    # Then map to the full 60-100% range
    if BASE_MAX > BASE_MIN:
        # Normalize: map BASE_MIN-BASE_MAX to 0-1
        normalized = (base_percentage - BASE_MIN) / (BASE_MAX - BASE_MIN)
        # Scale: map 0-1 to 60-100
        scaled_percentage = MIN_SCORE + normalized * (MAX_SCORE - MIN_SCORE)
    else:
        # Fallback: if all routes have same base score, give them middle of range
        scaled_percentage = (MIN_SCORE + MAX_SCORE) / 2.0
    
    # Add travel time bonus
    final_percentage = scaled_percentage + travel_time_bonus
    
    # Ensure we stay within bounds
    final_percentage = max(MIN_SCORE, min(final_percentage, MAX_SCORE))
    
    return round(final_percentage, 2)

def calculate_route_length(route_geom):
    """Calculate route length in meters."""
    # Project to metric CRS for accurate distance
    wgs84 = pyproj.CRS('EPSG:4326')
    ch1903 = pyproj.CRS('EPSG:2056')
    project_to_metric = pyproj.Transformer.from_crs(wgs84, ch1903, always_xy=True).transform
    
    # Transform to metric and calculate length
    line_metric = transform(project_to_metric, route_geom)
    return line_metric.length

def process_route_file(route_file, spatial_index):
    """Process a single route file and add lumo_score_percentage."""
    print(f"Processing {route_file.name}...")
    
    route_data = load_geojson(route_file)
    
    for feature in route_data.get('features', []):
        if feature['geometry']['type'] == 'LineString':
            route_geom = shape(feature['geometry'])
            
            # Calculate route length for travel time weighting
            route_length = calculate_route_length(route_geom)
            
            # Calculate lumo score percentage
            lumo_percentage = calculate_lumo_score_percentage(route_geom, spatial_index, route_length)
            
            # Add to properties
            if 'properties' not in feature:
                feature['properties'] = {}
            
            feature['properties']['lumo_score_percentage'] = lumo_percentage
            
            print(f"  Route {route_file.stem}: {lumo_percentage}% (length: {route_length:.0f}m)")
    
    # Save updated route file
    save_geojson(route_data, route_file)
    return route_data

def calculate_base_percentage(route_geom, spatial_index, route_length_meters=None, sample_distance=50):
    """
    Calculate base percentage without final scaling (for normalization).
    Returns the raw base percentage.
    """
    if route_geom.geom_type != 'LineString':
        return 0.0
    
    sample_points = sample_points_along_line(route_geom, sample_distance)
    if not sample_points:
        return 0.0
    
    total_score = 0.0
    total_weight = 0.0
    
    for point in sample_points:
        hexagon = get_hexagon_for_point(point, spatial_index)
        if hexagon:
            light_score = hexagon.get('light_score', 0.0) or 0.0
            vibrancy_score = hexagon.get('vibrancy_score', 0.0) or 0.0
            combined_brightness = light_score + vibrancy_score
            
            normalized_brightness = min(combined_brightness / 5.0, 1.0)
            weight = 1.0 + (normalized_brightness * 2.0)
            score = normalized_brightness * 100.0
            
            total_score += score * weight
            total_weight += weight
    
    if total_weight > 0:
        return total_score / total_weight
    return 0.0

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
    
    # First pass: collect base percentages to find min/max for normalization
    print("\nFirst pass: calculating base scores...")
    base_scores = {}
    for route_file in route_files:
        try:
            route_data = load_geojson(route_file)
            for feature in route_data.get('features', []):
                if feature['geometry']['type'] == 'LineString':
                    route_geom = shape(feature['geometry'])
                    base_percentage = calculate_base_percentage(route_geom, spatial_index)
                    base_scores[route_file.stem] = base_percentage
        except Exception as e:
            print(f"  Error processing {route_file.name}: {e}")
    
    # Find min and max base scores
    if base_scores:
        min_base = min(base_scores.values())
        max_base = max(base_scores.values())
        print(f"Base score range: {min_base:.2f}% - {max_base:.2f}%")
    else:
        min_base = 0.0
        max_base = 100.0
    
    # Store normalization range globally for use in calculate_lumo_score_percentage
    global BASE_MIN, BASE_MAX
    BASE_MIN = min_base
    BASE_MAX = max_base if max_base > min_base else min_base + 1.0  # Avoid division by zero
    
    # Second pass: process routes with normalized scaling
    print("\nSecond pass: processing routes with normalized scores...")
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
    print(f"  Score range: {MIN_SCORE}% - {MAX_SCORE}%")
    print(f"  Bright threshold: {BRIGHT_THRESHOLD} (light_score + vibrancy_score)")

if __name__ == "__main__":
    main()

