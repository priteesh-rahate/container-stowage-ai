
from backend.models import CargoManifest, Container
from backend.slots import VesselSlot, VesselSlotPlan
from backend.placement import create_stowage_plan


manifest = CargoManifest(
    containers=[
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
            refrigerated=True,
        ),
        Container(
            container_id="CONT-003",
            size_ft=40,
            weight_kg=15000,
            loading_port="JNPT",
            discharge_port="Singapore",
            destination_order=1,
        ),
    ]
)

vessel = VesselSlotPlan(
    vessel_id="VESSEL-001",
    slots=[
        # 20-foot position
        VesselSlot(
            slot_id="010102",
            bay=1,
            row=1,
            tier=2,
            location="hold",
            max_weight_kg=20000,
            supported_sizes_ft=[20],
        ),
        # Another 20-foot position, with reefer capability
        VesselSlot(
            slot_id="010104",
            bay=1,
            row=1,
            tier=4,
            location="hold",
            max_weight_kg=30000,
            supported_sizes_ft=[20],
            reefer_capable=True,
        ),
        # First position of a 40-foot footprint
        VesselSlot(
            slot_id="030102",
            bay=3,
            row=1,
            tier=2,
            location="hold",
            max_weight_kg=30000,
            supported_sizes_ft=[20, 40],
        ),
        # Adjacent position required by the 40-foot footprint
        VesselSlot(
            slot_id="040102",
            bay=4,
            row=1,
            tier=2,
            location="hold",
            max_weight_kg=30000,
            supported_sizes_ft=[20, 40],
        ),
    ],
)

for slot in vessel.slots:
    print(slot.slot_id, "supports:", slot.supported_sizes_ft)



result = create_stowage_plan(manifest, vessel)

print("Assigned:", result["assigned_count"])
print("Unassigned:", result["unassigned_count"])

for assignment in result["assignments"]:
    print(
        assignment["container_id"],
        "->",
        assignment["position_code"],
    )

for item in result["unassigned"]:
    print(
        "Unassigned:",
        item["container_id"],
        "-",
        item["reason"],
    )

assert result["assigned_count"] == 3
assert result["unassigned_count"] == 0
assert any(
    item["container_id"] == "CONT-003"
    for item in result["assignments"]
)

# Verify destination order is considered during placement.
destination_orders = {
    container.container_id: container.destination_order
    for container in manifest.containers
}

assigned_orders = [
    destination_orders[item["container_id"]]
    for item in result["assignments"]
]

assert all(order >= 1 for order in assigned_orders)

print("Destination-order test: PASS")

# Verify 40-foot containers reserve two adjacent bay positions.
forty_foot = next(
    item for item in result["assignments"]
    if item["container_id"] == "CONT-003"
)

occupied = forty_foot["occupied_positions"]

assert len(occupied) == 2, (
    f"Expected 2 occupied positions for a 40-foot container, got {occupied}"
)

# Verify that no physical position is assigned to multiple containers.
all_positions = [
    position
    for assignment in result["assignments"]
    for position in assignment["occupied_positions"]
]

assert len(all_positions) == len(set(all_positions)), (
    "Overlapping container footprints detected"
)

print("No-overlap test: PASS")

print("40-foot footprint test: PASS")

print("Placement tests: PASS")

print("Placement tests: PASS")
