
from backend.models import CargoManifest, Container
from backend.slots import VesselSlot, VesselSlotPlan
from backend.placement import estimate_rehandles

manifest = CargoManifest(
    containers=[
        Container(
            container_id="PORT2",
            size_ft=20,
            weight_kg=10000,
            loading_port="JNPT",
            discharge_port="Colombo",
            destination_order=1,
        ),
        Container(
            container_id="PORT3",
            size_ft=20,
            weight_kg=12000,
            loading_port="JNPT",
            discharge_port="Singapore",
            destination_order=2,
        ),
    ]
)

vessel = VesselSlotPlan(
    vessel_id="TEST-VESSEL",
    slots=[
        VesselSlot(
            slot_id="010102",
            bay=1,
            row=1,
            tier=2,
            location="hold",
            max_weight_kg=30000,
            supported_sizes_ft=[20],
            stack_id="STACK-A",
        ),
        VesselSlot(
            slot_id="010104",
            bay=1,
            row=1,
            tier=4,
            location="hold",
            max_weight_kg=30000,
            supported_sizes_ft=[20],
            stack_id="STACK-A",
        ),

        VesselSlot(
            slot_id="010204",
            bay=1,
            row=2,
            tier=4,
            location="hold",
            max_weight_kg=30000,
            supported_sizes_ft=[20],
            stack_id="STACK-B",
        ),

    ],
)

# Port 3 is above Port 2, so Port 2's container is blocked.
assignments = [
    {
        "container_id": "PORT2",
        "slot_id": "010102",
    },
    {
        "container_id": "PORT3",
        "slot_id": "010104",
    },
]

result = estimate_rehandles(assignments, manifest, vessel)

print(result)

assert result["estimated_rehandles"] == 1
assert len(result["rehandle_details"]) == 1
print("Rehandling test: PASS")


# Containers in separate stacks should not block each other.
separate_stack_assignments = [
    {
        "container_id": "PORT2",
        "slot_id": "010102",
    },
    {
        "container_id": "PORT3",
        "slot_id": "010204",
    },

]

result_separate = estimate_rehandles(
    separate_stack_assignments,
    manifest,
    vessel,
)

assert result_separate["estimated_rehandles"] == 0
assert len(result_separate["rehandle_details"]) == 0
print("Separate-stack rehandling test: PASS")