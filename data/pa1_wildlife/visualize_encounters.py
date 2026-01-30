"""
DSCI 221 - PA1 Wildlife Encounters Visualizer
==============================================

This script visualizes your wolf tracking analysis!

Instructions:
1. Complete your functions in the PA1 assignment
2. Run this script: python visualize_encounters.py
3. See your wolves come to life!

The script will:
- Plot wolf movement paths colored by pack
- Show territory boundaries
- Highlight detected inter-pack encounters
- Display a timeline of encounters
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
import numpy as np
import pandas as pd
from datetime import datetime

# =============================================================================
# PASTE YOUR FUNCTIONS HERE (or import them)
# =============================================================================

def haversine_distance(lat1, lon1, lat2, lon2):
    """YOUR IMPLEMENTATION - distance in km between two GPS coordinates."""
    import math
    R = 6371  # Earth's radius in km

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def find_inter_pack_encounters(df, distance_threshold_km=2.0, time_threshold_hours=4):
    """
    YOUR IMPLEMENTATION - find encounters between wolves of different packs.

    This is a placeholder that returns sample encounters.
    Replace with your actual implementation!
    """
    # Placeholder - returns empty list
    # Your implementation should return list of encounter dicts
    return []


# =============================================================================
# VISUALIZATION CODE (provided - don't modify)
# =============================================================================

# Pack colors - colorblind-friendly palette
PACK_COLORS = {
    'Yellowhead': '#E69F00',  # Orange
    'Smoky': '#56B4E9',       # Sky blue
    'Jasper': '#009E73',      # Teal
    'Willmore': '#F0E442',    # Yellow
    'Kakwa': '#CC79A7',       # Pink
}

def load_wolf_data(filename='wolf_tracking.csv'):
    """Load wolf tracking data."""
    df = pd.read_csv(filename)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def plot_wolf_paths(df, ax, alpha=0.6, linewidth=0.8):
    """Plot movement paths for all wolves, colored by pack."""
    for wolf_id in df['wolf_id'].unique():
        wolf_data = df[df['wolf_id'] == wolf_id].sort_values('timestamp')
        pack = wolf_data['pack_id'].iloc[0]
        color = PACK_COLORS.get(pack, 'gray')

        ax.plot(wolf_data['longitude'], wolf_data['latitude'],
                color=color, alpha=alpha, linewidth=linewidth,
                label=pack if wolf_id == df[df['pack_id'] == pack]['wolf_id'].iloc[0] else '')

def plot_territory_hulls(df, ax, alpha=0.15):
    """Plot convex hulls around each pack's territory."""
    from scipy.spatial import ConvexHull

    for pack in df['pack_id'].unique():
        pack_data = df[df['pack_id'] == pack]
        points = pack_data[['longitude', 'latitude']].values

        if len(points) >= 3:
            try:
                hull = ConvexHull(points)
                hull_points = points[hull.vertices]
                hull_points = np.vstack([hull_points, hull_points[0]])  # Close the polygon

                color = PACK_COLORS.get(pack, 'gray')
                ax.fill(hull_points[:, 0], hull_points[:, 1],
                       color=color, alpha=alpha, edgecolor=color, linewidth=2)
            except:
                pass  # Skip if hull fails

def plot_encounters(encounters, ax, marker_size=100):
    """Plot encounter points with special markers."""
    if not encounters:
        return

    for enc in encounters:
        ax.scatter(enc['location'][1], enc['location'][0],
                  s=marker_size, c='red', marker='*', zorder=10,
                  edgecolors='darkred', linewidths=1)

def create_main_visualization(df, encounters, title="Wolf Pack Territories & Encounters"):
    """Create the main map visualization."""
    fig, ax = plt.subplots(figsize=(14, 10))

    # Plot territories first (background)
    plot_territory_hulls(df, ax)

    # Plot movement paths
    plot_wolf_paths(df, ax)

    # Plot encounters
    plot_encounters(encounters, ax)

    # Create legend
    legend_patches = [mpatches.Patch(color=color, label=pack)
                     for pack, color in PACK_COLORS.items()]
    if encounters:
        legend_patches.append(plt.scatter([], [], s=100, c='red', marker='*',
                                          label=f'Encounters ({len(encounters)})'))

    ax.legend(handles=legend_patches, loc='upper left', fontsize=10)

    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig, ax

def create_encounter_timeline(encounters, df):
    """Create a timeline showing when encounters occurred."""
    if not encounters:
        print("No encounters to plot in timeline.")
        return None, None

    fig, ax = plt.subplots(figsize=(14, 4))

    # Get date range from data
    min_date = df['timestamp'].min()
    max_date = df['timestamp'].max()

    # Plot encounters on timeline
    for i, enc in enumerate(encounters):
        t1 = pd.to_datetime(enc['timestamp1'])
        packs = f"{enc['pack1']}-{enc['pack2']}"

        ax.scatter(t1, i, s=100, c='red', marker='o', zorder=10)
        ax.annotate(f"{enc['wolf1']} & {enc['wolf2']}\n({enc['distance_km']:.1f} km)",
                   (t1, i), xytext=(10, 0), textcoords='offset points',
                   fontsize=8, va='center')

    ax.set_xlim(min_date, max_date)
    ax.set_ylim(-1, len(encounters))
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Encounter #', fontsize=12)
    ax.set_title('Timeline of Inter-Pack Encounters', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    return fig, ax

def create_distance_histogram(df, encounters):
    """Show distribution of inter-pack distances."""
    fig, ax = plt.subplots(figsize=(10, 5))

    # This would require computing many distances - simplified version
    if encounters:
        distances = [enc['distance_km'] for enc in encounters]
        ax.hist(distances, bins=20, color='#E69F00', edgecolor='black', alpha=0.7)
        ax.axvline(x=2.0, color='red', linestyle='--', linewidth=2, label='Threshold (2 km)')
        ax.set_xlabel('Distance (km)', fontsize=12)
        ax.set_ylabel('Number of Encounters', fontsize=12)
        ax.set_title('Distribution of Encounter Distances', fontsize=14, fontweight='bold')
        ax.legend()
    else:
        ax.text(0.5, 0.5, 'No encounters detected.\n\nMake sure your find_inter_pack_encounters()\nfunction is implemented!',
               ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.set_title('Encounter Distance Distribution', fontsize=14, fontweight='bold')

    plt.tight_layout()
    return fig, ax

def print_encounter_summary(encounters):
    """Print a summary of detected encounters."""
    print("\n" + "="*60)
    print("ENCOUNTER SUMMARY")
    print("="*60)

    if not encounters:
        print("\nNo inter-pack encounters detected!")
        print("Check your find_inter_pack_encounters() implementation.")
        return

    print(f"\nTotal encounters detected: {len(encounters)}")
    print("-"*60)

    # Group by pack pairs
    pack_pairs = {}
    for enc in encounters:
        pair = tuple(sorted([enc['pack1'], enc['pack2']]))
        if pair not in pack_pairs:
            pack_pairs[pair] = []
        pack_pairs[pair].append(enc)

    for pair, encs in sorted(pack_pairs.items()):
        print(f"\n{pair[0]} <-> {pair[1]}: {len(encs)} encounter(s)")
        for enc in encs[:3]:  # Show first 3
            print(f"  - {enc['wolf1']} & {enc['wolf2']}: {enc['distance_km']:.2f} km")
        if len(encs) > 3:
            print(f"  ... and {len(encs)-3} more")

def main():
    """Run the full visualization."""
    print("="*60)
    print("DSCI 221 - PA1 Wildlife Encounters Visualizer")
    print("="*60)

    # Load data
    print("\nLoading wolf tracking data...")
    try:
        df = load_wolf_data('wolf_tracking.csv')
        print(f"  Loaded {len(df)} GPS points for {df['wolf_id'].nunique()} wolves")
        print(f"  Packs: {', '.join(df['pack_id'].unique())}")
        print(f"  Date range: {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
    except FileNotFoundError:
        print("ERROR: wolf_tracking.csv not found!")
        print("Make sure you're running this script in the PA1 data directory.")
        return

    # Find encounters using student's function
    print("\nDetecting inter-pack encounters...")
    encounters = find_inter_pack_encounters(df, distance_threshold_km=2.0)
    print_encounter_summary(encounters)

    # Create visualizations
    print("\nGenerating visualizations...")

    # Main map
    fig1, ax1 = create_main_visualization(df, encounters)

    # Timeline (if encounters exist)
    if encounters:
        fig2, ax2 = create_encounter_timeline(encounters, df)

    # Distance histogram
    fig3, ax3 = create_distance_histogram(df, encounters)

    print("\nDisplaying plots... (close windows to exit)")
    plt.show()

if __name__ == '__main__':
    main()
