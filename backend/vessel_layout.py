
from backend.slots import VesselSlot, VesselSlotPlan


def create_vessel_layout(vessel_id: str = "VESSEL-001") -> VesselSlotPlan:
    """Generate a synthetic vessel layout using bay-row-tier coordinates."""

    slots = []

    # Synthetic layout: 50 bays, 10 rows, 4 tiers per row.
    # Odd-numbered bays represent 20-foot positions.
    # Even-numbered bays represent 40-foot positions.
    bay_numbers = range(1, 51)
    row_numbers = range(0, 10)
    hold_tiers = [2, 4, 6, 8]
    deck_tiers = [82, 84, 86, 88]

    for bay in bay_numbers:
        for row in row_numbers:
            for tier in hold_tiers + deck_tiers:
                location = "hold" if tier < 80 else "deck"


                supported_sizes = [20]
                slot_id = (
                    f"{bay:02d}"
                    f"{row:02d}"
                    f"{tier:02d}"
                )

                slots.append(
                    VesselSlot(
                        slot_id=slot_id,
                        bay=bay,
                        row=row,
                        tier=tier,
                        stack_id=f"{bay:02d}-{row:02d}",
                        location=location,
                        max_weight_kg=30000,
                        supported_sizes_ft=supported_sizes,
                        reefer_capable=True,
                        hazardous_allowed=True,
                    )
                )

    return VesselSlotPlan(vessel_id=vessel_id, slots=slots)
