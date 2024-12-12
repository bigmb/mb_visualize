import json
import random
from datetime import datetime, timedelta

# Generate 10000 random points
num_points = 10000
data = {
    "x": [random.uniform(-5, 5) for _ in range(num_points)],
    "y": [random.uniform(-5, 5) for _ in range(num_points)],
    "z": [random.uniform(-5, 5) for _ in range(num_points)],
    "taxcode": [f"TAX{str(i).zfill(6)}" for i in range(num_points)],
    "date": [],
    "image": [f"data/images/image{str(i).zfill(6)}.jpg" for i in range(num_points)]
}

# Generate dates between 2023-01-01 and 2023-12-31
start_date = datetime(2023, 1, 1)
for _ in range(num_points):
    days = random.randint(0, 364)
    current_date = start_date + timedelta(days=days)
    data["date"].append(current_date.strftime("%Y-%m-%d"))

# Save to JSON file
with open('data/embeddings/large_embedding.json', 'w') as f:
    json.dump(data, f, indent=2)
