#!/bin/bash
set -e

boundary="constant/polyMesh/boundary"

test -f "$boundary" || {
    echo "ERROR: $boundary not found. Run gmshToFoam first."
    exit 1
}

# Convert the 2D front/back patches to empty.
sed -i '/frontAndBack/,/}/ s/type[[:space:]]*patch;/type            empty;/' "$boundary"

# Convert solid surfaces to wall patches.
for patch in ground ahmed_body; do
    sed -i "/^[[:space:]]*${patch}[[:space:]]*$/,/}/ s/type[[:space:]]*patch;/type            wall;/" "$boundary"
done

echo "Boundary patch types updated. Verify constant/polyMesh/boundary."
