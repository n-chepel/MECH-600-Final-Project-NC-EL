
import re
import numpy as np
from pathlib import Path

mesh = Path("constant/polyMesh")

# Face indices reported by checkMesh
bad_faces = [120127, 120405]


def read_foam_list(filename):
    """Read an ASCII OpenFOAM list."""
    content = (mesh / filename).read_text()

    # Remove comments
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.S)
    content = re.sub(r"//.*", "", content)

    if "format      binary" in content:
        raise ValueError(f"{filename} is binary; ASCII required.")

    # Extract list body after the count
    match = re.search(r"\n\s*\d+\s*\(", content)
    if not match:
        raise ValueError(f"Could not find list in {filename}")

    return content[match.end():content.rfind(")")]


# Read mesh points
point_data = read_foam_list("points")
points = np.array([
    [float(v) for v in p.split()]
    for p in re.findall(r"\(([^()]*)\)", point_data)
])

# Read mesh faces
face_data = read_foam_list("faces")
faces = [
    [int(v) for v in f.split()]
    for f in re.findall(r"\d+\s*\(([^()]*)\)", face_data)
]

print(f"Read {len(points)} points and {len(faces)} faces\n")

for index in bad_faces:
    vertex_ids = faces[index]
    vertices = points[vertex_ids]
    centre = vertices.mean(axis=0)

    print(f"Face {index}:")
    print(f"  Vertices: {vertex_ids}")
    print(f"  Centroid: {centre}")
    print(f"  Coordinates:\n{vertices}\n")
