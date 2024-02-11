A pipeline can have multiple connections:

``` Python
[vtk.vtkSphereSource(), vtk.vtkSphereSource()] >> vtk.vtkAppendFilter()
```

or

``` Python
a = vtk.vtkAppendFilter()
vtk.vtkSphereSource() >> a
vtk.vtkSphereSource() >> a
```

To reset the append filter, you have to use:

``` Python
a.RemoveAllInputConnections(0)
```
