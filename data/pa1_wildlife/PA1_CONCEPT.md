# PA1: Wildlife Encounters
## Detecting Close Calls in Wolf GPS Tracking Data

### The Story

You're a wildlife biologist studying wolf pack territories in the Alberta-BC border region. Wolf packs are highly territorial - when wolves from different packs encounter each other, conflicts can be deadly.

Using GPS collar data from 19 wolves across 5 packs, your job is to detect **potential encounter events** - moments when wolves from different packs came dangerously close to each other.

With 3,420 GPS readings, checking all pairs naively would require **5.8 million distance calculations**. Your algorithm needs to be smarter.

---

### The Data

**wolf_tracking.csv** - 30 days of GPS data (June 2024)
- 19 wolves across 5 packs (Yellowhead, Smoky, Jasper, Willmore, Kakwa)
- ~180 GPS pings per wolf (every 4 hours)
- Columns: `wolf_id`, `pack_id`, `timestamp`, `latitude`, `longitude`

**wolf_tracking_small.csv** - 4 wolves for testing (720 records)

---

### Part 1: Distance Calculations (10 points)

Implement `haversine_distance(lat1, lon1, lat2, lon2)` to calculate the distance in kilometers between two GPS coordinates.

```python
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth.

    Args:
        lat1, lon1: Coordinates of first point (degrees)
        lat2, lon2: Coordinates of second point (degrees)

    Returns:
        Distance in kilometers
    """
```

This is the foundation - you'll use this in every subsequent part.

---

### Part 2: Brute Force Closest Pair (15 points)

Implement `closest_pair_brute(points)` that finds the two closest points using the naive O(n²) approach.

```python
def closest_pair_brute(points):
    """
    Find the closest pair of points using brute force.

    Args:
        points: List of (x, y) tuples

    Returns:
        ((x1, y1), (x2, y2), distance) - the two closest points and their distance
    """
```

Test it on the small dataset. Time it. Feel the pain.

---

### Part 3: The Divide-and-Conquer Algorithm (30 points)

Now implement the O(n log n) recursive algorithm:

```python
def closest_pair_recursive(points):
    """
    Find the closest pair of points using divide-and-conquer.

    The algorithm:
    1. Base case: if n <= 3, use brute force
    2. Sort points by x-coordinate
    3. Divide into left and right halves
    4. Recursively find closest pair in each half
    5. The tricky part: check the "strip" near the dividing line

    Returns:
        ((x1, y1), (x2, y2), distance)
    """
```

The key insight: after finding the minimum distance `d` in both halves, you only need to check points within distance `d` of the dividing line. And for each point in this strip, you only need to check at most 7 other points (sorted by y-coordinate).

---

### Part 4: Finding Wolf Encounters (20 points)

Now apply your algorithm to the real problem:

```python
def find_inter_pack_encounters(df, distance_threshold_km=2.0):
    """
    Find all instances where wolves from DIFFERENT packs came within
    the threshold distance of each other.

    Args:
        df: DataFrame with wolf tracking data
        distance_threshold_km: Distance that counts as an "encounter"

    Returns:
        List of encounter events: [
            {
                'wolf1': 'W001', 'pack1': 'Yellowhead',
                'wolf2': 'W013', 'pack2': 'Willmore',
                'timestamp1': '2024-06-15T08:00:00',
                'timestamp2': '2024-06-15T12:00:00',
                'distance_km': 1.3,
                'location': (54.12, -119.87)
            },
            ...
        ]
    """
```

The challenge: you need to consider both space AND time. A "close call" means wolves were close in space at approximately the same time.

---

### Part 5: Performance Analysis (15 points)

1. Time your brute-force algorithm on datasets of size 100, 500, 1000, 2000, 3420
2. Time your divide-and-conquer algorithm on the same datasets
3. Plot both on the same graph
4. Fit the theoretical curves O(n²) and O(n log n) to your data
5. Answer: At what size n does divide-and-conquer become 10x faster?

---

### Part 6: Visualization (10 points)

Create a visualization showing:
- Wolf territories (as convex hulls or heat maps)
- Movement paths colored by pack
- Detected encounters highlighted with markers
- A timeline showing when encounters occurred

---

### Why This Matters

This isn't just an academic exercise. Real wildlife biologists use exactly these techniques to:
- Study territorial dynamics
- Predict conflict zones for conservation
- Plan wildlife corridors
- Understand disease transmission between populations

The closest-pair algorithm is also used in:
- Collision detection in physics simulations
- Finding duplicate records in databases
- Cluster analysis in machine learning
- Computer graphics and computational geometry

---

### Grading Rubric

| Part | Points | Focus |
|------|--------|-------|
| 1. Haversine distance | 10 | Correctness |
| 2. Brute force | 15 | Correctness |
| 3. Divide-and-conquer | 30 | Correctness + Recursion |
| 4. Wolf encounters | 20 | Application + Edge cases |
| 5. Performance analysis | 15 | Analysis + Plotting |
| 6. Visualization | 10 | Creativity + Clarity |
| **Total** | **100** | |

---

### Data Source Note

The wolf tracking data is synthetically generated based on realistic movement patterns from published studies of wolf packs in Alberta and British Columbia. Real wolf tracking data is available from [Movebank](https://www.movebank.org), a free database hosted by the Max Planck Institute of Animal Behavior.

---

### Starter Code Location

See `pa1_starter.py` for function signatures and test cases.
