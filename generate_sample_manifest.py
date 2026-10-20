
import csv
import random
from pathlib import Path

random.seed(42)

OUTPUT_FILE = Path(__file__).parent / "sample_manifest_2000.csv"

loading_ports = ["JNPT"]
discharge_ports = ["Colombo", "Singapore", "Port Klang", "Rotterdam"]

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "container_id",
            "size_ft",
            "weight_kg",
            "loading_port",
            "discharge_port",
            "destination_order",
            "refrigerated",
            "hazardous",
        ],
    )
    writer.writeheader()

    for i in range(1, 2001):
        size_ft = random.choices([20, 40], weights=[0.55, 0.45])[0]

        # Plausible illustrative gross weights, in kilograms
        if size_ft == 20:
            weight_kg = random.randint(5000, 30000)
        else:
            weight_kg = random.randint(8000, 30000)

        discharge_port = random.choice(discharge_ports)

        writer.writerow({
            "container_id": f"CONT-{i:04d}",
            "size_ft": size_ft,
            "weight_kg": weight_kg,
            "loading_port": random.choice(loading_ports),
            "discharge_port": discharge_port,
            "destination_order": discharge_ports.index(discharge_port) + 1,
            "refrigerated": random.random() < 0.08,
            "hazardous": random.random() < 0.04,
        })

print(f"Created: {OUTPUT_FILE}")
print("Container records: 2000")
