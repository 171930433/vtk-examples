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

In the case of `GetColor3d()` a `vtkColor3d` class is returned not a vector, tuple or a simple variable.
