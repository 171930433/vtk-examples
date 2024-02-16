# Python API Comments

## Initializing a VTK Class

You can initialze the properties of a wrapped VTK class by specifying keyword arguments in the constructor.

| Example Name | Comments | Image |
| -------------- | ---------------------- | ------- |
[WarpCombustor](/PythonAPI/VisualizationAlgorithms/WarpCombustor) | Note that in the initialization of `?vtkMultiBlockPLOT3DReader?`, `SetFileName` is an alias for `SetXYZFileName` so you can use `file_name` instead of `x_y_z_file_name`.
[ParametricKuenDemo](/PythonAPI/GeometricObjects/ParametricKuenDemo) | Very useful in regards to the intitialization of `?vtkSliderRepresentation2D?` in `make_slider_widget(...)`.

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

A pipeline can have multiple connections:

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
[WarpCombustor](/PythonAPI/VisualizationAlgorithms/WarpCombustor) | Three planes are added to a `?vtkAppendPolyData?`filter.

## Multiple outputs from a pipeline

A pipeline can produce multiple outputs

| Example Name | Comments | Image |
| -------------- | ---------------------- | ------- |
[WarpCombustor](/PythonAPI/Meshes/SolidClip) | The tuple `clipper` contains the clipped output as the first element and clipped away output is the second element.

## Updating part of a pipeline

Sometimes we need to update part of a pipeline so that output can be used in other pipelines.

| Example Name | Comments | Image |
| -------------- | ---------------------- | ------- |
[LineOnMesh](/PythonAPI/DataManipulation/LineOnMesh) | One pipeline creates a smoothed dataset. However we need to update `smooth_loop` in the pipeline so that `?vtkCellLocator?` finds cells in order to create the spline.
[MeshLabelImageColor](/PythonAPI/DataManipulation/MeshLabelImageColor) | We need the smoother error for the scalar range in the mapper. So we create the pipeline and update `smoother` to get the needed scalar range. Of course, all other pipeline elements feeding into `smoother` will be updated also.
