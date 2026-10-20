
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class VesselDimensions(BaseModel):
    length_overall_m: float = Field(gt=0)
    breadth_m: float = Field(gt=0)
    maximum_draft_m: float = Field(gt=0)


class Vessel(BaseModel):
    vessel_id: str
    name: str
    capacity_teu: int = Field(gt=0)
    dimensions: VesselDimensions


class Container(BaseModel):
    container_id: str
    size_ft: Literal[20, 40]
    weight_kg: float = Field(gt=0)
    loading_port: str
    discharge_port: str
    destination_order: int = Field(ge=1)
    refrigerated: bool = False
    hazardous: bool = False

    @model_validator(mode="after")
    def validate_route(self):
        if self.loading_port == self.discharge_port:
            raise ValueError(
                "Loading and discharge ports must be different"
            )
        return self


class CargoManifest(BaseModel):
    containers: list[Container]

    @model_validator(mode="after")
    def validate_unique_ids(self):
        ids = [container.container_id for container in self.containers]

        if len(ids) != len(set(ids)):
            raise ValueError("Container IDs must be unique")

        return self

 