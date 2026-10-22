
import json

import time
from pathlib import Path

import pandas as pd

from backend.models import CargoManifest, Container
from backend.vessel_layout import create_vessel_layout
from backend.placement import create_stowage_plan


# Find the CSV in the project root.
project_root = Path(__file__).resolve().parent.parent
csv_path = project_root / "sample_manifest_2000.csv"

df = pd.read_csv(csv_path)

containers = [
    Container(**record)
    for record in df.to_dict(orient="records")
]

manifest = CargoManifest(containers=containers)

# Generate the synthetic 4,000-slot vessel.
vessel = create_vessel_layout()

print("Containers loaded:", len(manifest.containers))
print("Vessel slots:", len(vessel.slots))
print("Starting Qwen AI batching test...")

start = time.perf_counter()

result = create_stowage_plan(
    manifest,
    vessel,
    use_ai=True,
)

elapsed = time.perf_counter() - start

print("\n========== TEST RESULTS ==========")
print("Total containers:", len(containers))
print("Assigned:", result["assigned_count"])
print("Unassigned:", result["unassigned_count"])
print("Elapsed seconds:", round(elapsed, 2))

print("\nFinal placements:")
for assignment in result["assignments"]:
    print(
        assignment["container_id"],
        "->",
        assignment["slot_id"],
    )
print("==================================")

output_path = project_root / "ai_placements_2000.json"

print("AI proposals:", result["ai_proposed_count"])
print("AI preferred slots accepted:", result["ai_accepted_count"])
print("AI fallback slots used:", result["ai_fallback_count"])

print(
    "AI preferred slots already occupied:",
    result["ai_preferred_occupied_count"],
)

with output_path.open("w", encoding="utf-8") as file:
    json.dump(result["assignments"], file, indent=2)

print("Saved placements to:", output_path)