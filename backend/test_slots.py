
from pydantic import ValidationError

from backend.slots import VesselSlot, VesselSlotPlan


slot = VesselSlot(
    slot_id="010382",
    bay=1,
    row=3,
    tier=82,
    location="deck",
    max_weight_kg=30000,
    reefer_capable=True,
)

plan = VesselSlotPlan(
    vessel_id="VESSEL-001",
    slots=[slot],
)

print("Slot creation: PASS")
print(f"Position code: {slot.position_code}")
print(f"Vessel slots: {len(plan.slots)}")

try:
    VesselSlotPlan(
        vessel_id="VESSEL-001",
        slots=[slot, slot],
    )
except ValidationError:
    print("Duplicate slot validation: PASS")
else:
    raise AssertionError("Duplicate slots were not rejected")
