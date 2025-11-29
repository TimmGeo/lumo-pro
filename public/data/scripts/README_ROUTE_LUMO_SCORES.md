# Route Lumo Score Calculator

This Python script calculates the "Lumo Score" percentage for each route, representing what percentage of the route passes through "bright" areas (areas with high light + vibrancy scores).

## What it does

For each route file in `../routes/`, the script:
1. Samples points along the route at regular intervals (every 50 meters)
2. For each point, finds which hexagon from `../lumo_score.geojson` it intersects
3. Calculates the brightness as `light_score + vibrancy_score`
4. Determines what percentage of the route passes through "bright" areas (where brightness >= threshold)
5. Adds the `lumo_score_percentage` property to each route's GeoJSON file

## Installation

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the script from the scripts directory:

```bash
cd public/data/scripts
python calculate_route_lumo_scores.py
```

Or from the project root:

```bash
python public/data/scripts/calculate_route_lumo_scores.py
```

The script will:
- Load hexagon data from `../lumo_score.geojson`
- Process all `.geojson` files in `../routes/`
- Add `lumo_score_percentage` property to each route
- Print a summary of results

## Configuration

You can adjust the following parameters in the script:

- `BRIGHT_THRESHOLD`: Threshold for considering an area "bright" (default: 0.5)
  - An area is considered bright if `light_score + vibrancy_score >= BRIGHT_THRESHOLD`
  
- `sample_distance`: Distance in meters between sample points along routes (default: 50)
  - Smaller values = more accurate but slower
  - Larger values = faster but less accurate

## Output

Each route file will be updated with a new property:
```json
{
  "properties": {
    "lumo_score_percentage": 42.5,
    ...
  }
}
```

The percentage represents what portion of the route (0-100%) passes through bright areas.

## Example Output

```
============================================================
Route Lumo Score Calculator
============================================================

Loading hexagon data from ../lumo_score.geojson...
Loaded 10459 hexagons
Creating spatial index...
Index created with 10459 hexagons

Found 28 route files to process

Processing routes...
------------------------------------------------------------
Processing 2_3.geojson...
  Route 2_3: 42.5% bright
Processing 2_4.geojson...
  Route 2_4: 38.2% bright
...

============================================================
Summary
============================================================
  2_3: 42.5% bright
  2_4: 38.2% bright
  ...

✓ Processed 28 routes successfully!
  Bright threshold: 0.5 (light_score + vibrancy_score)
```

