#!/usr/bin/env python3

from dataclasses import dataclass

"""
    These handle the "#define VTK_SOME_CONSTANT x" in the VTK C++ code.
    The outer dataclass class name consists of the VTK class name
     (without the leading vtk).
    The nested dataclasses are named after the relevant macro name in the
     VTK class.
    
    Note: To find these constants, use the link to the header in the
          documentation for the class.
"""


@dataclass(frozen=True)
class BandedPolyDataContourFilter:
    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_INDEX: int = 0
        VTK_SCALAR_MODE_VALUE: int = 1


@dataclass(frozen=True)
class ColorTransferFunction:
    @dataclass(frozen=True)
    class ColorSpace:
        VTK_CTF_RGB: int = 0
        VTK_CTF_HSV: int = 1
        VTK_CTF_LAB: int = 2
        VTK_CTF_DIVERGING: int = 3
        VTK_CTF_LAB_CIEDE2000: int = 4
        VTK_CTF_STEP: int = 5

    @dataclass(frozen=True)
    class Scale:
        VTK_CTF_LINEAR: int = 0
        VTK_CTF_LOG10: int = 1


@dataclass(frozen=True)
class ConnectivityFilter:
    @dataclass(frozen=True)
    class ExtractionMode:
        VTK_EXTRACT_POINT_SEEDED_REGIONS: int = 1
        VTK_EXTRACT_CELL_SEEDED_REGIONS: int = 2
        VTK_EXTRACT_SPECIFIED_REGIONS: int = 3
        VTK_EXTRACT_LARGEST_REGION: int = 4
        VTK_EXTRACT_ALL_REGIONS: int = 5
        VTK_EXTRACT_CLOSEST_POINT_REGION: int = 6


@dataclass(frozen=True)
class Coordinate:
    @dataclass(frozen=True)
    class CoordinateSystem:
        VTK_DISPLAY: int = 0
        VTK_NORMALIZED_DISPLAY: int = 1
        VTK_VIEWPORT: int = 2
        VTK_NORMALIZED_VIEWPORT: int = 3
        VTK_VIEW: int = 4
        VTK_POSE: int = 5
        VTK_WORLD: int = 6
        VTK_USERDEFINED: int = 7


@dataclass(frozen=True)
class Curvatures:
    @dataclass(frozen=True)
    class CurvatureType:
        VTK_CURVATURE_GAUSS: int = 0
        VTK_CURVATURE_MEAN: int = 1
        VTK_CURVATURE_MAXIMUM: int = 2
        VTK_CURVATURE_MINIMUM: int = 3


@dataclass(frozen=True)
class Glyph3D:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_BY_SCALE: int = 0
        VTK_COLOR_BY_SCALAR: int = 1
        VTK_COLOR_BY_VECTOR: int = 2

    @dataclass(frozen=True)
    class IndexMode:
        VTK_INDEXING_OFF: int = 0
        VTK_INDEXING_BY_SCALAR: int = 1
        VTK_INDEXING_BY_VECTOR: int = 2

    @dataclass(frozen=True)
    class ScaleMode:
        VTK_SCALE_BY_SCALAR: int = 0
        VTK_SCALE_BY_VECTOR: int = 1
        VTK_SCALE_BY_VECTORCOMPONENTS: int = 2
        VTK_DATA_SCALING_OFF: int = 3

    @dataclass(frozen=True)
    class VectorMode:
        VTK_USE_VECTOR: int = 0
        VTK_USE_NORMAL: int = 1
        VTK_VECTOR_ROTATION_OFF: int = 2
        VTK_FOLLOW_CAMERA_DIRECTION: int = 3


@dataclass(frozen=True)
class ImageCanvasSource2D:
    @dataclass(frozen=True)
    class ScalarType:
        VTK_CHAR: int = 2
        VTK_UNSIGNED_CHAR: int = 3
        VTK_SHORT: int = 4
        VTK_UNSIGNED_SHORT: int = 5
        VTK_INT: int = 6
        VTK_UNSIGNED_INT: int = 7
        VTK_LONG: int = 8
        VTK_UNSIGNED_LONG: int = 9
        VTK_FLOAT: int = 10
        VTK_DOUBLE: int = 11


@dataclass(frozen=True)
class ImageCast:
    @dataclass(frozen=True)
    class OutputScalarType:
        VTK_CHAR: int = 2
        VTK_UNSIGNED_CHAR: int = 3
        VTK_SHORT: int = 4
        VTK_UNSIGNED_SHORT: int = 5
        VTK_INT: int = 6
        VTK_UNSIGNED_INT: int = 7
        VTK_LONG: int = 8
        VTK_UNSIGNED_LONG: int = 9
        VTK_FLOAT: int = 10
        VTK_DOUBLE: int = 11


@dataclass(frozen=True)
class ImageMathematics:
    @dataclass(frozen=True)
    class Operation:
        VTK_ADD: int = 0
        VTK_SUBTRACT: int = 1
        VTK_MULTIPLY: int = 2
        VTK_DIVIDE: int = 3
        VTK_INVERT: int = 4
        VTK_SIN: int = 5
        VTK_COS: int = 6
        VTK_EXP: int = 7
        VTK_LOG: int = 8
        VTK_ABS: int = 9
        VTK_SQR: int = 10
        VTK_SQRT: int = 11
        VTK_MIN: int = 12
        VTK_MAX: int = 13
        VTK_ATAN: int = 14
        VTK_ATAN2: int = 15
        VTK_MULTIPLYBYK: int = 16
        VTK_ADDC: int = 17
        VTK_CONJUGATE: int = 18
        VTK_COMPLEX_MULTIPLY: int = 19
        VTK_REPLACECBYK: int = 20


@dataclass(frozen=True)
class LandmarkTransform:
    @dataclass(frozen=True)
    class Mode:
        VTK_LANDMARK_RIGIDBODY: int = 6
        VTK_LANDMARK_SIMILARITY: int = 7
        VTK_LANDMARK_AFFINE: int = 12


@dataclass(frozen=True)
class LookupTable:
    @dataclass(frozen=True)
    class Scale:
        VTK_SCALE_LINEAR: int = 0
        VTK_SCALE_LOG10: int = 1


@dataclass(frozen=True)
class Mapper:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_MODE_DEFAULT: int = 0
        VTK_COLOR_MODE_MAP_SCALARS: int = 1
        VTK_COLOR_MODE_DIRECT_SCALARS: int = 2

    @dataclass(frozen=True)
    class ResolveCoincidentTopology:
        VTK_RESOLVE_OFF: int = 0
        VTK_RESOLVE_POLYGON_OFFSET: int = 1
        VTK_RESOLVE_SHIFT_ZBUFFER: int = 2

    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_DEFAULT: int = 0
        VTK_SCALAR_MODE_USE_POINT_DATA: int = 1
        VTK_SCALAR_MODE_USE_CELL_DATA: int = 2
        VTK_SCALAR_MODE_USE_POINT_FIELD_DATA: int = 3
        VTK_SCALAR_MODE_USE_CELL_FIELD_DATA: int = 4
        VTK_SCALAR_MODE_USE_FIELD_DATA: int = 5


@dataclass(frozen=True)
class Property:
    @dataclass(frozen=True)
    class Interpolation:
        VTK_FLAT: int = 0
        VTK_GOURAUD: int = 1
        VTK_PHONG: int = 2
        VTK_PBR: int = 3

    @dataclass(frozen=True)
    class Representation:
        VTK_POINTS: int = 0
        VTK_WIREFRAME: int = 1
        VTK_SURFACE: int = 2


@dataclass(frozen=True)
class SpiderPlotActor:
    @dataclass(frozen=True)
    class IndependentVariables:
        VTK_IV_COLUMN: int = 0
        VTK_IV_ROW: int = 1


@dataclass(frozen=True)
class TextProperty:
    @dataclass(frozen=True)
    class Justification:
        VTK_TEXT_LEFT: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_RIGHT: int = 2

    @dataclass(frozen=True)
    class VerticalJustification:
        VTK_TEXT_BOTTOM: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_TOP: int = 2


@dataclass(frozen=True)
class Texture:
    @dataclass(frozen=True)
    class Quality:
        VTK_TEXTURE_QUALITY_DEFAULT: int = 0
        VTK_TEXTURE_QUALITY_16BIT: int = 16
        VTK_TEXTURE_QUALITY: int = 32

    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_MODE_DEFAULT: int = 0
        VTK_COLOR_MODE_MAP_SCALARS: int = 1
        VTK_COLOR_MODE_DIRECT_SCALARS: int = 2


@dataclass(frozen=True)
class VolumeProperty:
    @dataclass(frozen=True)
    class InterpolationType:
        VTK_NEAREST_INTERPOLATION: int = 0
        VTK_LINEAR_INTERPOLATION: int = 1
        VTK_CUBIC_INTERPOLATION: int = 2
