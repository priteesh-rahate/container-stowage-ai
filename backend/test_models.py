
from pydantic import ValidationError

from backend.models import Container, CargoManifest, Vessel, VesselDimensions


vessel = Vessel(
    vessel_id="VESSEL-001",
    name="Synthetic Feeder",
    capacity_teu=2116,
    dimensions=VesselDimensions(
        length_overall_m=172,
        breadth_m=30,
        maximum_draft_m=10.5,
    ),
)

container = Container(
    container_id="CONT-001",
    size_ft=20,
    weight_kg=12000,
    loading_port="JNPT",
    discharge_port="Singapore",
    destination_order=3,
)

manifest = CargoManifest(containers=[container])

print("Vessel model: PASS")
print("Container model: PASS")
print("Cargo manifest: PASS")
print(f"Vessel capacity: {vessel.capacity_teu} TEU")
print(f"Containers in manifest: {len(manifest.containers)}")

try:
    CargoManifest(containers=[container, container])
except ValidationError:
    print("Duplicate container validation: PASS")
else:
    raise AssertionError("Duplicate container IDs were not rejected")

