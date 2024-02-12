A pipeline can produce multiple outputs:

``` Python
    clipper = (
            superquadric_source >>
            vtkClipPolyData(clip_function=clip_plane, generate_clipped_output=True)
    ).update().output
```

Here the tuple `clipper` contains the clipped output as the first element and clipped away output is the second element.

