
from typing import Literal

from pydantic import BaseModel, Field, model_validator

# Each slot represents one 20-foot base position.
# A 40-foot container must reserve two adjacent positions
# at the same row and tier.

class VesselSlot(BaseModel):
    slot_id: str
    bay: int = Field(ge=1)
    row: int = Field(ge=0)
    tier: int = Field(ge=2)
    location: Literal["hold", "deck"]

    
    max_weight_kg: float = Field(gt=0)
    supported_sizes_ft: list[Literal[20, 40]] = Field(default_factory=lambda: [20])
    footprint_bays: int = Field(default=1, ge=1)
    stack_id: str | None = None
    reefer_capable: bool = False
    hazardous_allowed: bool = True


    @property
    def position_code(self) -> str:
        return f"{self.bay:02d}-{self.row:02d}-{self.tier:02d}"


class VesselSlotPlan(BaseModel):
    vessel_id: str
    slots: list[VesselSlot]

    @model_validator(mode="after")
    def validate_slots(self):
        slot_ids = [slot.slot_id for slot in self.slots]
        positions = [
            (slot.bay, slot.row, slot.tier)
            for slot in self.slots
        ]

        if len(slot_ids) != len(set(slot_ids)):
            raise ValueError("Slot IDs must be unique")

        if len(positions) != len(set(positions)):
            raise ValueError("Physical slot positions must be unique")

        return self
