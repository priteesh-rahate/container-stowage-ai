
import json

from backend.ai_service import propose_container_placements
from backend.ai_batching import get_ai_batch_proposals
from backend.models import CargoManifest
from backend.slots import VesselSlotPlan


def estimate_rehandles(assignments: list[dict], manifest: CargoManifest,
                       vessel: VesselSlotPlan) -> dict:
    """Estimate containers blocking earlier-discharge cargo in each stack."""

    container_by_id = {
        container.container_id: container
        for container in manifest.containers
    }
    slot_by_id = {
        slot.slot_id: slot
        for slot in vessel.slots
    }

    stacks = {}

    for assignment in assignments:
        slot = slot_by_id[assignment["slot_id"]]
        stack_id = slot.stack_id

        if stack_id is None:
            stack_id = f"{slot.bay:02d}-{slot.row:02d}"

        stacks.setdefault(stack_id, []).append(assignment)

    total_rehandles = 0
    details = []

    for stack_id, stack_assignments in stacks.items():
        stack_assignments.sort(
            key=lambda item: slot_by_id[item["slot_id"]].tier
        )

        for lower_index, lower in enumerate(stack_assignments):
            lower_container = container_by_id[lower["container_id"]]

            for upper in stack_assignments[lower_index + 1:]:
                upper_container = container_by_id[upper["container_id"]]

                if (
                    upper_container.destination_order
                    > lower_container.destination_order
                ):
                    total_rehandles += 1
                    details.append({
                        "stack_id": stack_id,
                        "blocking_container": upper_container.container_id,
                        "blocked_container": lower_container.container_id,
                        "rehandle_at_port_order":
                            lower_container.destination_order,
                    })

    return {
        "estimated_rehandles": total_rehandles,
        "rehandle_details": details,
    }


def create_stowage_plan(
    manifest: CargoManifest,
    vessel: VesselSlotPlan,
    use_ai: bool = True,
) -> dict:
    """Assign containers to compatible slots with footprint reservation."""

    if not vessel.vessel_id:
        raise ValueError("Vessel ID cannot be empty")

    available_slots = sorted(
        vessel.slots,
        key=lambda slot: (slot.bay, slot.row, slot.tier),
    )

    # Each physical bay-row-tier position can be occupied only once.
    occupied_positions = set()
    slots_by_position = {
    (slot.bay, slot.row, slot.tier): slot
    for slot in available_slots
    }
    assignments = []
    unassigned = []
    # Prioritize earlier discharge ports, then heavier containers.
    containers = sorted(
        manifest.containers,
        key=lambda container: (
            container.destination_order,
            -container.weight_kg,
        ),
    )

    ai_proposals = {}

    if use_ai and containers:
        ai_proposals = get_ai_batch_proposals(
            containers,
            available_slots,
            slots_by_position,
            max_batches=4,
        )

    for container in containers:
        chosen_slot = None
        chosen_positions = None

        preferred_slot_id = ai_proposals.get(container.container_id)

        if preferred_slot_id:
            print(
                "AI PREFERRED SLOT:",
                container.container_id,
                "->",
                preferred_slot_id,
            )        

        ordered_slots = sorted(
            available_slots,
            key=lambda slot: (
                slot.slot_id != preferred_slot_id,
                slot.bay,
                slot.row,
                slot.tier,
            ),
        )

        if preferred_slot_id:
            print(
                "AI SLOT CHECK:",
                preferred_slot_id,
                "found:",
                any(s.slot_id == preferred_slot_id for s in available_slots),
            )

        for slot in ordered_slots:

            if (slot.bay, slot.row, slot.tier) in occupied_positions:
                continue

            if container.size_ft not in slot.supported_sizes_ft:
                continue

            if container.weight_kg > slot.max_weight_kg:
                continue

            if container.refrigerated and not slot.reefer_capable:
                continue

            if container.hazardous and not slot.hazardous_allowed:
                continue

            footprint = 2 if container.size_ft == 40 else 1

            # A 40-foot container occupies two consecutive bay coordinates.
            required_positions = [
                (slot.bay + offset, slot.row, slot.tier)
                for offset in range(footprint)
            ]

            # Reject occupied positions.
            if any(
                position in occupied_positions
                for position in required_positions
            ):
                continue


            required_slots = [
                slots_by_position.get(position)
                for position in required_positions
            ]


            if any(required_slot is None for required_slot in required_slots):
                if slot.slot_id == preferred_slot_id:
                    print("AI SLOT REJECTED: missing footprint position")
                continue            
            if any(
                container.size_ft not in required_slot.supported_sizes_ft
                for required_slot in required_slots
            ):
                if slot.slot_id == preferred_slot_id:
                    print("AI SLOT REJECTED: incompatible size")
                continue
            # Every position must support the container weight.
            if any(
                container.weight_kg > required_slot.max_weight_kg
                for required_slot in required_slots
            ):
                continue

            # Check reefer capability across the footprint.
            if container.refrigerated and any(
                not required_slot.reefer_capable
                for required_slot in required_slots
            ):
                continue

            # Check hazardous-cargo permission across the footprint.
            if container.hazardous and any(
                not required_slot.hazardous_allowed
                for required_slot in required_slots
            ):
                continue

            chosen_slot = slot
            chosen_positions = required_positions
            break

        if chosen_slot is None:
            unassigned.append({
                "container_id": container.container_id,
                "reason": "No compatible footprint available",
            })
            continue

        occupied_positions.update(chosen_positions)

        assignments.append({
            "container_id": container.container_id,
            "slot_id": chosen_slot.slot_id,
            "position_code": chosen_slot.position_code,
            "bay": chosen_slot.bay,
            "row": chosen_slot.row,
            "tier": chosen_slot.tier,
            "size_ft": container.size_ft,
            "occupied_positions": [
                f"{bay:02d}-{row:02d}-{tier:02d}"
                for bay, row, tier in chosen_positions
            ],
        })

    rehandling = estimate_rehandles(assignments, manifest, vessel)

    return {
        "vessel_id": vessel.vessel_id,
        "assigned_count": len(assignments),
        "unassigned_count": len(unassigned),
        "assignments": assignments,
        "unassigned": unassigned,
        "estimated_rehandles": rehandling["estimated_rehandles"],
        "rehandle_details": rehandling["rehandle_details"],
        "limitations": [
            "40-foot containers reserve two consecutive bay coordinates.",
            "The synthetic layout does not validate real vessel geometry.",
            "Rehandling is estimated from configured stack relationships.",
            "Port sequencing, stack loads, and vessel stability are not yet enforced.",
        ],
    }
