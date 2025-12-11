#!/usr/bin/env python3
"""
Calculate median combined_score from all hexagons in Zurich.

This script reads the lumo_score.geojson file and calculates the median
combined_score value across all hexagons. This median is used for coloring
hexagons in the animation (red for below median, green for above median).
"""

import json
from pathlib import Path
import statistics

# Configuration - paths relative to script location
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent
LUMO_SCORE_FILE = DATA_DIR / "lumo_score.geojson"
OUTPUT_FILE = DATA_DIR / "hexagon_median.json"

def load_geojson(filepath):
    """Load a GeoJSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Save data as JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    """Main function to calculate median."""
    print("Loading hexagon data...")
    hexagons = load_geojson(LUMO_SCORE_FILE)
    print(f"Loaded {len(hexagons['features'])} hexagons")
    
    # Extract all combined_score values
    scores = []
    for feature in hexagons['features']:
        score = feature['properties'].get('combined_score', 0)
        # Only include hexagons with score > 0 (filtered in the layer anyway)
        if score > 0:
            scores.append(score)
    
    print(f"Found {len(scores)} hexagons with combined_score > 0")
    
    if len(scores) == 0:
        print("No scores found, cannot calculate median")
        return
    
    # Calculate median
    median_score = statistics.median(scores)
    mean_score = statistics.mean(scores)
    min_score = min(scores)
    max_score = max(scores)
    
    print(f"\nStatistics:")
    print(f"  Median: {median_score:.4f}")
    print(f"  Mean: {mean_score:.4f}")
    print(f"  Min: {min_score:.4f}")
    print(f"  Max: {max_score:.4f}")
    
    # Save median data
    output_data = {
        'median_score': median_score,
        'mean_score': mean_score,
        'min_score': min_score,
        'max_score': max_score,
        'total_hexagons': len(scores),
    }
    
    save_json(output_data, OUTPUT_FILE)
    print(f"\n✓ Median calculated and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
