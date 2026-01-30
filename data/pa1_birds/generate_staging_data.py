"""
Generate synthetic bird staging area data for PA1.

Scenario: Two species (snow geese and sandhill cranes) sharing a wetland
staging area during fall migration. Birds cluster around several roost sites.

The data is designed to:
1. Have enough points (20k+) that O(n²) is noticeably slow
2. Have realistic clustering (birds gather at roost sites)
3. Have two distinct groups for the bichromatic closest pair problem

Clustering Model:
We use a Thomas cluster process, the standard model in spatial ecology for
clustered point patterns. In this model:
- "Parent" points (roost sites) are placed in the area
- "Offspring" (birds) are distributed around each parent using a bivariate
  normal (Gaussian) distribution

This is more ecologically grounded than an exponential distribution. The
Gaussian model implies birds settle at some typical distance from the roost
center, with variation around that distance—which matches how flocking birds
spread out from a central point.

References:
- Thomas, M. (1949). A generalization of Poisson's binomial limit.
- Diggle, P.J. (2013). Statistical Analysis of Spatial and Spatio-Temporal
  Point Patterns, 3rd ed. CRC Press.
"""

import csv
import random
from pathlib import Path

# Reproducibility
random.seed(42)

# Configuration
N_BIRDS_PER_SPECIES = 10000
N_ROOST_SITES = 8  # Shared staging area with multiple roost locations

# Geographic bounds (fictional wetland, ~20km x 20km area)
# Using simple x,y coordinates in km for clarity
AREA_SIZE_KM = 20

# Thomas cluster process parameter: standard deviation of Gaussian spread
# around each roost (in km). This controls how tightly birds cluster.
CLUSTER_SIGMA_KM = 0.5


def generate_roost_sites(n_sites, area_size):
    """Generate random roost site locations."""
    return [(random.uniform(2, area_size-2), random.uniform(2, area_size-2))
            for _ in range(n_sites)]


def generate_birds_around_roosts(n_birds, roosts, species_name, sigma=CLUSTER_SIGMA_KM):
    """
    Generate bird positions clustered around roost sites using a Thomas
    cluster process (bivariate Gaussian distribution around each roost).

    Args:
        n_birds: Number of birds to generate
        roosts: List of (x, y) roost site locations
        species_name: Name of the species
        sigma: Standard deviation of Gaussian spread (km)

    Returns:
        List of bird dictionaries with id, species, x_km, y_km
    """
    birds = []
    for i in range(n_birds):
        # Pick a roost (uniform random - could add popularity weights)
        roost = random.choice(roosts)

        # Thomas cluster process: bivariate normal around roost center
        # random.gauss(mu, sigma) gives N(mu, sigma^2)
        x = random.gauss(roost[0], sigma)
        y = random.gauss(roost[1], sigma)

        birds.append({
            'bird_id': f'{species_name[:2].upper()}{i+1:05d}',
            'species': species_name,
            'x_km': round(x, 6),
            'y_km': round(y, 6)
        })

    return birds


def main():
    output_dir = Path(__file__).parent

    # Generate shared roost sites (both species use the same staging area)
    roosts = generate_roost_sites(N_ROOST_SITES, AREA_SIZE_KM)

    print(f"Generated {N_ROOST_SITES} roost sites:")
    for i, (x, y) in enumerate(roosts):
        print(f"  Roost {i+1}: ({x:.2f}, {y:.2f}) km")

    # Generate birds for each species
    snow_geese = generate_birds_around_roosts(
        N_BIRDS_PER_SPECIES, roosts, 'snow_goose'
    )
    sandhill_cranes = generate_birds_around_roosts(
        N_BIRDS_PER_SPECIES, roosts, 'sandhill_crane'
    )

    all_birds = snow_geese + sandhill_cranes
    random.shuffle(all_birds)  # Mix them up

    # Write full dataset
    full_path = output_dir / 'bird_staging.csv'
    with open(full_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['bird_id', 'species', 'x_km', 'y_km'])
        writer.writeheader()
        writer.writerows(all_birds)

    print(f"\nGenerated {len(all_birds)} birds -> {full_path}")

    # Write small dataset for testing (500 per species)
    # Use same roosts for consistency
    small_birds = (
        generate_birds_around_roosts(500, roosts, 'snow_goose') +
        generate_birds_around_roosts(500, roosts, 'sandhill_crane')
    )
    random.shuffle(small_birds)

    small_path = output_dir / 'bird_staging_small.csv'
    with open(small_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['bird_id', 'species', 'x_km', 'y_km'])
        writer.writeheader()
        writer.writerows(small_birds)

    print(f"Generated {len(small_birds)} birds -> {small_path}")

    # Print stats
    print(f"\nDataset stats:")
    print(f"  Area: {AREA_SIZE_KM}km x {AREA_SIZE_KM}km")
    print(f"  Roost sites: {N_ROOST_SITES}")
    print(f"  Cluster sigma: {CLUSTER_SIGMA_KM} km")
    print(f"  Snow geese: {N_BIRDS_PER_SPECIES}")
    print(f"  Sandhill cranes: {N_BIRDS_PER_SPECIES}")

    # Compute x/y ranges
    xs = [b['x_km'] for b in all_birds]
    ys = [b['y_km'] for b in all_birds]
    print(f"  X range: {min(xs):.2f} to {max(xs):.2f} km")
    print(f"  Y range: {min(ys):.2f} to {max(ys):.2f} km")

    print(f"\nModel: Thomas cluster process (bivariate Gaussian)")
    print(f"  - Standard ecological model for clustered point patterns")
    print(f"  - Each bird's position: N(roost_center, sigma={CLUSTER_SIGMA_KM}km)")


if __name__ == '__main__':
    main()
