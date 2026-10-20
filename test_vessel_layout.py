
from backend.vessel_layout import create_vessel_layout

vessel = create_vessel_layout()

print("Vessel ID:", vessel.vessel_id)
print("Total slots:", len(vessel.slots))

print("\nFirst 5 positions:")
for slot in vessel.slots[:5]:
    print(
        slot.slot_id,
        slot.position_code,
        slot.location,
        slot.supported_sizes_ft,
    )

assert len(vessel.slots) == 4000
assert all(slot.row >= 0 for slot in vessel.slots)

print("\nVessel layout test: PASS")

