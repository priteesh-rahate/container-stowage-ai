
import json
from unittest.mock import patch

from backend.ai_batching import get_ai_batch_proposals
from backend.models import Container
from backend.vessel_layout import create_vessel_layout

containers = [
    Container(
        container_id=f"TEST-{i}",
        size_ft=20,
        weight_kg=12000,
        loading_port="JNPT",
        discharge_port="Singapore",
        destination_order=1,
    )
    for i in range(6)
]

vessel = create_vessel_layout()
calls = []

def fake_qwen(prompt):
    data = json.loads(prompt)
    calls.append(len(data["containers"]))

    return json.dumps({
        "placements": [{
            "container_ref": 0,
            "slot_ref": len(calls) - 1
        }]
    })

with patch(
    "backend.ai_service.propose_container_placements",
    side_effect=fake_qwen
):
    proposals = get_ai_batch_proposals(
        containers,
        vessel.slots,
        {(s.bay, s.row, s.tier): s for s in vessel.slots},
        max_batches=2,
    )

assert calls == [5, 1], f"Wrong batch sizes: {calls}"
assert len(proposals) == 2

print("Batch sizes:", calls)
print("AI calls:", len(calls))
print("Multi-batch test: PASS")
