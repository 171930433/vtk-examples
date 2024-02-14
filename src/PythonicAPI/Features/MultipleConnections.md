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

To reset the append filter, you can use any one of these commands:

``` Python
a.RemoveAllInputConnections(0)
None >> a
[] >> a
() >> a
```

Note: `None >> a` can also be used to clear any inputs on the filter `a`, whether they are multiple connections or not.
