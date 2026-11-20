
#!/usr/bin/env python3
"""Generate a 2D-extruded Ahmed-body Gmsh mesh.

Writes:
    - ahmed_body_2d_<level>_<wall-treatment>.geo
    - fix_mesh.sh

The ground boundary layer is deliberately stopped before the two
outer domain corners. The Ahmed-body boundary layer is unchanged.
"""

import math
import argparse

# ------------------------------------------------------------
# Ahmed body dimensions (m)
# ------------------------------------------------------------

L = 1.044
H = 0.288
GC = 0.050
SL = 0.222
R = 0.100
ANGLE = 25.0
N_FILLET = 20

# ------------------------------------------------------------
# Computational domain
# ------------------------------------------------------------

XMIN, XMAX = -5.0, 12.0
ZMIN, ZMAX = 0.0, 5.0

# Thin extrusion: exactly one cell layer
Y_START = 0.005
SPAN = 0.010

# Leave this many global mesh lengths at each ground corner
GROUND_BL_END_MARGIN_CELLS = 2.0

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


def stations():
    """Return (x, lower_z, upper_z) points defining the Ahmed body."""

    a = math.radians(ANGLE)
    x_slant = L - SL * math.cos(a)
    z_top = GC + H
    z_end = z_top - SL * math.sin(a)

    result = []

    for k in range(N_FILLET + 1):
        th = (math.pi / 2) * k / N_FILLET

        x = R * (1 - math.cos(th))
        inset = R * (1 - math.sin(th))

        result.append((
            x,
            GC + inset,
            z_top - inset,
        ))

    result.append((x_slant, GC, z_top))
    result.append((L, GC, z_end))

    return result


def boundary_layer_layer_count(first_layer, thickness, ratio):
    """Number of geometric layers needed to reach the requested thickness."""

    if ratio <= 1.0:
        return math.ceil(thickness / first_layer)

    return math.ceil(
        math.log(
            1.0 + thickness * (ratio - 1.0) / first_layer
        ) / math.log(ratio)
    )


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

    # Leave two global mesh lengths without ground BL at either end.
    ground_margin = GROUND_BL_END_MARGIN_CELLS * h_global

    ground_bl_start = XMIN + ground_margin
    ground_bl_end = XMAX - ground_margin

    if ground_bl_start >= ground_bl_end:
        raise ValueError("Ground BL end margins leave no active ground section.")

    # The lower inlet/outlet edge is split at the BL thickness height.
    # This preserves the existing corner-edge spacing strategy.
    corner_height = bl_thickness

    n_bl_layers = boundary_layer_layer_count(
        first_layer,
        bl_thickness,
        bl_ratio,
    )

    # --------------------------------------------------------
    # Ahmed body outline
    # --------------------------------------------------------

    sec = stations()

    body = [(x, zt) for x, zb, zt in sec]
    body += [(x, zb) for x, zb, zt in reversed(sec)]

    n = len(body)

    # --------------------------------------------------------
    # Geometry
    #
    # Outer points:
    # 1: bottom-left
    # 2: bottom-right
    # 3: outlet split point
    # 4: top-right
    # 5: top-left
    # 6: inlet split point
    # 7: ground BL start
    # 8: ground BL end
    #
    # Outer curves:
    # 1: upstream ground, no BL
    # 2: central ground, BL active
    # 3: downstream ground, no BL
    # 4: lower outlet
    # 5: upper outlet
    # 6: top
    # 7: upper inlet
    # 8: lower inlet
    # --------------------------------------------------------

    lines = [
        'SetFactory("Built-in");',
        'Mesh.MshFileVersion = 2.2;',
        f'Mesh.MeshSizeMin = {h_min};',
        f'Mesh.MeshSizeMax = {h_global};',
        'Mesh.MeshSizeFromPoints = 0;',
        'Mesh.MeshSizeFromCurvature = 0;',
        'Mesh.MeshSizeExtendFromBoundary = 0;',
        'Mesh.Algorithm = 5;',
        '',
        '// Outer domain points',
        f'Point(1) = {{{XMIN}, {Y_START}, {ZMIN}, {h_global}}};',
        f'Point(2) = {{{XMAX}, {Y_START}, {ZMIN}, {h_global}}};',
        f'Point(3) = {{{XMAX}, {Y_START}, {corner_height}, {h_global}}};',
        f'Point(4) = {{{XMAX}, {Y_START}, {ZMAX}, {h_global}}};',
        f'Point(5) = {{{XMIN}, {Y_START}, {ZMAX}, {h_global}}};',
        f'Point(6) = {{{XMIN}, {Y_START}, {corner_height}, {h_global}}};',
        f'Point(7) = {{{ground_bl_start}, {Y_START}, {ZMIN}, {h_global}}};',
        f'Point(8) = {{{ground_bl_end}, {Y_START}, {ZMIN}, {h_global}}};',
        '',
        '// Outer boundary curves',
        'Line(1) = {1, 7}; // Upstream ground: no BL',
        'Line(2) = {7, 8}; // Central ground: BL active',
        'Line(3) = {8, 2}; // Downstream ground: no BL',
        'Line(4) = {2, 3}; // Lower outlet',
        'Line(5) = {3, 4}; // Upper outlet',
        'Line(6) = {4, 5}; // Top',
        'Line(7) = {5, 6}; // Upper inlet',
        'Line(8) = {6, 1}; // Lower inlet',
        '',
        '// Match the lower inlet/outlet edge spacing to the BL progression',
        f'Transfinite Curve {{4}} = {n_bl_layers + 1} Using Progression {bl_ratio};',
        f'Transfinite Curve {{8}} = {n_bl_layers + 1} Using Progression {1.0 / bl_ratio:.12f};',
        '',
        'Curve Loop(1) = {1, 2, 3, 4, 5, 6, 7, 8};',
        '',
        '// Ahmed body points',
    ]

    # Body points start at 9; body curves start at 9.
    body_point_start = 9
    body_curve_start = 9

    for i, (x, z) in enumerate(body):
        pid = body_point_start + i

        lines.append(
            f'Point({pid}) = {{{x:.10f}, {Y_START}, {z:.10f}, {h_body}}};'
        )

    body_curves = []

    for i in range(n):
        cid = body_curve_start + i
        p1 = body_point_start + i
        p2 = body_point_start + (i + 1) % n

        lines.append(f'Line({cid}) = {{{p1}, {p2}}};')
        body_curves.append(cid)

    curve_list = ", ".join(map(str, body_curves))

    lines += [
        '',
        f'Curve Loop(2) = {{{curve_list}}};',
        'Plane Surface(1) = {1, 2};',
        '',
        '// 1. Refinement near the Ahmed body',
        'Field[1] = Distance;',
        f'Field[1].CurvesList = {{{curve_list}}};',
        'Field[1].Sampling = 100;',
        '',
        'Field[2] = Threshold;',
        'Field[2].InField = 1;',
        f'Field[2].SizeMin = {h_body};',
        f'Field[2].SizeMax = {h_global};',
        'Field[2].DistMin = 0.02;',
        'Field[2].DistMax = 0.60;',
        '',
        '// 2. Wake refinement',
        'Field[3] = Box;',
        f'Field[3].VIn = {h_wake};',
        f'Field[3].VOut = {h_global};',
        'Field[3].XMin = 0.8;',
        'Field[3].XMax = 8.0;',
        'Field[3].YMin = -0.006;',
        'Field[3].YMax = 0.006;',
        'Field[3].ZMin = 0.0;',
        'Field[3].ZMax = 1.0;',
        'Field[3].Thickness = 2.0;',
        '',
        '// 3. Ground-clearance refinement',
        'Field[4] = Box;',
        f'Field[4].VIn = {h_body};',
        f'Field[4].VOut = {h_global};',
        'Field[4].XMin = -0.2;',
        'Field[4].XMax = 1.5;',
        'Field[4].YMin = -0.006;',
        'Field[4].YMax = 0.006;',
        'Field[4].ZMin = 0.0;',
        'Field[4].ZMax = 0.16;',
        'Field[4].Thickness = 1.0;',
        '',
        'Field[5] = Min;',
        'Field[5].FieldsList = {2, 3, 4};',
        'Background Field = 5;',
        '',
        '// 4. Boundary layer',
        '// Ground BL is deliberately restricted to curve 2.',
        '// The Ahmed body BL remains active on all body curves.',
        'Field[6] = BoundaryLayer;',
        f'Field[6].CurvesList = {{2, {curve_list}}};',
        f'Field[6].Size = {first_layer};',
        f'Field[6].Thickness = {bl_thickness};',
        f'Field[6].Ratio = {bl_ratio};',
        'Field[6].Quads = 1;',
        'BoundaryLayer Field = 6;',
        '',
        '// Extrude exactly one cell layer through the 2D span',
        f'out[] = Extrude {{0, {-SPAN}, 0}} {{',
        '    Surface{1};',
        '    Layers{1};',
        '    Recombine;',
        '};',
        '',
        '// Physical patches',
        '// Outer curves are ordered 1 through 8 above.',
        'Physical Surface("frontAndBack") = {1, out[0]};',
        'Physical Surface("ground") = {out[2], out[3], out[4]};',
        'Physical Surface("outlet") = {out[5], out[6]};',
        'Physical Surface("top") = {out[7]};',
        'Physical Surface("inlet") = {out[8], out[9]};',
        f'Physical Surface("ahmed_body") = {{{", ".join(f"out[{i}]" for i in range(10, 10+n))}}};',
        'Physical Volume("fluid") = {out[1]};',
        '',
    ]

    filename = (
        f"ahmed_body_2d_{mesh_level}_"
        f"{wall_treatment.replace('-', '_')}.geo"
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # --------------------------------------------------------
    # OpenFOAM patch-type helper
    # --------------------------------------------------------

    fix_script = r"""#!/bin/bash
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
"""

    with open("fix_mesh.sh", "w", encoding="utf-8") as f:
        f.write(fix_script)

    import os
    os.chmod("fix_mesh.sh", 0o755)

    print(f"Generated {filename}")
    print("Generated fix_mesh.sh")
    print()
    print("Ground BL:")
    print(f"  Starts at x = {ground_bl_start:.3f} m")
    print(f"  Ends at   x = {ground_bl_end:.3f} m")
    print(f"  Corner margin = {ground_margin:.3f} m at each end")
    print()
    print("Physical patch mapping:")
    print("  ground     = out[2], out[3], out[4]")
    print("  outlet     = out[5], out[6]")
    print("  top        = out[7]")
    print("  inlet      = out[8], out[9]")
    print(f"  ahmed_body = out[10] through out[{9+n}]")
    print("  fluid      = out[1]")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

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

    generate_geo(args.mesh_level, args.wall_treatment)
