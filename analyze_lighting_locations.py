#!/usr/bin/env python3
"""
Analyzes lighting intensity in Zurich and finds locations with highest and lowest intensity.
Generates a JSON file with the results for use in the app.
"""

import json
import math
from pathlib import Path
from typing import List, Dict, Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB values."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def calculate_lighting_intensity(color: str) -> float:
    """
    Calculate lighting intensity from hex color.
    Lighter colors = higher intensity, darker colors = lower intensity.
    Uses relative luminance formula (perceived brightness).
    """
    r, g, b = hex_to_rgb(color)
    
    # Convert to relative luminance (perceived brightness)
    # Formula from WCAG: https://www.w3.org/WAI/GL/wiki/Relative_luminance
    def to_linear(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    
    r_lin = to_linear(r)
    g_lin = to_linear(g)
    b_lin = to_linear(b)
    
    # Relative luminance
    luminance = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
    
    return luminance


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
    # Zurich city center roughly: 8.52-8.55, 47.36-47.38
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


def analyze_lighting_data(geojson_path: Path) -> Dict:
    """Analyze lighting data and find highest/lowest intensity locations."""
    print(f"Loading data from {geojson_path}...")
    
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    locations = []
    
    for feature in data['features']:
        color = feature['properties'].get('color', '#000000')
        intensity = calculate_lighting_intensity(color)
        geometry = feature['geometry']
        lon, lat = get_center_coordinates(geometry)
        location_name = reverse_geocode_simple(lon, lat)
        
        location_name = reverse_geocode_simple(lon, lat)
        description = get_location_description(location_name)
        
        locations.append({
            'intensity': intensity,
            'color': color,
            'lon': lon,
            'lat': lat,
            'location': location_name,
            'description': description,
            'coordinates': [lon, lat]
        })
    
    # Sort by intensity
    locations.sort(key=lambda x: x['intensity'], reverse=True)
    
    # Get top 3 highest and lowest
    highest = locations[:3]
    lowest = locations[-3:][::-1]  # Reverse to show lowest first
    
    return {
        'highest': highest,
        'lowest': lowest,
        'total_locations': len(locations),
        'avg_intensity': sum(l['intensity'] for l in locations) / len(locations),
        'max_intensity': locations[0]['intensity'],
        'min_intensity': locations[-1]['intensity']
    }


def create_visualization_html(results: Dict, output_path: Path):
    """Create a simple HTML visualization of the results."""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Zurich Lighting Intensity Analysis</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }}
        h1 {{ color: #fff; }}
        .section {{
            margin: 30px 0;
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 8px;
        }}
        .location-item {{
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 12px;
            margin: 8px 0;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 6px;
        }}
        .color-box {{
            width: 40px;
            height: 40px;
            border-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .location-info {{
            flex: 1;
        }}
        .location-name {{
            font-weight: 600;
            font-size: 14px;
        }}
        .location-coords {{
            font-size: 11px;
            color: rgba(255, 255, 255, 0.6);
            margin-top: 4px;
        }}
        .intensity-value {{
            font-size: 12px;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <h1>Zurich Lighting Intensity Analysis</h1>
    
    <div class="section">
        <h2>Highest Intensity Locations (Top 10)</h2>
        {"".join([
            f'''
            <div class="location-item">
                <div class="color-box" style="background-color: {loc['color']}"></div>
                <div class="location-info">
                    <div class="location-name">{loc['location']}</div>
                    <div class="location-coords">{loc['lat']:.4f}, {loc['lon']:.4f}</div>
                </div>
                <div class="intensity-value">{loc['intensity']:.4f}</div>
            </div>
            ''' for loc in results['highest']
        ])}
    </div>
    
    <div class="section">
        <h2>Lowest Intensity Locations (Bottom 10)</h2>
        {"".join([
            f'''
            <div class="location-item">
                <div class="color-box" style="background-color: {loc['color']}"></div>
                <div class="location-info">
                    <div class="location-name">{loc['location']}</div>
                    <div class="location-coords">{loc['lat']:.4f}, {loc['lon']:.4f}</div>
                </div>
                <div class="intensity-value">{loc['intensity']:.4f}</div>
            </div>
            ''' for loc in results['lowest']
        ])}
    </div>
    
    <div class="section">
        <h3>Statistics</h3>
        <p>Total locations analyzed: {results['total_locations']}</p>
        <p>Average intensity: {results['avg_intensity']:.4f}</p>
        <p>Maximum intensity: {results['max_intensity']:.4f}</p>
        <p>Minimum intensity: {results['min_intensity']:.4f}</p>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Visualization saved to {output_path}")


def main():
    base_path = Path(__file__).parent
    geojson_path = base_path / 'public' / 'data' / 'hex_light_100m.geojson'
    json_output = base_path / 'public' / 'data' / 'lighting_locations.json'
    html_output = base_path / 'public' / 'data' / 'lighting_locations.html'
    
    if not geojson_path.exists():
        print(f"Error: {geojson_path} not found!")
        return
    
    # Analyze data
    results = analyze_lighting_data(geojson_path)
    
    # Save JSON for app use
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {json_output}")
    
    # Create HTML visualization
    create_visualization_html(results, html_output)
    
    print("\nAnalysis complete!")
    print(f"  - Highest intensity: {results['highest'][0]['location']} ({results['highest'][0]['intensity']:.4f})")
    print(f"  - Lowest intensity: {results['lowest'][0]['location']} ({results['lowest'][0]['intensity']:.4f})")


if __name__ == '__main__':
    main()
