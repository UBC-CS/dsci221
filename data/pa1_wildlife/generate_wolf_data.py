"""
Generate realistic wolf GPS tracking data for PA1.

Based on patterns from real wolf tracking studies:
- Wolves in Alberta/BC typically have home ranges of 150-1000 km²
- GPS collars typically ping every 2-4 hours
- Wolves travel 15-50 km per day
- Pack territories are roughly 250-750 km²

We'll simulate multiple wolf packs with occasional territory overlaps
where "close encounters" might occur.
"""

import csv
import random
import math
from datetime import datetime, timedelta

# Set seed for reproducibility
random.seed(42)

# Alberta/BC wolf territory approximate coordinates
# Centered around ~54°N, -120°W (northern Alberta/BC border region)
BASE_LAT = 54.0
BASE_LON = -120.0

def generate_pack_territory(pack_id, offset_lat, offset_lon, radius_km=15):
    """Generate a pack's home territory center."""
    return {
        'pack_id': pack_id,
        'center_lat': BASE_LAT + offset_lat,
        'center_lon': BASE_LON + offset_lon,
        'radius_km': radius_km
    }

def km_to_degrees(km, at_latitude):
    """Convert km to approximate degrees (rough approximation)."""
    # 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 * cos(latitude) km
    lat_deg = km / 111.0
    lon_deg = km / (111.0 * math.cos(math.radians(at_latitude)))
    return lat_deg, lon_deg

def generate_wolf_path(wolf_id, pack_territory, start_time, num_days=30, pings_per_day=6):
    """Generate a wolf's movement path within its pack territory."""
    points = []

    center_lat = pack_territory['center_lat']
    center_lon = pack_territory['center_lon']
    radius_km = pack_territory['radius_km']

    # Start somewhere in territory
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(0, radius_km * 0.7)
    lat_offset, lon_offset = km_to_degrees(dist, center_lat)

    current_lat = center_lat + lat_offset * math.cos(angle)
    current_lon = center_lon + lon_offset * math.sin(angle)
    current_time = start_time

    # Movement parameters
    avg_speed_km_per_hour = 3  # Wolves average ~3 km/hr when active
    hours_between_pings = 24 / pings_per_day

    for day in range(num_days):
        for ping in range(pings_per_day):
            # Add some randomness to movement
            # Distance traveled since last ping
            distance_km = random.gauss(avg_speed_km_per_hour * hours_between_pings, 2)
            distance_km = max(0.1, min(distance_km, 15))  # Clamp to reasonable values

            # Direction - biased toward territory center if far away
            dist_from_center = math.sqrt(
                ((current_lat - center_lat) * 111) ** 2 +
                ((current_lon - center_lon) * 111 * math.cos(math.radians(center_lat))) ** 2
            )

            if dist_from_center > radius_km * 0.8:
                # Head back toward center
                angle_to_center = math.atan2(
                    center_lon - current_lon,
                    center_lat - current_lat
                )
                direction = angle_to_center + random.gauss(0, 0.5)
            else:
                # Random walk
                direction = random.uniform(0, 2 * math.pi)

            # Move
            lat_delta, lon_delta = km_to_degrees(distance_km, current_lat)
            current_lat += lat_delta * math.cos(direction)
            current_lon += lon_delta * math.sin(direction)

            # Record point
            points.append({
                'wolf_id': wolf_id,
                'pack_id': pack_territory['pack_id'],
                'timestamp': current_time.isoformat(),
                'latitude': round(current_lat, 6),
                'longitude': round(current_lon, 6)
            })

            current_time += timedelta(hours=hours_between_pings)

    return points

def generate_dataset():
    """Generate the full wolf tracking dataset."""

    # Create pack territories - some overlapping for potential encounters
    packs = [
        generate_pack_territory('Yellowhead', 0, 0, radius_km=18),
        generate_pack_territory('Smoky', 0.15, 0.2, radius_km=15),      # Adjacent
        generate_pack_territory('Jasper', -0.1, -0.25, radius_km=20),   # Adjacent
        generate_pack_territory('Willmore', 0.25, -0.1, radius_km=16),  # Slight overlap with Yellowhead
        generate_pack_territory('Kakwa', 0.3, 0.35, radius_km=14),      # Far
    ]

    # Generate wolves for each pack
    wolves_per_pack = {'Yellowhead': 4, 'Smoky': 3, 'Jasper': 5, 'Willmore': 3, 'Kakwa': 4}

    all_points = []
    start_time = datetime(2024, 6, 1, 6, 0, 0)  # Summer tracking season

    wolf_counter = 1
    for pack in packs:
        pack_name = pack['pack_id']
        for i in range(wolves_per_pack[pack_name]):
            wolf_id = f"W{wolf_counter:03d}"
            # Stagger start times slightly
            wolf_start = start_time + timedelta(hours=random.randint(0, 12))
            points = generate_wolf_path(wolf_id, pack, wolf_start, num_days=30, pings_per_day=6)
            all_points.extend(points)
            wolf_counter += 1
            print(f"Generated {len(points)} points for wolf {wolf_id} ({pack_name} pack)")

    return all_points

def write_csv(points, filename):
    """Write points to CSV file."""
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['wolf_id', 'pack_id', 'timestamp', 'latitude', 'longitude'])
        writer.writeheader()
        writer.writerows(points)
    print(f"\nWrote {len(points)} records to {filename}")

if __name__ == '__main__':
    points = generate_dataset()
    write_csv(points, 'wolf_tracking.csv')

    # Also create a smaller test dataset
    small_points = [p for p in points if p['wolf_id'] in ['W001', 'W002', 'W005', 'W006']]
    write_csv(small_points, 'wolf_tracking_small.csv')

    print("\n--- Sample data ---")
    for p in points[:5]:
        print(p)
