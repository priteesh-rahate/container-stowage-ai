
import json
from unittest.mock import patch

from backend.models import CargoManifest, Container
from backend.vessel_layout import create_vessel_layout
from backend.placement import create_stowage_plan

manifest = CargoManifest(containers=[
    Container(
        container_id=f"TEST-{i}",
        size_ft=40 if i in (1, 4) else 20,
        weight_kg=12000,
        loading_port="JNPT",
        discharge_port="Singapore",
        destination_order=1,
    )
    for i in range(6)
])

vessel = create_vessel_layout()
calls = []

def fake_qwen(prompt):
    data = json.loads(prompt)
    calls.append(len(data["containers"]))

    # Intentionally propose the same slot for everyone.
    return json.dumps({
        "placements": [
            {"container_ref": i, "slot_ref": 0}
            for i in range(len(data["containers"]))
        ]
    })

with patch(
    "backend.ai_service.propose_container_placements",
    side_effect=fake_qwen
):
    result = create_stowage_plan(
        manifest,
        vessel,
        use_ai=True,
    )

positions = []

for assignment in result["assignments"]:
    positions.extend(assignment["occupied_positions"])

    if assignment["size_ft"] == 40:
        assert len(assignment["occupied_positions"]) == 2

assert calls == [5, 1]
assert result["assigned_count"] == 6
assert result["unassigned_count"] == 0
assert len(positions) == len(set(positions))

print("AI batch sizes:", calls)
print("Assigned:", result["assigned_count"])
print("Unassigned:", result["unassigned_count"])
print("No overlapping positions: PASS")
print("40-foot footprint validation: PASS")
print("MULTI-BATCH SAFETY TEST: PASS")
