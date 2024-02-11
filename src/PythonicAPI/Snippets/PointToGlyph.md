### Description

Represent points as glyphs. The point is represented as a sphere.

To use the snippet, click the *Copy to clipboard* at the upper right of the code blocks.

### Implementation

``` Python

# from vtkmodules.vtkCommonDataModel import vtkPolyData
# from vtkmodules.vtkFiltersSources import vtkSphereSource
# from vtkmodules.vtkRenderingCore import (
#     vtkActor,
#     vtkGlyph3DMapper
# )


def point_to_glyph(points, scale):
    """
    Convert points to glyphs.
    :param points: The points to glyph.
    :param scale: The scale, used to determine the size of the
                  glyph representing the point, expressed as a
                  fraction of the largest side of the bounding
                  box surrounding the points. e.g. 0.05
    :return: The actor.
    """

    bounds = points.bounds
    max_len = 0.0
    for i in range(0, 3):
        max_len = max(bounds[i + 1] - bounds[i], max_len)

    sphere_source = vtkSphereSource(radius=scale * max_len)

    pd = vtkPolyData(points=points)

    mapper = vtkGlyph3DMapper(input_data=pd,
                              source_connection=sphere_source.output_port,
                              scalar_visibility=0,
                              scaling=0)

    return vtkActor(mapper=mapper)

```

### Usage

``` Python

    # Update may be needed.
    some_filter.update()
    # Map the points to spheres
    sphere_actor = point_to_glyph(some_filter.output.points, 0.05)
    sphere_actor.property.color = colors.GetColor3d('Violet')
    # Add the actor to the renderer.
    ren.AddActor(sphere_actor)

```
