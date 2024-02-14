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

To reset the append filter, you any one of these:

``` Python
a.RemoveAllInputConnections(0)
None >> a
[] >> a
() >> a
```

**None** can also be used to clear any inputs, repeatable or not.
