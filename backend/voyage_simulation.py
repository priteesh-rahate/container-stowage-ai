
from backend.models import CargoManifest
from backend.slots import VesselSlotPlan


def simulate_voyage(
    manifest: CargoManifest,
    vessel: VesselSlotPlan,
    port_sequence: list[str],
) -> dict:
    """
    Simulate cargo movements across a sequence of port calls.

    This is a simplified operational simulation, not a vessel-safety
    or stability validation.
    """
    if len(port_sequence) < 2:
        raise ValueError("A voyage must contain at least two port calls.")

    if len(port_sequence) != len(set(port_sequence)):
        raise ValueError("Port sequence must not contain duplicate ports.")

    ports = [port.strip() for port in port_sequence]
    if any(not port for port in ports):
        raise ValueError("Port names cannot be empty.")

    port_index = {port: i for i, port in enumerate(ports)}

    for container in manifest.containers:
        if container.loading_port not in port_index:
            raise ValueError(
                f"Loading port '{container.loading_port}' for container "
                f"'{container.container_id}' is not in the voyage."
            )
        if container.discharge_port not in port_index:
            raise ValueError(
                f"Discharge port '{container.discharge_port}' for container "
                f"'{container.container_id}' is not in the voyage."
            )
        if port_index[container.loading_port] >= port_index[container.discharge_port]:
            raise ValueError(
                f"Container '{container.container_id}' must be loaded before "
                "its discharge port in the voyage sequence."
            )

    events = []
    onboard = set()
    remaining_to_load = {
        container.container_id: container
        for container in manifest.containers
    }
    containers_by_id = {
        container.container_id: container
        for container in manifest.containers
    }

    for port in ports:
        discharged = []
        loaded = []

        for container_id in list(onboard):
            container = containers_by_id[container_id]
            if container.discharge_port == port:
                onboard.remove(container_id)
                discharged.append(container_id)

        for container_id, container in list(remaining_to_load.items()):
            if container.loading_port == port:
                onboard.add(container_id)
                loaded.append(container_id)
                del remaining_to_load[container_id]

        events.append({
            "port": port,
            "loaded": sorted(loaded),
            "discharged": sorted(discharged),
            "onboard_after_port_call": len(onboard),
        })

    return {
        "port_sequence": ports,
        "total_containers": len(manifest.containers),
        "vessel_slot_count": len(vessel.slots),
        "events": events,
        "remaining_onboard_after_final_port": sorted(onboard),
        "limitations": [
            "This simulates cargo movements only; it does not re-optimize stowage at each port.",
            "It does not validate vessel stability, stack loads, or dangerous-goods segregation.",
        ],
    }
