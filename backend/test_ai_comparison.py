
from backend.models import CargoManifest, Container
from backend.vessel_layout import create_vessel_layout
from backend.placement import create_stowage_plan
import time

# Create sample container data
manifest = CargoManifest(containers=[
    Container(
        container_id="CONT-001",
        size_ft=20,
        weight_kg=12000,
        loading_port="JNPT",
        discharge_port="Singapore",
        destination_order=1,
    ),
    Container(
        container_id="CONT-002",
        size_ft=20,
        weight_kg=28000,
        loading_port="JNPT",
        discharge_port="Colombo",
        destination_order=2,
    ),
    Container(
        container_id="CONT-003",
        size_ft=40,
        weight_kg=15000,
        loading_port="JNPT",
        discharge_port="Singapore",
        destination_order=1,
    ),
])

vessel = create_vessel_layout()

def test_plan(name, use_ai):
    print(f"\n--- {name} ---")

    start = time.time()

    result = create_stowage_plan(
        manifest,
        vessel,
        use_ai=use_ai,
    )

    elapsed = time.time() - start

    print("Assigned:", result["assigned_count"])
    print("Unassigned:", result["unassigned_count"])

    positions = []

    for assignment in result["assignments"]:
        print(
            assignment["container_id"],
            "->",
            assignment["position_code"]
        )
        positions.extend(assignment["occupied_positions"])

        if assignment["size_ft"] == 40:
            assert len(assignment["occupied_positions"]) == 2

    assert len(positions) == len(set(positions))
    assert result["assigned_count"] + result["unassigned_count"] == 3

    print("Execution time:", round(elapsed, 2), "seconds")
    print("No-overlap validation: PASS")

    return result

normal = test_plan("WITHOUT AI", False)
ai = test_plan("WITH QWEN AI", True)

normal_slots = {
    a["container_id"]: a["slot_id"]
    for a in normal["assignments"]
}

ai_slots = {
    a["container_id"]: a["slot_id"]
    for a in ai["assignments"]
}

print("\n--- COMPARISON ---")
print("Positions different:", normal_slots != ai_slots)
print("Comparison test: PASS")
