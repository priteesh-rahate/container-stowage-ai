
from backend.models import CargoManifest, Container
from backend.slots import VesselSlot, VesselSlotPlan
from backend.placement import create_stowage_plan

manifest = CargoManifest(
    containers=[
        Container(
            container_id="FORTY-001",
            size_ft=40,
            weight_kg=15000,
            loading_port="JNPT",
            discharge_port="Singapore",
            destination_order=1,
        )
    ]
)

# Only bay 3 exists; the required adjacent bay 4 is missing.
vessel = VesselSlotPlan(
    vessel_id="TEST-VESSEL",
    slots=[
        VesselSlot(
            slot_id="030102",
            bay=3,
            row=1,
            tier=2,
            location="hold",
            max_weight_kg=30000,
            supported_sizes_ft=[20, 40],
        )
    ],
)

result = create_stowage_plan(manifest, vessel)

print("Assigned:", result["assigned_count"])
print("Unassigned:", result["unassigned_count"])
print("Details:", result["unassigned"])

assert result["assigned_count"] == 0, (
    "A 40-foot container was assigned despite its second bay being missing."
)
assert result["unassigned_count"] == 1

print("Missing-bay validation test: PASS")


# Test an existing adjacent bay that supports only 20-foot containers.
incompatible_vessel = VesselSlotPlan(
    vessel_id="TEST-VESSEL-2",
    slots=[
        VesselSlot(
            slot_id="030102",
            bay=3,
            row=1,
            tier=2,
            location="hold",
            max_weight_kg=30000,
            supported_sizes_ft=[20, 40],
        ),
        VesselSlot(
            slot_id="040102",
            bay=4,
            row=1,
            tier=2,
            location="hold",
            max_weight_kg=30000,
            supported_sizes_ft=[],
        ),
    ],
)

incompatible_result = create_stowage_plan(
    manifest,
    incompatible_vessel,
)

print("Incompatible-bay result:", incompatible_result["unassigned"])

assert incompatible_result["assigned_count"] == 0, (
    "A 40-foot container was assigned despite an incompatible adjacent bay."
)
assert incompatible_result["unassigned_count"] == 1

print("Incompatible-bay validation test: PASS")
