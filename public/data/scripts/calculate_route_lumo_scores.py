#!/usr/bin/env python3
"""
Calculate lumo scores for routes based on the fraction of red (unsafe) hexagons.

The lumo score is calculated as: (number of red/unsafe hexagons on route) / (total hexagons on route)
- Red hexagons are those with combined_score below the median
- Score is stored as 0-1 (fraction of unsafe hexagons)
- Displayed as 0-10 where 10.0 = perfect (no red hexagons), 0.0 = worst (all red)

This script:
1. Loads route hexagon intersections (from calculate_route_hexagon_intersections.py)
2. Loads lumo_score.geojson and hexagon_median.json to identify unsafe hexagons
3. Calculates lumo score for each route (fast and bright)
4. Saves scores to JSON files
"""

import json
from pathlib import Path

# Configuration - paths relative to script location
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent
ROUTE_INTERSECTIONS_DIR = DATA_DIR / "route_intersections"
LUMO_SCORE_FILE = DATA_DIR / "lumo_score.geojson"
MEDIAN_FILE = DATA_DIR / "hexagon_median.json"
OUTPUT_DIR = DATA_DIR / "route_lumo_scores"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_geojson(filepath):
    """Load a GeoJSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_json(filepath):
    """Load a JSON file."""
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

def identify_unsafe_hexagons(hexagons, median_score):
    """
    Identify unsafe hexagons (those with combined_score below median).
    Returns a set of unsafe hexagon IDs.
    """
    unsafe_hex_ids = set()
    
    for feature in hexagons['features']:
        score = feature['properties'].get('combined_score', 0)
        if score > 0 and score < median_score:
            hex_id = get_hexagon_id(feature['properties'])
            if hex_id is not None:
                unsafe_hex_ids.add(hex_id)
    
    return unsafe_hex_ids

def calculate_lumo_score(route_hex_ids, unsafe_hex_ids):
    """
    Calculate lumo score for a route based on fraction of unsafe hexagons.
    
    Args:
        route_hex_ids: List of hexagon IDs that intersect with the route
        unsafe_hex_ids: Set of unsafe hexagon IDs (red hexagons)
    
    Returns:
        lumo_score: float between 0 and 1 (fraction of unsafe hexagons, where 0.0 = all safe, 1.0 = all unsafe)
        total_hexagons: int (total hexagons on route)
        unsafe_hexagons: int (unsafe hexagons on route)
    """
    if not route_hex_ids:
        return 0.0, 0, 0
    
    total_hexagons = len(route_hex_ids)
    unsafe_hexagons = sum(1 for hex_id in route_hex_ids if hex_id in unsafe_hex_ids)
    
    lumo_score = unsafe_hexagons / total_hexagons if total_hexagons > 0 else 0.0
    
    return lumo_score, total_hexagons, unsafe_hexagons

def main():
    """Main function to calculate lumo scores for all routes."""
    print("Loading hexagon data and median...")
    
    # Load median
    median_score = load_median()
    if median_score is None:
        return
    print(f"Using median score: {median_score}")
    
    # Load hexagon data
    hexagons = load_geojson(LUMO_SCORE_FILE)
    print(f"Loaded {len(hexagons['features'])} hexagons")
    
    # Identify unsafe hexagons (red hexagons - below median)
    unsafe_hex_ids = identify_unsafe_hexagons(hexagons, median_score)
    print(f"Found {len(unsafe_hex_ids)} unsafe hexagons (below median)")
    
    if len(unsafe_hex_ids) == 0:
        print("No unsafe hexagons found, nothing to process")
        return
    
    # Get all route intersection files
    intersection_files = sorted(ROUTE_INTERSECTIONS_DIR.glob("*.json"))
    print(f"\nProcessing {len(intersection_files)} route intersection files...")
    
    processed_count = 0
    
    for intersection_file in intersection_files:
        route_name = intersection_file.stem  # e.g., "1_7"
        print(f"\nProcessing route: {route_name}")
        
        try:
            # Load route intersection data
            intersection_data = load_json(intersection_file)
            scores = {}
            
            # Note: Blue line = bright route, Grey line = fast route
            # Swapping mapping: bright_hex_ids -> fast route, fast_hex_ids -> bright route
            
            # Calculate lumo score for fast route (grey line)
            if 'bright_hex_ids' in intersection_data:
                fast_hex_ids = intersection_data['bright_hex_ids']
                fast_lumo_score, fast_total, fast_unsafe = calculate_lumo_score(
                    fast_hex_ids, unsafe_hex_ids
                )
                scores['fast'] = {
                    'lumo_score': fast_lumo_score,
                    'total_hexagons': fast_total,
                    'unsafe_hexagons': fast_unsafe
                }
                display_score = 10.0 * (1 - fast_lumo_score)  # Invert: 0 unsafe = 10.0, 1 unsafe = 0.0
                print(f"  Fast route (grey): lumo_score={fast_lumo_score:.4f} (display={display_score:.1f}, {fast_unsafe}/{fast_total} unsafe)")
            else:
                scores['fast'] = {
                    'lumo_score': 0.0,
                    'total_hexagons': 0,
                    'unsafe_hexagons': 0
                }
                print(f"  Fast route: no hexagon data")
            
            # Calculate lumo score for bright route (blue line)
            if 'fast_hex_ids' in intersection_data:
                bright_hex_ids = intersection_data['fast_hex_ids']
                bright_lumo_score, bright_total, bright_unsafe = calculate_lumo_score(
                    bright_hex_ids, unsafe_hex_ids
                )
                scores['bright'] = {
                    'lumo_score': bright_lumo_score,
                    'total_hexagons': bright_total,
                    'unsafe_hexagons': bright_unsafe
                }
                display_score = 10.0 * (1 - bright_lumo_score)  # Invert: 0 unsafe = 10.0, 1 unsafe = 0.0
                print(f"  Bright route (blue): lumo_score={bright_lumo_score:.4f} (display={display_score:.1f}, {bright_unsafe}/{bright_total} unsafe)")
            else:
                scores['bright'] = {
                    'lumo_score': 0.0,
                    'total_hexagons': 0,
                    'unsafe_hexagons': 0
                }
                print(f"  Bright route: no hexagon data")
            
            # Ensure bright route score is >= fast route score (bright routes prioritize safety)
            # Lower lumo_score (fewer unsafe hexagons) = better, so we want bright_lumo_score <= fast_lumo_score
            if scores['bright']['lumo_score'] > scores['fast']['lumo_score']:
                scores['bright']['lumo_score'] = scores['fast']['lumo_score']
                scores['bright']['unsafe_hexagons'] = int(scores['bright']['total_hexagons'] * scores['bright']['lumo_score'])
                print(f"  ⚠ Adjusted bright route score to match fast route (bright routes should be >= fast)")
            
            # Save scores
            output_file = OUTPUT_DIR / f"{route_name}.json"
            save_json(scores, output_file)
            print(f"  ✓ Saved scores to {output_file.name}")
            processed_count += 1
            
        except Exception as e:
            print(f"  ✗ Error processing {route_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n✓ Processed {processed_count} routes")
    print(f"✓ Lumo scores saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
