SetFactory("Built-in");
Mesh.MshFileVersion = 2.2;
Mesh.MeshSizeMin = 0.0008;
Mesh.MeshSizeMax = 0.3;
Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeExtendFromBoundary = 0;
Mesh.Algorithm = 5;

// Outer domain points
Point(1) = {-5.0, 0.005, 0.0, 0.3};
Point(2) = {12.0, 0.005, 0.0, 0.3};
Point(3) = {12.0, 0.005, 0.006, 0.3};
Point(4) = {12.0, 0.005, 5.0, 0.3};
Point(5) = {-5.0, 0.005, 5.0, 0.3};
Point(6) = {-5.0, 0.005, 0.006, 0.3};
Point(7) = {-4.4, 0.005, 0.0, 0.3};
Point(8) = {11.4, 0.005, 0.0, 0.3};

// Outer boundary curves
Line(1) = {1, 7}; // Upstream ground: no BL
Line(2) = {7, 8}; // Central ground: BL active
Line(3) = {8, 2}; // Downstream ground: no BL
Line(4) = {2, 3}; // Lower outlet
Line(5) = {3, 4}; // Upper outlet
Line(6) = {4, 5}; // Top
Line(7) = {5, 6}; // Upper inlet
Line(8) = {6, 1}; // Lower inlet

// Match the lower inlet/outlet edge spacing to the BL progression
Transfinite Curve {4} = 7 Using Progression 1.1;
Transfinite Curve {8} = 7 Using Progression 0.909090909091;

Curve Loop(1) = {1, 2, 3, 4, 5, 6, 7, 8};

// Ahmed body points
Point(9) = {0.0000000000, 0.005, 0.2380000000, 0.006};
Point(10) = {0.0003082666, 0.005, 0.2458459096, 0.006};
Point(11) = {0.0012311659, 0.005, 0.2536434465, 0.006};
Point(12) = {0.0027630080, 0.005, 0.2613445364, 0.006};
Point(13) = {0.0048943484, 0.005, 0.2689016994, 0.006};
Point(14) = {0.0076120467, 0.005, 0.2762683432, 0.006};
Point(15) = {0.0108993476, 0.005, 0.2833990500, 0.006};
Point(16) = {0.0147359836, 0.005, 0.2902498565, 0.006};
Point(17) = {0.0190983006, 0.005, 0.2967785252, 0.006};
Point(18) = {0.0239594034, 0.005, 0.3029448048, 0.006};
Point(19) = {0.0292893219, 0.005, 0.3087106781, 0.006};
Point(20) = {0.0350551952, 0.005, 0.3140405966, 0.006};
Point(21) = {0.0412214748, 0.005, 0.3189016994, 0.006};
Point(22) = {0.0477501435, 0.005, 0.3232640164, 0.006};
Point(23) = {0.0546009500, 0.005, 0.3271006524, 0.006};
Point(24) = {0.0617316568, 0.005, 0.3303879533, 0.006};
Point(25) = {0.0690983006, 0.005, 0.3331056516, 0.006};
Point(26) = {0.0766554636, 0.005, 0.3352369920, 0.006};
Point(27) = {0.0843565535, 0.005, 0.3367688341, 0.006};
Point(28) = {0.0921540904, 0.005, 0.3376917334, 0.006};
Point(29) = {0.1000000000, 0.005, 0.3380000000, 0.006};
Point(30) = {0.8427996713, 0.005, 0.3380000000, 0.006};
Point(31) = {1.0440000000, 0.005, 0.2441787459, 0.006};
Point(32) = {1.0440000000, 0.005, 0.0500000000, 0.006};
Point(33) = {0.8427996713, 0.005, 0.0500000000, 0.006};
Point(34) = {0.1000000000, 0.005, 0.0500000000, 0.006};
Point(35) = {0.0921540904, 0.005, 0.0503082666, 0.006};
Point(36) = {0.0843565535, 0.005, 0.0512311659, 0.006};
Point(37) = {0.0766554636, 0.005, 0.0527630080, 0.006};
Point(38) = {0.0690983006, 0.005, 0.0548943484, 0.006};
Point(39) = {0.0617316568, 0.005, 0.0576120467, 0.006};
Point(40) = {0.0546009500, 0.005, 0.0608993476, 0.006};
Point(41) = {0.0477501435, 0.005, 0.0647359836, 0.006};
Point(42) = {0.0412214748, 0.005, 0.0690983006, 0.006};
Point(43) = {0.0350551952, 0.005, 0.0739594034, 0.006};
Point(44) = {0.0292893219, 0.005, 0.0792893219, 0.006};
Point(45) = {0.0239594034, 0.005, 0.0850551952, 0.006};
Point(46) = {0.0190983006, 0.005, 0.0912214748, 0.006};
Point(47) = {0.0147359836, 0.005, 0.0977501435, 0.006};
Point(48) = {0.0108993476, 0.005, 0.1046009500, 0.006};
Point(49) = {0.0076120467, 0.005, 0.1117316568, 0.006};
Point(50) = {0.0048943484, 0.005, 0.1190983006, 0.006};
Point(51) = {0.0027630080, 0.005, 0.1266554636, 0.006};
Point(52) = {0.0012311659, 0.005, 0.1343565535, 0.006};
Point(53) = {0.0003082666, 0.005, 0.1421540904, 0.006};
Point(54) = {0.0000000000, 0.005, 0.1500000000, 0.006};
Line(9) = {9, 10};
Line(10) = {10, 11};
Line(11) = {11, 12};
Line(12) = {12, 13};
Line(13) = {13, 14};
Line(14) = {14, 15};
Line(15) = {15, 16};
Line(16) = {16, 17};
Line(17) = {17, 18};
Line(18) = {18, 19};
Line(19) = {19, 20};
Line(20) = {20, 21};
Line(21) = {21, 22};
Line(22) = {22, 23};
Line(23) = {23, 24};
Line(24) = {24, 25};
Line(25) = {25, 26};
Line(26) = {26, 27};
Line(27) = {27, 28};
Line(28) = {28, 29};
Line(29) = {29, 30};
Line(30) = {30, 31};
Line(31) = {31, 32};
Line(32) = {32, 33};
Line(33) = {33, 34};
Line(34) = {34, 35};
Line(35) = {35, 36};
Line(36) = {36, 37};
Line(37) = {37, 38};
Line(38) = {38, 39};
Line(39) = {39, 40};
Line(40) = {40, 41};
Line(41) = {41, 42};
Line(42) = {42, 43};
Line(43) = {43, 44};
Line(44) = {44, 45};
Line(45) = {45, 46};
Line(46) = {46, 47};
Line(47) = {47, 48};
Line(48) = {48, 49};
Line(49) = {49, 50};
Line(50) = {50, 51};
Line(51) = {51, 52};
Line(52) = {52, 53};
Line(53) = {53, 54};
Line(54) = {54, 9};

Curve Loop(2) = {9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54};
Plane Surface(1) = {1, 2};

// 1. Refinement near the Ahmed body
Field[1] = Distance;
Field[1].CurvesList = {9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54};
Field[1].Sampling = 100;

Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = 0.006;
Field[2].SizeMax = 0.3;
Field[2].DistMin = 0.02;
Field[2].DistMax = 0.60;

// 2. Wake refinement
Field[3] = Box;
Field[3].VIn = 0.04;
Field[3].VOut = 0.3;
Field[3].XMin = 0.8;
Field[3].XMax = 8.0;
Field[3].YMin = -0.006;
Field[3].YMax = 0.006;
Field[3].ZMin = 0.0;
Field[3].ZMax = 1.0;
Field[3].Thickness = 2.0;

// 3. Ground-clearance refinement
Field[4] = Box;
Field[4].VIn = 0.006;
Field[4].VOut = 0.3;
Field[4].XMin = -0.2;
Field[4].XMax = 1.5;
Field[4].YMin = -0.006;
Field[4].YMax = 0.006;
Field[4].ZMin = 0.0;
Field[4].ZMax = 0.16;
Field[4].Thickness = 1.0;

Field[5] = Min;
Field[5].FieldsList = {2, 3, 4};
Background Field = 5;

// 4. Boundary layer
// Ground BL is deliberately restricted to curve 2.
// The Ahmed body BL remains active on all body curves.
Field[6] = BoundaryLayer;
Field[6].CurvesList = {2, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54};
Field[6].Size = 0.0008;
Field[6].Thickness = 0.006;
Field[6].Ratio = 1.1;
Field[6].Quads = 1;
BoundaryLayer Field = 6;

// Extrude exactly one cell layer through the 2D span
out[] = Extrude {0, -0.01, 0} {
    Surface{1};
    Layers{1};
    Recombine;
};

// Physical patches
// Outer curves are ordered 1 through 8 above.
Physical Surface("frontAndBack") = {1, out[0]};
Physical Surface("ground") = {out[2], out[3], out[4]};
Physical Surface("outlet") = {out[5], out[6]};
Physical Surface("top") = {out[7]};
Physical Surface("inlet") = {out[8], out[9]};
Physical Surface("ahmed_body") = {out[10], out[11], out[12], out[13], out[14], out[15], out[16], out[17], out[18], out[19], out[20], out[21], out[22], out[23], out[24], out[25], out[26], out[27], out[28], out[29], out[30], out[31], out[32], out[33], out[34], out[35], out[36], out[37], out[38], out[39], out[40], out[41], out[42], out[43], out[44], out[45], out[46], out[47], out[48], out[49], out[50], out[51], out[52], out[53], out[54], out[55]};
Physical Volume("fluid") = {out[1]};
