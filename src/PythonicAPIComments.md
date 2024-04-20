# Python API Comments

## Initializing a VTK Class

You can initialize the properties of a wrapped VTK class by specifying keyword arguments in the constructor.

| Example Name | Comments | Image |
| -------------- | ---------------------- | ------- |
[WarpCombustor](/PythonicAPI/VisualizationAlgorithms/WarpCombustor) | Note that in the initialization of `?vtkMultiBlockPLOT3DReader?`, `SetFileName` is an alias for `SetXYZFileName` so you can use `file_name` instead of `xyz_file_name`.
[ParametricKuenDemo](/PythonicAPI/GeometricObjects/ParametricKuenDemo) | Very useful in regards to the intitialization of `?vtkSliderRepresentation2D?` in `make_slider_widget(...)`.

## Set/Get Properties of a VTK Class

Instead of `SetSomeProperty()` or `GetSomeProperty()` you can just just drop the Set or Get prefix and use the snake case version of the suffix: `some_property`.

``` Python
    print(
        f'Cylinder properties:\n   height: {cylinder.height}, radius: {cylinder.radius},'
        f' center: {cylinder.center} resolution: {cylinder.resolution} capping: {cylinder.capping == 1}')

```

Generally if a VTK class has a Set or Get method then converting the name to snake case will give you the relevant property e.g. for `SetResolution()` or `GetResolution` the wrapped property will be `resolution`.

However:

``` Python
ca.GetProperty().SetColor(colors.GetColor3d('Tomato'))
```

becomes:

``` Python
ca.property.color=colors.GetColor3d('Tomato')
```

In the case of `GetColor3d()` a `?vtkColor3d?` class is returned not a vector, tuple or a simple variable.

## Multiple connections in a pipeline

A pipeline can have multiple connections.

``` Python
    (a, b, c) >> d >> e >> f >> g
```

E.g.

``` Python
[vtk.?vtkSphereSource?(), vtk.?vtkSphereSource?()] >> vtk.?vtkAppendFilter?()
```

or

``` Python
a = vtk.?vtkAppendFilter?()
vtk.?vtkSphereSource?() >> a
vtk.?vtkSphereSource?() >> a
```

To reset the append filter, you can use any one of these commands:

``` Python
a.RemoveAllInputConnections(0)
None >> a
[] >> a
() >> a
```

Note: `None >> a` can also be used to clear any inputs on the filter `a`, whether they are multiple connections or not.

| Example Name | Comments | Image |
| -------------- | ---------------------- | ------- |
[WarpCombustor](/PythonicAPI/VisualizationAlgorithms/WarpCombustor) | Three planes are added to a `?vtkAppendPolyData?`filter.

## Multiple outputs from a pipeline

A pipeline can produce multiple outputs. Here, p is a tuple of ?vtkDataObject?s, for example: `p: tuple(?vtkDataObject?, ..., ?vtkDataObject?)`. Subsequent pipelines can access the individual elements of the tuple.

``` Python
    p = (a >> b >> c).update().output
    p1 = vtkSomeClass(input_data=p[0]) >> e >> f
    p1 = vtkAnotherClass(input_data=p[1]) >> g >> h
```

| Example Name | Comments | Image |
| -------------- | ---------------------- | ------- |
[SolidClip](/PythonicAPI/Meshes/SolidClip) | The tuple `clipper` contains the clipped output as the first element and clipped away output as the second element.

## Updating part of a pipeline

Sometimes we need to update part of a pipeline so that output can be used in other pipelines.

``` Python
    a >> b >> c >> d
    c.update() # At this point, a and b will also be updated.
    # Use some data from c to build a new object, say v.
    ...
    # Then:
    v >> w >> x 
```

| Example Name | Comments | Image |
| -------------- | ---------------------- | ------- |
[LineOnMesh](/PythonicAPI/DataManipulation/LineOnMesh) | One pipeline creates a smoothed dataset. However we need to update `smooth_loop` in the pipeline so that `?vtkCellLocator?` finds cells in order to create the spline.
[MeshLabelImageColor](/PythonicAPI/DataManipulation/MeshLabelImageColor) | We need the smoother error for the scalar range in the mapper. So we create the pipeline and update `smoother` to get the needed scalar range. Of course, all other pipeline elements feeding into `smoother` will be updated also.

## Reusing a pipeline

Pipelines can be reused.

``` Python
    # The pipeline to reuse.
    p = (a >> b >> c)
    # Sources for the pipeline.
    s1 = d
    s2 = e
    # Use the pipeline in a functional way.
    p1 = p(s1())
    p2 = p(s2())
```

| Example Name | Comments | Image |
| -------------- | ---------------------- | ------- |
[PipelineReuse](/PythonicAPI/GeometricObjects/PipelineReuse) | Here we use the pipeline in a functional way. This allows us to reuse the pipeline, here, p(cone()) returns a data object so any changes to the pipeline afterward would not be automatically propagated to the rendering pipeline. Finally, we use an append filter to combine the cone and cylinder.

## Grouping pipelines

Grpuping the pipelines into code blocks may improve the readability of the code.

| Example Name | Comments | Image |
| -------------- | ---------------------- | ------- |
[EnhanceEdges](/PythonicAPI/ImageProcessing/EnhanceEdges) | The pipelines are grouped into a single code block. This may make understanding the code easier.

## How to handle #defines using dataclasses

This example, [CurvaturesNormalsElevations](/PythonicAPI/Visualization/CurvaturesNormalsElevations), is relatively complex in that a single source feeds into two functions `generate_gaussian_curvatures(...)` and `generate_mean_curvatures(...)` returning filters, scalar ranges of curvatures and elevation along with the lookup tables. Additionally a text widget and scalar bar widgets are positioned into two viewports. It nicely demonstrates the usage of dataclasses.

We can initialize nearly all properties of a wrapped VTK class by specifying keyword arguments in the constructor. There are no issues if the properties are True or False or an existing variable or an enum (which is wrapped in Python) e.g.:

``` Python
color_series = ?vtkColorSeries?(color_scheme=?vtkColorSeries?.BREWER_QUALITATIVE_SET3)
```

However, a lot of Set/Get functions in the VTK classes use values defined as `#define VTK_SOME_CONSTANT x`, these are not wrapped. In order to get around this we can use a data class in Python 3.7 or later.

The real advantage of this approach is that the defined VTK constants are used instead of meaningless integers or other values.

| Example Name | Comments | Image |
| -------------- | ---------------------- | ------- |
[VTKDataClasses](/PythonicAPI/Snippets/VTKDataClasses.md) | This snippet defines immutable dataclasses that can be used in the initialization of VTK classes or to replace the Set/Get functions that set and get these constants.
[CurvaturesNormalsElevations](/PythonicAPI/Visualization/CurvaturesNormalsElevations) | A lot of immutable dataclasses are used in this example


## Python functions and pipelines

A Python function returning a VTK object can be used as the first element of a pipeline.

- If the function returns `None`, then the pipeline will never be implemented.

``` Python
            read_poly_data(pth) >> mapper
```

Try this example with a `.csv` file to see what happens.

| Example Name | Comments | Image |
| -------------- | ---------------------- | ------- |
[ReadAllPolyDataTypesDemo](/PythonicAPI/IO/ReadAllPolyDataTypesDemo) | `read_poly_data(pth)` returns polydata that is fed directly into the mapper.

## Snippets

Here are some code snippets that can be directly dropped into your code [Snippets](/PythonicAPI/Snippets.md).

## PythonicAPI hints


### ?vtkLookupTable?

When using vtkLookupTable, code like:

``` Python
        lut.table_value = (i, r, g, b, 1.0)
```

will give the wrong color.

Keep using:

``` Python
        lut.SetTableValue(i, r, g, b, 1.0)
```

See [SmoothDiscreteFlyingEdges3D](/PythonicAPI/Modelling/SmoothDiscreteFlyingEdges3D)

## Python hints

### Make a tuple if you have a starred expression

In [MultiplePlots](/PythonicAPI/Plotting/MultiplePlots) we had an expression:

``` Python
    points.SetColor(*colors.GetColor4ub('Black'))
```

This can be rewritten as a tuple, using brackets and a comma:

``` Python
    points.color = (*colors.GetColor4ub('Black'),)
```

or, even better, by using a tuple constructor to make it more obvious:

``` Python
    points.color = tuple(colors.GetColor4ub('Black'))
```
