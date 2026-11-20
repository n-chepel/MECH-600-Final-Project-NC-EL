#!/bin/bash
# Fix the boundary types directly in the mesh file
sed -i '/frontAndBack/,/}/ s/type.*patch;/type            empty;/' constant/polyMesh/boundary
sed -i '/ground/,/}/ s/type.*patch;/type            wall;/' constant/polyMesh/boundary
sed -i '/ahmed_body/,/}/ s/type.*patch;/type            wall;/' constant/polyMesh/boundary

# Ensure the inGroups are correct
sed -i '/frontAndBack/,/}/ s/inGroups.*/inGroups        List<word> 1(empty);/' constant/polyMesh/boundary
sed -i '/ground/,/}/ s/inGroups.*/inGroups        List<word> 1(wall);/' constant/polyMesh/boundary
sed -i '/ahmed_body/,/}/ s/inGroups.*/inGroups        List<word> 1(wall);/' constant/polyMesh/boundary

echo "Boundary patches fixed successfully."
