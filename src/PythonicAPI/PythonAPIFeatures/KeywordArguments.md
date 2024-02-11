You can initialze the properties of a wrapped VTK class by specifying keyword arguments in the constructor.

``` Python
cylinder = vtkCylinderSource(resolution=8)
```

or

``` Python
pl3d = vtkMultiBlockPLOT3DReader(x_y_z_file_name=xyz_fn,
                                q_file_name=q_fn,
                                scalar_function_number=100,
                                vector_function_number=202)
   
```
