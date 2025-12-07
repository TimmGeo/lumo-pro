#!/usr/bin/env python3
"""
Calculate distances and walking times from hotspots to nearest routing hubs.
Outputs JSON files with enriched hotspot data.
"""

import json
import math
import os
from pathlib import Path

# Earth's radius in kilometers
R = 6371


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula."""
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def format_distance(distance_km):
    """Format distance as meters or kilometers."""
    distance_m = distance_km * 1000
    if distance_m < 1000:
        return f"{int(round(distance_m))}m"
    else:
        return f"{distance_km:.1f}km"


def format_time(distance_km, walking_speed_kmh=5):
    """Calculate and format walking time."""
    time_hours = distance_km / walking_speed_kmh
    time_minutes = round(time_hours * 60)
    if time_minutes < 60:
        return f"{time_minutes}min"
    else:
        return f"{time_hours:.1f}h"


def find_nearest_hub(hotspot_coords, routing_hubs):
    """Find the nearest routing hub to a hotspot."""
    hotspot_lon, hotspot_lat = hotspot_coords
    
    nearest_hub = None
    min_distance = float('inf')
    
    for hub in routing_hubs:
        hub_lon, hub_lat = hub['coordinates']
        distance = haversine_distance(hotspot_lat, hotspot_lon, hub_lat, hub_lon)
        
        if distance < min_distance:
            min_distance = distance
            nearest_hub = hub
    
    return nearest_hub, min_distance


def process_hotspots(hotspots_file, routing_hubs, output_file):
    """Process hotspots and add distance/time information."""
    with open(hotspots_file, 'r', encoding='utf-8') as f:
        hotspots_data = json.load(f)
    
    enriched_hotspots = []
    
    for feature in hotspots_data.get('features', []):
        properties = feature.get('properties', {})
        geometry = feature.get('geometry', {})
        coordinates = geometry.get('coordinates', [])
        
        if not coordinates or len(coordinates) < 2:
            continue
        
        # Find nearest hub
        nearest_hub, distance_km = find_nearest_hub(coordinates, routing_hubs)
        
        if nearest_hub:
            enriched_hotspot = {
                'name': properties.get('name', 'Unknown'),
                'fid': properties.get('fid'),
                'coordinates': coordinates,
                'lon': coordinates[0],
                'lat': coordinates[1],
                'nearest_hub': {
                    'id': nearest_hub['id'],
                    'name': nearest_hub.get('name', f"Hub {nearest_hub['id']}"),
                    'distance': format_distance(distance_km),
                    'distance_km': round(distance_km, 3),
                    'time': format_time(distance_km),
                    'time_minutes': round((distance_km / 5) * 60)
                }
            }
            enriched_hotspots.append(enriched_hotspot)
    
    # Sort by distance to nearest hub (closest first)
    enriched_hotspots.sort(key=lambda x: x['nearest_hub']['distance_km'])
    
    # Save to JSON file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched_hotspots, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Processed {len(enriched_hotspots)} hotspots -> {output_file}")
    return enriched_hotspots


def main():
    # Paths
    base_dir = Path('public/data')
    hotspots_dir = base_dir / 'hotspots_wgs84'
    routing_hubs_file = base_dir / 'routing_hubs.geojson'
    output_dir = base_dir
    
    # Load routing hubs
    with open(routing_hubs_file, 'r', encoding='utf-8') as f:
        routing_hubs_data = json.load(f)
    
    routing_hubs = []
    for feature in routing_hubs_data.get('features', []):
        props = feature.get('properties', {})
        coords = feature.get('geometry', {}).get('coordinates', [])
        if coords and len(coords) >= 2:
            routing_hubs.append({
                'id': props.get('id') or props.get('fid'),
                'name': props.get('locality') or props.get('neighborhood'),
                'coordinates': coords
            })
    
    print(f"📍 Loaded {len(routing_hubs)} routing hubs")
    
    # Process each hotspot type
    hotspot_files = {
        'lighting_hotspots.geojson': 'lighting_hotspots.json',
        'vibrancy_hotspots.geojson': 'vibrancy_hotspots.json',
        'combined_hotspots.geojson': 'combined_hotspots.json'
    }
    
    for input_file, output_file in hotspot_files.items():
        input_path = hotspots_dir / input_file
        output_path = output_dir / output_file
        
        if input_path.exists():
            process_hotspots(input_path, routing_hubs, output_path)
        else:
            print(f"⚠️  File not found: {input_path}")
    
    print("\n✨ All hotspots processed!")


if __name__ == '__main__':
    main()
