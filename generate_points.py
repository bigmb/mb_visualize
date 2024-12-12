import random
import json
from datetime import datetime, timedelta

def generate_points(num_points=10000):
    # Generate random points in a sphere
    points = {
        "x": [],
        "y": [],
        "z": [],
        "taxcode": [],
        "date": [],
        "image": []
    }
    
    start_date = datetime(2023, 1, 1)
    
    for i in range(num_points):
        # Generate points in a sphere using rejection sampling
        while True:
            x = random.uniform(-5, 5)
            y = random.uniform(-5, 5)
            z = random.uniform(-5, 5)
            # Accept if point is within sphere
            if (x*x + y*y + z*z) <= 25:  # radius = 5
                break
        
        points["x"].append(round(x, 3))
        points["y"].append(round(y, 3))
        points["z"].append(round(z, 3))
        points["taxcode"].append(f"TAX{str(i).zfill(6)}")
        
        # Random date in 2023
        days = random.randint(0, 364)
        current_date = start_date + timedelta(days=days)
        points["date"].append(current_date.strftime("%Y-%m-%d"))
        
        points["image"].append(f"data/images/image{str(i).zfill(6)}.jpg")
    
    return points

def update_visualization(points):
    with open('visualization.html', 'r') as f:
        content = f.read()
    
    # Find the position to insert the data
    start_marker = "// Embedding data"
    data_start = content.find(start_marker)
    if data_start == -1:
        raise ValueError("Could not find data insertion point in visualization.html")
    
    # Find the next script section
    script_end = content.find("</script>", data_start)
    if script_end == -1:
        raise ValueError("Could not find script end")
    
    # Find where to insert the data (after the const pointsData = )
    data_line_start = content.find("const pointsData = ", data_start)
    if data_line_start == -1:
        raise ValueError("Could not find pointsData declaration")
    
    data_start = content.find("{", data_line_start)
    data_end = content.find("};", data_start) + 1
    
    # Replace the existing data with new data
    new_content = (
        content[:data_start] +
        json.dumps(points, indent=4) +
        content[data_end:]
    )
    
    with open('visualization.html', 'w') as f:
        f.write(new_content)

if __name__ == "__main__":
    points = generate_points(10000)
    update_visualization(points)
    print(f"Generated {len(points['x'])} points and updated visualization.html")
