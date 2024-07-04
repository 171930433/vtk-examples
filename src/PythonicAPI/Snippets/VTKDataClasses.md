### Introduction

These immutable dataclasses are usually used in the initialization VTK classes or to replace the Set/Get functions that set and get these constants.

These handle the `#define VTK_SOME_CONSTANT x` in the VTK C++ code.  The outer dataclass class name consists of the VTK class name (without the leading vtk).

The nested dataclasses are named after the relevant function/macro name in the VTK class.

The big advantage of using dataclasses is that:

- The values in the class are constant because of `frozen=True`
- We can use meaningful names consistent with the naming of the VTK defines e.g. `VTK_SCALAR_MODE_INDEX`

For example:

``` Python
@dataclass(frozen=True)
class BandedPolyDataContourFilter:
    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_INDEX: int = 0
        VTK_SCALAR_MODE_VALUE: int = 1

```

Here:

- `BandedPolyDataContourFilter` refers to `vtkBandedPolyDataContourFilter`
- `ScalarMode` refers to the functions in the class called `SetScalarModeToIndex()` and `SetScalarModeToValue()`. This is why this subclass is named `ScalarMode`.

This allows us to write code like this:

``` Python
    bcf = vtkBandedPolyDataContourFilter(
        input_data=p,
        scalar_mode=BandedPolyDataContourFilter.ScalarMode.VTK_SCALAR_MODE_INDEX,
        generate_contour_edges=True)

    # Use either the minimum or maximum value for each band.
    for k in bands:
        bcf.SetValue(k, bands[k][2])

```

Instead of:

``` Python
    bcf = vtkBandedPolyDataContourFilter()
    bcf.SetInputData(cc.GetOutput())
    # Use either the minimum or maximum value for each band.
    for k in bands:
        bcf.SetValue(k, bands[k][2])
    # We will use an indexed lookup table.
    bcf.SetScalarModeToIndex()
    bcf.GenerateContourEdgesOn()

```

For an example of the usage of dataclasses, please see: [CurvaturesNormalsElevations](../../Visualization/CurvaturesNormalsElevations).

!!! note
    Just copy the needed dataclasses into your own code.
    More dataclasses will be added in alphabetical order as the need arises.

!!! note
    Generally there is no need for a dataclass if a public enum has been used in the C++ code. Just use a particular enum in this case.

To use these dataclasses, remember to import the following:

``` Python
from dataclasses import dataclass
```

### BandedPolyDataContourFilter

``` Python
@dataclass(frozen=True)
class BandedPolyDataContourFilter:
    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_INDEX: int = 0
        VTK_SCALAR_MODE_VALUE: int = 1

```

### ColorTransferFunction

``` Python
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

```

### ConnectivityFilter

``` Python
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

```

### Coordinate

``` Python
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

```

### Curvatures

``` Python
@dataclass(frozen=True)
class Curvatures:
    @dataclass(frozen=True)
    class CurvatureType:
        VTK_CURVATURE_GAUSS: int = 0
        VTK_CURVATURE_MEAN: int = 1
        VTK_CURVATURE_MAXIMUM: int = 2
        VTK_CURVATURE_MINIMUM: int = 3

```

### Cutter

``` Python
@dataclass(frozen=True)
class Cutter:
    @dataclass(frozen=True)
    class SortBy:
        VTK_SORT_BY_VALUE: int = 0
        VTK_SORT_BY_CELL: int = 1

```

### DataObjectToDataSetFilter

``` Python
class DataObjectToDataSetFilter:
    @dataclass(frozen=True)
    class DataSetType:
        VTK_POLY_DATA: int = 0
        VTK_STRUCTURED_POINTS: int = 1
        VTK_STRUCTURED_GRID: int = 2
        VTK_RECTILINEAR_GRID: int = 3
        VTK_UNSTRUCTURED_GRID: int = 4

```

### FieldDataToAttributeDataFilter

``` Python
@dataclass(frozen=True)
class FieldDataToAttributeDataFilter:
    @dataclass(frozen=True)
    class InputField:
        VTK_DATA_OBJECT_FIELD: int = 0
        VTK_POINT_DATA_FIELD: int = 1
        VTK_CELL_DATA_FIELD: int = 2

    @dataclass(frozen=True)
    class OutputAttributeData:
        VTK_CELL_DATA: int = 0
        VTK_POINT_DATA: int = 1

```

### Glyph3D

``` Python
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

```

### GlyphSource2D

``` Python
@dataclass(frozen=True)
class GlyphSource2D:
    @dataclass(frozen=True)
    class GlyphType:
        VTK_NO_GLYPH: int = 0
        VTK_VERTEX_GLYPH: int = 1
        VTK_DASH_GLYPH: int = 2
        VTK_CROSS_GLYPH: int = 3
        VTK_THICKCROSS_GLYPH: int = 4
        VTK_TRIANGLE_GLYPH: int = 5
        VTK_SQUARE_GLYPH: int = 6
        VTK_CIRCLE_GLYPH: int = 7
        VTK_DIAMOND_GLYPH: int = 8
        VTK_ARROW_GLYPH: int = 9
        VTK_THICKARROW_GLYPH: int = 10
        VTK_HOOKEDARROW_GLYPH: int = 11
        VTK_EDGEARROW_GLYPH: int = 12

```

### HyperStreamline

``` Python
@dataclass(frozen=True)
class HyperStreamline:
    @dataclass(frozen=True)
    class IntegrationDirection:
        VTK_INTEGRATE_FORWARD: int = 0
        VTK_INTEGRATE_BACKWARD: int = 1
        VTK_INTEGRATE_BOTH_DIRECTIONS: int = 2

    @dataclass(frozen=True)
    class IntegrationEigenvector:
        VTK_INTEGRATE_MAJOR_EIGENVECTOR: int = 0
        VTK_INTEGRATE_MEDIUM_EIGENVECTOR: int = 1
        VTK_INTEGRATE_MINOR_EIGENVECTOR: int = 2

```

### ImageCanvasSource2D

``` Python
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

```

### ImageCast

``` Python
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


```

### ImageImport

``` Python
@dataclass(frozen=True)
class ImageImport:
    @dataclass(frozen=True)
    class DataScalarType:
        VTK_UNSIGNED_CHAR: int = 3
        VTK_SHORT: int = 4
        VTK_UNSIGNED_SHORT: int = 5
        VTK_INT: int = 6
        VTK_FLOAT: int = 10
        VTK_DOUBLE: int = 11

```

### ImageMathematics

``` Python
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

```

### ImageProperty

``` Python
@dataclass(frozen=True)
class ImageProperty:
    @dataclass(frozen=True)
    class InterpolationType:
        VTK_NEAREST_INTERPOLATION: int = 0
        VTK_LINEAR_INTERPOLATION: int = 1
        VTK_CUBIC_INTERPOLATION: int = 2

```

### LandmarkTransform

``` Python
@dataclass(frozen=True)
class LandmarkTransform:
    @dataclass(frozen=True)
    class Mode:
        VTK_LANDMARK_RIGIDBODY: int = 6
        VTK_LANDMARK_SIMILARITY: int = 7
        VTK_LANDMARK_AFFINE: int = 12

```

### Lights

``` Python
@dataclass(frozen=True)
class Light:
    @dataclass(frozen=True)
    class LightType:
        VTK_LIGHT_TYPE_HEADLIGHT: int = 1
        VTK_LIGHT_TYPE_CAMERA_LIGHT: int = 2
        VTK_LIGHT_TYPE_SCENE_LIGHT: int = 3

```

### LinearExtrusionFilter

``` Python
@dataclass(frozen=True)
class LinearExtrusionFilter:
    @dataclass(frozen=True)
    class ExtrusionType:
        VTK_VECTOR_EXTRUSION: int = 1
        VTK_NORMAL_EXTRUSION: int = 2
        VTK_POINT_EXTRUSION: int = 3

```

### LookupTable

``` Python
@dataclass(frozen=True)
class LookupTable:
    @dataclass(frozen=True)
    class Scale:
        VTK_SCALE_LINEAR: int = 0
        VTK_SCALE_LOG10: int = 1

```

### Mapper

``` Python
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

```

### Property

``` Python
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

```

### RuledSurfaceFilter

``` Python
@dataclass(frozen=True)
class RuledSurfaceFilter:
    @dataclass(frozen=True)
    class RuledMode:
        VTK_RULED_MODE_RESAMPLE: int = 0
        VTK_RULED_MODE_POINT_WALK: int = 1

```

### SphereWidget

``` Python
@dataclass(frozen=True)
class SphereWidget:
    @dataclass(frozen=True)
    class Representation:
        VTK_SPHERE_OFF: int = 0
        VTK_SPHERE_WIREFRAME: int = 1
        VTK_SPHERE_SURFACE: int = 2

```

### SpiderPlotActor

``` Python
@dataclass(frozen=True)
class SpiderPlotActor:
    @dataclass(frozen=True)
    class IndependentVariables:
        VTK_IV_COLUMN: int = 0
        VTK_IV_ROW: int = 1

```

### TextProperty

``` Python
@dataclass(frozen=True)
class TextProperty:
    @dataclass(frozen=True)
    class FontFamily:
        VTK_ARIAL: int = 0
        VTK_COURIER: int = 1
        VTK_TIMES: int = 2
        VTK_UNKNOWN_FONT: int = 3

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

```

### Texture

``` Python
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

```

### TubeFilter

``` Python
@dataclass(frozen=True)
class TubeFilter:
    @dataclass(frozen=True)
    class VaryRadius:
        VTK_VARY_RADIUS_OFF: int = 0
        VTK_VARY_RADIUS_BY_SCALAR: int = 1
        VTK_VARY_RADIUS_BY_VECTOR: int = 2
        VTK_VARY_RADIUS_BY_ABSOLUTE_SCALAR: int = 3
        VTK_VARY_RADIUS_BY_VECTOR_NORM: int = 4
```

### VolumeProperty

``` Python
@dataclass(frozen=True)
class VolumeProperty:
    @dataclass(frozen=True)
    class InterpolationType:
        VTK_NEAREST_INTERPOLATION: int = 0
        VTK_LINEAR_INTERPOLATION: int = 1
        VTK_CUBIC_INTERPOLATION: int = 2

```

### VoxelModeller

``` VoxelModeller
    @dataclass(frozen=True)
    class ScalarType:
        VTK_BIT: int = 1
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

```

### WindowToImageFilter

``` Python
@dataclass(frozen=True)
class WindowToImageFilter:
    @dataclass(frozen=True)
    class InputBufferType:
        VTK_RGB: int = 3
        VTK_RGBA: int = 4
        VTK_ZBUFFER: int = 5

```
