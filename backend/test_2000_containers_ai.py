
import time
import pandas as pd

from backend.models import CargoManifest, Container
from backend.vessel_layout import create_vessel_layout
from backend.placement import create_stowage_plan

# Load the 2,000-container dataset
df = pd.read_csv("sample_manifest_2000.csv")

manifest = CargoManifest(
    containers=[
        Container(**row)
        for row in df.to_dict(orient="records")
    ]
)

vessel = create_vessel_layout()

print("Total containers:", len(manifest.containers))
print("Available vessel slots:", len(vessel.slots))

# Test Python placement without AI
start = time.perf_counter()

result = create_stowage_plan(
    manifest,
    vessel,
    use_ai=True
)

elapsed = time.perf_counter() - start

# Validate occupied positions
positions = [
    position
    for assignment in result["assignments"]
    for position in assignment["occupied_positions"]
]

assert (
    result["assigned_count"] + result["unassigned_count"]
    == len(manifest.containers)
)

assert len(positions) == len(set(positions)), (
    "Overlapping positions detected!"
)

for assignment in result["assignments"]:
    expected = 2 if assignment["size_ft"] == 40 else 1
    assert len(assignment["occupied_positions"]) == expected

print("\n--- RESULTS ---")
print("Assigned:", result["assigned_count"])
print("Unassigned:", result["unassigned_count"])
print("Estimated rehandles:", result["estimated_rehandles"])
print("Execution time:", round(elapsed, 2), "seconds")
print("No overlapping positions: PASS")
print("Container footprint test: PASS")
print("2000-CONTAINER AI TEST: PASS")