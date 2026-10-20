
def split_into_batches(containers, batch_size=5):
    """Divide containers into smaller batches."""

    if batch_size <= 0:
        raise ValueError("Batch size must be greater than zero")

    for start in range(0, len(containers), batch_size):
        yield containers[start:start + batch_size]


def get_ai_batch_proposals(
    containers,
    available_slots,
    slots_by_position,
    max_batches=4,
):
    import json
    from backend.ai_service import propose_container_placements

    ai_proposals = {}

    for batch_index, batch in enumerate(
        split_into_batches(containers, 5)
    ):
        if batch_index >= max_batches:
            break

        def is_compatible(container, slot):
            footprint = 2 if container.size_ft == 40 else 1

            for offset in range(footprint):
                position = (
                    slot.bay + offset,
                    slot.row,
                    slot.tier,
                )
                required_slot = slots_by_position.get(position)

                if required_slot is None:
                    return False
                if container.size_ft not in required_slot.supported_sizes_ft:
                    return False
                if container.weight_kg > required_slot.max_weight_kg:
                    return False
                if container.refrigerated and not required_slot.reefer_capable:
                    return False
                if container.hazardous and not required_slot.hazardous_allowed:
                    return False

            return True

        candidates = [
            slot
            for slot in available_slots
            if any(is_compatible(c, slot) for c in batch)
        ][:40]

        if not candidates:
            continue

        prompt_data = {
            "task": "Recommend suitable container slots.",
            "containers": [
                {
                    "container_ref": i,
                    "size_ft": c.size_ft,
                    "weight_kg": c.weight_kg,
                    "destination_order": c.destination_order,
                    "refrigerated": c.refrigerated,
                    "hazardous": c.hazardous,
                }
                for i, c in enumerate(batch)
            ],
            "candidate_slots": [
                {
                    "slot_ref": i,
                    "bay": s.bay,
                    "row": s.row,
                    "tier": s.tier,
                    "supported_sizes_ft": s.supported_sizes_ft,
                    "max_weight_kg": s.max_weight_kg,
                    "reefer_capable": s.reefer_capable,
                    "hazardous_allowed": s.hazardous_allowed,
                }
                for i, s in enumerate(candidates)
            ],
            "instructions": (
                "Return JSON only, formatted as "
                '{"placements":[{"container_ref":0,"slot_ref":0}]}. '
                "Use only provided integer references. "
                "Do not invent containers or slots. "
                "Do not assign one slot to multiple containers. "
                "Do not claim vessel safety is verified."
            ),
        }

        try:
            response = propose_container_placements(
                json.dumps(prompt_data)
            )
            placements = json.loads(response).get("placements", [])

            for item in placements:
                ci = item.get("container_ref")
                si = item.get("slot_ref")

                if (
                    type(ci) is int
                    and type(si) is int
                    and 0 <= ci < len(batch)
                    and 0 <= si < len(candidates)
                ):
                    container_id = batch[ci].container_id
                    slot_id = candidates[si].slot_id
                    ai_proposals.setdefault(container_id, slot_id)

            print(f"AI batch {batch_index + 1}: processed")

        except Exception as error:
            print(f"AI batch {batch_index + 1} failed: {error}")

    return ai_proposals
