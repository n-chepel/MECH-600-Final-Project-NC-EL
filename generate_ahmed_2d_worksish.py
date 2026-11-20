
#!/usr/bin/env python3

import math
import argparse
import os

# ============================================================
# AHMED BODY DIMENSIONS (m)
# ============================================================

L = 1.044
H = 0.288
GC = 0.050
SL = 0.222
R = 0.100
ANGLE = 25.0
N_FILLET = 20

# ============================================================
# COMPUTATIONAL DOMAIN
# ============================================================

XMIN, XMAX = -5.0, 12.0
ZMIN, ZMAX = 0.0, 5.0

# Thin extrusion: one cell layer
Y_START = 0.005
SPAN = 0.010

# ============================================================
# MESH SETTINGS
# ============================================================

MESH_SETTINGS = {
    "coarse": {
        "global": 0.30,
        "body": 0.012,
        "wake": 0.030,
    },
    "normal": {
        "global": 0.30,
        "body": 0.006,
        "wake": 0.04,
    },
    "fine": {
        "global": 0.16,
        "body": 0.006,
        "wake": 0.015,
    },
}

WALL_SETTINGS = {
    "wall-functions": {
        "first_layer": 0.0008,
        "thickness": 0.006,
        "ratio": 1.10,
    },
    "wall-resolved": {
        "first_layer": 0.00002,
        "thickness": 0.008,
        "ratio": 1.10,
    },
}


# ============================================================
# AHMED BODY GEOMETRY
# ============================================================

def stations():

    a = math.radians(ANGLE)

    x_slant = L - SL * math.cos(a)
    z_top = GC + H
    z_end = z_top - SL * math.sin(a)

    result = []

    # Rounded front nose
    for k in range(N_FILLET + 1):

        th = (math.pi / 2) * k / N_FILLET

        x = R * (1 - math.cos(th))
        inset = R * (1 - math.sin(th))

        result.append((
            x,
            GC + inset,
            z_top - inset
        ))

    # Roof and rear
    result.append((x_slant, GC, z_top))
    result.append((L, GC, z_end))

    return result


# ============================================================
# CALCULATE CORNER BOUNDARY DISCRETIZATION
# ============================================================

def corner_mesh_parameters(first_layer, thickness, ratio):

    # Estimate the number of boundary-layer intervals needed
    # to reach the specified total thickness.
    n_layers = math.ceil(
        math.log(
            1.0 + thickness * (ratio - 1.0) / first_layer
        ) / math.log(ratio)
    )

    n_layers = max(1, n_layers)

    # Height occupied by the corresponding geometric series
    corner_height = (
        first_layer
        * (ratio ** n_layers - 1.0)
        / (ratio - 1.0)
    )

    return n_layers, corner_height


# ============================================================
# WRITE fix_mesh.sh
# ============================================================

def write_fix_mesh():

    script = r'''#!/bin/bash

set -e

boundary="constant/polyMesh/boundary"

if [ ! -f "$boundary" ]; then
    echo "ERROR: $boundary not found."
    echo "Run gmshToFoam before running this script."
    exit 1
fi

# Convert front and back to empty patches.
sed -i '/^[[:space:]]*frontAndBack[[:space:]]*$/,/^[[:space:]]*}/ s/type[[:space:]]*patch;/type empty;/' "$boundary"

# Convert ground to a wall.
sed -i '/^[[:space:]]*ground[[:space:]]*$/,/^[[:space:]]*}/ s/type[[:space:]]*patch;/type wall;/' "$boundary"

# Convert Ahmed body to a wall.
sed -i '/^[[:space:]]*ahmed_body[[:space:]]*$/,/^[[:space:]]*}/ s/type[[:space:]]*patch;/type wall;/' "$boundary"

echo "Boundary patch types updated:"
echo "  frontAndBack: empty"
echo "  ground:       wall"
echo "  ahmed_body:   wall"
echo "  inlet:        unchanged"
echo "  outlet:       unchanged"
echo "  top:          unchanged"
'''

    with open("fix_mesh.sh", "w") as f:
        f.write(script)

    os.chmod("fix_mesh.sh", 0o755)

    print("Generated fix_mesh.sh")


# ============================================================
# GENERATE GMSH GEOMETRY
# ============================================================

def generate_geo(mesh_level, wall_treatment):

    settings = MESH_SETTINGS[mesh_level]
    wall = WALL_SETTINGS[wall_treatment]

    h_global = settings["global"]
    h_body = settings["body"]
    h_wake = settings["wake"]

    first_layer = wall["first_layer"]
    bl_thickness = wall["thickness"]
    bl_ratio = wall["ratio"]

    h_min = min(h_body, first_layer)

    # Calculate inlet/outlet lower-segment spacing
    n_bl_layers, corner_height = corner_mesh_parameters(
        first_layer,
        bl_thickness,
        bl_ratio
    )

    n_corner_points = n_bl_layers + 1

    # Ensure the split point remains inside the domain
    if corner_height >= ZMAX:
        raise ValueError("Calculated corner height exceeds domain height.")

    sec = stations()

    # Body outline
    body = [(x, zt) for x, zb, zt in sec]
    body += [(x, zb) for x, zb, zt in reversed(sec)]

    n = len(body)

    lines = [

        '// Generated Ahmed body 2D geometry',
        'SetFactory("Built-in");',

        '',
        'Mesh.MshFileVersion = 2.2;',
        f'Mesh.MeshSizeMin = {h_min};',
        f'Mesh.MeshSizeMax = {h_global};',

        'Mesh.MeshSizeFromPoints = 0;',
        'Mesh.MeshSizeFromCurvature = 0;',
        'Mesh.MeshSizeExtendFromBoundary = 0;',

        'Mesh.Algorithm = 5;',

        '',

        '// ====================================================',
        '// OUTER DOMAIN CORNER POINTS',
        '// ====================================================',

        f'Point(1) = {{{XMIN}, {Y_START}, {ZMIN}, {h_global}}};',
        f'Point(2) = {{{XMAX}, {Y_START}, {ZMIN}, {h_global}}};',
        f'Point(3) = {{{XMAX}, {Y_START}, {ZMAX}, {h_global}}};',
        f'Point(4) = {{{XMIN}, {Y_START}, {ZMAX}, {h_global}}};',

        '',

        '// Intermediate points on inlet and outlet',
        '// positioned at the end of the lower graded segment',

        f'Point(5) = {{{XMAX}, {Y_START}, {corner_height:.12f}, {first_layer}}};',
        f'Point(6) = {{{XMIN}, {Y_START}, {corner_height:.12f}, {first_layer}}};',

        '',

        '// ====================================================',
        '// OUTER BOUNDARY CURVES',
        '// ====================================================',

        'Line(1) = {1, 2}; // Ground',
        'Line(2) = {2, 5}; // Lower outlet',
        'Line(3) = {5, 3}; // Upper outlet',
        'Line(4) = {3, 4}; // Top',
        'Line(5) = {4, 6}; // Upper inlet',
        'Line(6) = {6, 1}; // Lower inlet',

        'Curve Loop(1) = {1, 2, 3, 4, 5, 6};',

        '',

        '// ====================================================',
        '// EXPLICIT INLET/OUTLET CORNER DISCRETIZATION',
        '// ====================================================',

        '// Outlet: curve runs from ground upwards',
        f'Transfinite Curve {{2}} = {n_corner_points} Using Progression {bl_ratio:.12f};',

        '// Inlet: curve runs from top down towards ground',
        f'Transfinite Curve {{6}} = {n_corner_points} Using Progression {1.0/bl_ratio:.12f};',

        '',

        '// ====================================================',
        '// AHMED BODY OUTLINE',
        '// ====================================================',
    ]

    # Body points start at ID 7
    for i, (x, z) in enumerate(body):

        pid = 7 + i

        lines.append(
            f'Point({pid}) = '
            f'{{{x:.10f}, {Y_START}, {z:.10f}, {h_body}}};'
        )

    # Body curves
    body_curves = []

    for i in range(n):

        cid = 7 + n + i

        p1 = 7 + i
        p2 = 7 + (i + 1) % n

        lines.append(
            f'Line({cid}) = {{{p1}, {p2}}};'
        )

        body_curves.append(cid)

    curve_list = ', '.join(map(str, body_curves))

    lines += [

        '',
        f'Curve Loop(2) = {{{curve_list}}};',
        'Plane Surface(1) = {1, 2};',

        '',

        '// ====================================================',
        '// BODY REFINEMENT',
        '// ====================================================',

        'Field[1] = Distance;',
        f'Field[1].CurvesList = {{{curve_list}}};',
        'Field[1].Sampling = 100;',

        'Field[2] = Threshold;',
        'Field[2].InField = 1;',
        f'Field[2].SizeMin = {h_body};',
        f'Field[2].SizeMax = {h_global};',
        'Field[2].DistMin = 0.02;',
        'Field[2].DistMax = 0.60;',

        '',

        '// ====================================================',
        '// WAKE REFINEMENT',
        '// ====================================================',

        'Field[3] = Box;',
        f'Field[3].VIn = {h_wake};',
        f'Field[3].VOut = {h_global};',
        'Field[3].XMin = 0.8;',
        'Field[3].XMax = 8.0;',
        'Field[3].YMin = -0.006;',
        'Field[3].YMax = 0.006;',
        'Field[3].ZMin = 0.0;',
        'Field[3].ZMax = 0.8;',

        '',

        '// ====================================================',
        '// GROUND CLEARANCE REFINEMENT',
        '// ====================================================',

        'Field[4] = Box;',
        f'Field[4].VIn = {h_body};',
        f'Field[4].VOut = {h_global};',
        'Field[4].XMin = -0.2;',
        'Field[4].XMax = 1.5;',
        'Field[4].YMin = -0.006;',
        'Field[4].YMax = 0.006;',
        'Field[4].ZMin = 0.0;',
        'Field[4].ZMax = 0.16;',

        '',

        'Field[5] = Min;',
        'Field[5].FieldsList = {2, 3, 4};',
        'Background Field = 5;',

        '',

        '// ====================================================',
        '// BOUNDARY LAYER',
        '// ====================================================',

        'Field[6] = BoundaryLayer;',
        f'Field[6].CurvesList = {{1, {curve_list}}};',

        f'Field[6].Size = {first_layer};',
        f'Field[6].Thickness = {bl_thickness};',
        f'Field[6].Ratio = {bl_ratio};',

        'Field[6].Quads = 1;',
        'BoundaryLayer Field = 6;',

        '',

        '// ====================================================',
        '// EXTRUDE ONE CELL THROUGH SPAN',
        '// ====================================================',

        f'out[] = Extrude {{0, {-SPAN}, 0}} {{',
        '    Surface{1};',
        '    Layers{1};',
        '    Recombine;',
        '};',

        '',

        '// ====================================================',
        '// PHYSICAL PATCHES FOR OPENFOAM',
        '// ====================================================',

        'Physical Surface("frontAndBack") = {1, out[0]};',

        'Physical Surface("ground") = {out[2]};',

        'Physical Surface("outlet") = {out[3], out[4]};',

        'Physical Surface("top") = {out[5]};',

        'Physical Surface("inlet") = {out[6], out[7]};',

        f'Physical Surface("ahmed_body") = '
        f'{{{", ".join(f"out[{i}]" for i in range(8, 8+n))}}};',

        'Physical Volume("fluid") = {out[1]};',

        ''
    ]

    filename = (
        f"ahmed_body_2d_{mesh_level}_"
        f"{wall_treatment.replace('-', '_')}.geo"
    )

    with open(filename, "w") as f:
        f.write("\n".join(lines))

    print(f"\nGenerated {filename}")

    print(f"Mesh level: {mesh_level}")
    print(f"Wall treatment: {wall_treatment}")
    print(f"Global size: {h_global} m")
    print(f"Body size: {h_body} m")
    print(f"Wake size: {h_wake} m")

    print("\nBoundary-layer settings:")
    print(f"  First layer: {first_layer} m")
    print(f"  Total thickness: {bl_thickness} m")
    print(f"  Growth ratio: {bl_ratio}")

    print("\nInlet/outlet lower boundary settings:")
    print(f"  Number of elements: {n_bl_layers}")
    print(f"  Number of points: {n_corner_points}")
    print(f"  Lower segment height: {corner_height:.8f} m")

    write_fix_mesh()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate a 2D Ahmed-body mesh using Gmsh."
    )

    parser.add_argument(
        "--mesh-level",
        choices=["coarse", "normal", "fine"],
        default="normal",
    )

    parser.add_argument(
        "--wall-treatment",
        choices=["wall-functions", "wall-resolved"],
        default="wall-functions",
    )

    args = parser.parse_args()

    generate_geo(
        args.mesh_level,
        args.wall_treatment
    )
