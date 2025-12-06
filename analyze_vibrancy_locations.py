#!/usr/bin/env python3
"""
Analyzes vibrancy (POI density) in Zurich and finds locations with highest vibrancy.
Generates a JSON file with the results for use in the app.
"""

import json
import math
from pathlib import Path
from typing import List, Dict, Tuple


def get_center_coordinates(geometry: Dict) -> Tuple[float, float]:
    """Calculate center coordinates of a polygon."""
    if geometry['type'] == 'Polygon':
        coords = geometry['coordinates'][0]  # First ring (exterior)
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        return (sum(lons) / len(lons), sum(lats) / len(lats))
    return (0, 0)


def get_location_description(location_name: str) -> str:
    """Get a short description for a location."""
    descriptions = {
        "Bahnhofstrasse": "Famous shopping street in the heart of Zurich",
        "Limmatquai": "Historic quay along the Limmat River",
        "Paradeplatz": "Financial district and banking center",
        "Sechseläutenplatz": "Large square near the opera house",
        "Niederdorf": "Old town area with narrow streets",
        "Bellevue": "Central square with tram connections",
        "Langstrasse": "Vibrant nightlife and cultural district",
        "Hardbrücke": "Major bridge connecting west and east Zurich",
        "Altstetten": "Residential area in western Zurich",
        "Wiedikon": "Residential district with parks",
        "Wollishofen": "Quiet residential area by the lake",
        "Enge": "Upscale residential neighborhood",
        "Oerlikon": "Business district and transport hub",
        "Seebach": "Residential area in northern Zurich",
        "Affoltern": "Residential district in the north",
        "Schwamendingen": "Residential area in eastern Zurich",
        "Hirzenbach": "Residential neighborhood in the east",
        "Dübendorf": "Suburban area east of Zurich",
        "Leimbach": "Residential area in southern Zurich",
        "Adliswil": "Town south of Zurich",
        "Kilchberg": "Residential area by the lake",
        "Escher Wyss": "Industrial area converted to modern district",
        "City Center": "Central business and shopping district",
        "West Zurich": "Western part of the city",
        "East Zurich": "Eastern part of the city",
        "North Zurich": "Northern part of the city",
        "South Zurich": "Southern part of the city",
        "Zurich": "Zurich area"
    }
    return descriptions.get(location_name, "Area in Zurich")


def reverse_geocode_simple(lon: float, lat: float) -> str:
    """
    Simple reverse geocoding using known Zurich landmarks and districts.
    """
    # Extended list of Zurich locations with coordinates
    zurich_areas = {
        # City center
        (8.5417, 47.3769): "Bahnhofstrasse",
        (8.5481, 47.3686): "Limmatquai",
        (8.5456, 47.3733): "Paradeplatz",
        (8.5500, 47.3800): "Sechseläutenplatz",
        (8.5430, 47.3700): "Niederdorf",
        (8.5380, 47.3750): "Bellevue",
        
        # West
        (8.5303, 47.3667): "Langstrasse",
        (8.5172, 47.3708): "Hardbrücke",
        (8.5150, 47.3830): "Hardbrücke",
        (8.5200, 47.3500): "Altstetten",
        (8.5100, 47.3600): "Wiedikon",
        (8.5350, 47.3600): "Wiedikon",
        (8.5000, 47.3400): "Wollishofen",
        (8.4900, 47.3500): "Enge",
        
        # North
        (8.5600, 47.3900): "Oerlikon",
        (8.5500, 47.4000): "Oerlikon",
        (8.5400, 47.4100): "Seebach",
        (8.5300, 47.4200): "Affoltern",
        
        # East
        (8.5600, 47.3700): "Schwamendingen",
        (8.5700, 47.3600): "Hirzenbach",
        (8.5800, 47.3500): "Dübendorf",
        
        # South
        (8.5400, 47.3400): "Leimbach",
        (8.5300, 47.3300): "Adliswil",
        (8.5200, 47.3200): "Kilchberg",
        
        # Additional areas
        (8.5100, 47.3800): "Escher Wyss",
        (8.5050, 47.3750): "Escher Wyss",
        (8.4950, 47.3680): "Escher Wyss",
        (8.4900, 47.3650): "Escher Wyss",
        (8.5250, 47.3850): "Hardbrücke",
        (8.5090, 47.4200): "Oerlikon",
        (8.5150, 47.3830): "Hardbrücke",
    }
    
    # Find closest area
    min_dist = float('inf')
    closest_area = None
    
    for (area_lon, area_lat), area_name in zurich_areas.items():
        dist = math.sqrt((lon - area_lon)**2 + (lat - area_lat)**2)
        if dist < min_dist:
            min_dist = dist
            closest_area = area_name
    
    # Use a larger threshold for better coverage
    if min_dist < 0.03:  # Within ~3km
        return closest_area
    
    # Try to determine district based on coordinates
    if 8.52 <= lon <= 8.55 and 47.36 <= lat <= 47.38:
        return "City Center"
    elif lon < 8.52:
        return "West Zurich"
    elif lon > 8.55:
        return "East Zurich"
    elif lat > 47.38:
        return "North Zurich"
    elif lat < 47.36:
        return "South Zurich"
    
    return "Zurich"


def analyze_vibrancy_data(geojson_path: Path) -> Dict:
    """Analyze vibrancy data and find highest vibrancy locations."""
    print(f"Loading data from {geojson_path}...")
    
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    locations = []
    
    for feature in data['features']:
        num_points = feature['properties'].get('NUMPOINTS', 0.0)
        vibrancy_score = float(num_points)  # POI count = vibrancy
        
        geometry = feature['geometry']
        lon, lat = get_center_coordinates(geometry)
        location_name = reverse_geocode_simple(lon, lat)
        description = get_location_description(location_name)
        
        locations.append({
            'vibrancy': vibrancy_score,
            'lon': lon,
            'lat': lat,
            'location': location_name,
            'description': description,
            'coordinates': [lon, lat]
        })
    
    # Sort by vibrancy (POI count)
    locations.sort(key=lambda x: x['vibrancy'], reverse=True)
    
    # Get top 3 highest
    highest = locations[:3]
    
    return {
        'highest': highest,
        'total_locations': len(locations),
        'avg_vibrancy': sum(l['vibrancy'] for l in locations) / len(locations) if locations else 0,
        'max_vibrancy': locations[0]['vibrancy'] if locations else 0,
        'min_vibrancy': locations[-1]['vibrancy'] if locations else 0
    }


def analyze_combined_data(lighting_path: Path, vibrancy_path: Path) -> Dict:
    """Analyze combined lighting and vibrancy data."""
    print(f"Loading lighting data from {lighting_path}...")
    with open(lighting_path, 'r', encoding='utf-8') as f:
        lighting_data = json.load(f)
    
    print(f"Loading vibrancy data from {vibrancy_path}...")
    with open(vibrancy_path, 'r', encoding='utf-8') as f:
        vibrancy_data = json.load(f)
    
    # Create maps for quick lookup
    lighting_map = {}
    for feature in lighting_data['features']:
        geometry = feature['geometry']
        lon, lat = get_center_coordinates(geometry)
        key = (round(lon, 6), round(lat, 6))
        color = feature['properties'].get('color', '#000000')
        # Calculate lighting intensity from color
        hex_color = color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        # Simple brightness calculation
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        lighting_map[key] = brightness / 255.0  # Normalize to 0-1
    
    locations = []
    
    for feature in vibrancy_data['features']:
        num_points = feature['properties'].get('NUMPOINTS', 0.0)
        vibrancy_score = float(num_points)
        
        geometry = feature['geometry']
        lon, lat = get_center_coordinates(geometry)
        key = (round(lon, 6), round(lat, 6))
        
        # Get lighting intensity for this location
        lighting_intensity = lighting_map.get(key, 0.0)
        
        # Combined score (normalize both to 0-1 and average)
        # Normalize vibrancy (assuming max is around 100)
        normalized_vibrancy = min(vibrancy_score / 100.0, 1.0) if vibrancy_score > 0 else 0.0
        combined_score = (lighting_intensity + normalized_vibrancy) / 2.0
        
        location_name = reverse_geocode_simple(lon, lat)
        description = get_location_description(location_name)
        
        locations.append({
            'combined_score': combined_score,
            'lighting': lighting_intensity,
            'vibrancy': normalized_vibrancy,
            'lon': lon,
            'lat': lat,
            'location': location_name,
            'description': description,
            'coordinates': [lon, lat]
        })
    
    # Sort by combined score
    locations.sort(key=lambda x: x['combined_score'], reverse=True)
    
    # Get top 3 highest
    highest = locations[:3]
    
    return {
        'highest': highest,
        'total_locations': len(locations),
        'avg_combined': sum(l['combined_score'] for l in locations) / len(locations) if locations else 0,
        'max_combined': locations[0]['combined_score'] if locations else 0,
        'min_combined': locations[-1]['combined_score'] if locations else 0
    }


def main():
    base_path = Path(__file__).parent
    vibrancy_path = base_path / 'public' / 'data' / 'hex_vibrancy_100m.geojson'
    lighting_path = base_path / 'public' / 'data' / 'hex_light_100m.geojson'
    
    # Analyze vibrancy
    print("\n=== Analyzing Vibrancy Data ===")
    vibrancy_results = analyze_vibrancy_data(vibrancy_path)
    vibrancy_output = base_path / 'public' / 'data' / 'vibrancy_locations.json'
    with open(vibrancy_output, 'w', encoding='utf-8') as f:
        json.dump(vibrancy_results, f, indent=2, ensure_ascii=False)
    print(f"Vibrancy results saved to {vibrancy_output}")
    
    # Analyze combined
    print("\n=== Analyzing Combined Data ===")
    combined_results = analyze_combined_data(lighting_path, vibrancy_path)
    combined_output = base_path / 'public' / 'data' / 'combined_locations.json'
    with open(combined_output, 'w', encoding='utf-8') as f:
        json.dump(combined_results, f, indent=2, ensure_ascii=False)
    print(f"Combined results saved to {combined_output}")
    
    print("\nAnalysis complete!")
    if vibrancy_results['highest']:
        print(f"  - Highest vibrancy: {vibrancy_results['highest'][0]['location']} ({vibrancy_results['highest'][0]['vibrancy']:.1f} POIs)")
    if combined_results['highest']:
        print(f"  - Highest combined: {combined_results['highest'][0]['location']} ({combined_results['highest'][0]['combined_score']:.4f})")


if __name__ == '__main__':
    main()
