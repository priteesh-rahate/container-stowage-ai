
import pytest
from pydantic import ValidationError

from backend.models import (
    Container,
    CargoManifest,
    Vessel,
    VesselDimensions,
)


@pytest.fixture
def vessel():
    return Vessel(
        vessel_id="VESSEL-001",
        name="Synthetic Feeder",
        capacity_teu=2116,
        dimensions=VesselDimensions(
            length_overall_m=172,
            breadth_m=30,
            maximum_draft_m=10.5,
        ),
    )


@pytest.fixture
def container():
    return Container(
        container_id="CONT-001",
        size_ft=20,
        weight_kg=12000,
        loading_port="JNPT",
        discharge_port="Singapore",
        destination_order=3,
    )


def test_vessel_model(vessel):
    assert vessel.vessel_id == "VESSEL-001"
    assert vessel.capacity_teu == 2116


def test_container_model(container):
    assert container.container_id == "CONT-001"
    assert container.size_ft == 20
    assert container.weight_kg == 12000


def test_cargo_manifest(container):
    manifest = CargoManifest(containers=[container])

    assert len(manifest.containers) == 1
    assert manifest.containers[0].container_id == "CONT-001"


def test_duplicate_container_ids_rejected(container):
    with pytest.raises(ValidationError):
        CargoManifest(containers=[container, container])
