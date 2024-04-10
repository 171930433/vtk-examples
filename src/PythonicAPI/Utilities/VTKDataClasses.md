### Description

These dataclasses are used to initialize the VTK classes.

These handle the `#define VTK_SOME_CONSTANT x` in the VTK C++ code.  The outer dataclass class name consists of the VTK class name (without the leading vtk).

The nested dataclasses are named after the relevant macro name in the VTK class.

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

- `BandedPolyDataContourFilter` refers to `?vtkBandedPolyDataContourFilter?`
- `ScalarMode` refers to the functions in the class called `SetScalarModeToIndex()` and `SetScalarModeToValue()`. This is why this subclass is named `ScalarMode`.

This allows us to write code like this:

``` Python
    bcf = ?vtkBandedPolyDataContourFilter?(
        input_data=p,
        scalar_mode=BandedPolyDataContourFilter.ScalarMode.VTK_SCALAR_MODE_INDEX,
        generate_contour_edges=True)

    # Use either the minimum or maximum value for each band.
    for k in bands:
        bcf.SetValue(k, bands[k][2])

```

Instead of:

``` Python
    bcf = ?vtkBandedPolyDataContourFilter?()
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
    Just copy the needed dataclasses into your own code. There is no requirement to copy all the dataclasses from here.

!!! note
    More dataclasses will be added in alphabetical order as the need arises.

!!! note
    Generally there is no need for a dataclass if an enum has been used in the C++ code and it is public.

!!! note
    If your Python version is less than 3.7, just remove the `@dataclass(frozen=True)` decorators. However the values will no longer be constant.
