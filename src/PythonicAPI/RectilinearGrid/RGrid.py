#!/usr/bin/env python3

"""
This example shows how to create a rectilinear grid.
"""

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkDoubleArray
from vtkmodules.vtkCommonDataModel import vtkRectilinearGrid
from vtkmodules.vtkFiltersGeometry import vtkRectilinearGridGeometryFilter
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    x = [-1.22396, -1.17188, -1.11979, -1.06771, -1.01562, -0.963542, -0.911458, -0.859375, -0.807292, -0.755208,
         -0.703125, -0.651042, -0.598958, -0.546875, -0.494792, -0.442708, -0.390625, -0.338542, -0.286458, -0.234375,
         -0.182292, -0.130209, -0.078125, -0.026042, 0.0260415, 0.078125, 0.130208, 0.182291, 0.234375, 0.286458,
         0.338542, 0.390625, 0.442708, 0.494792, 0.546875, 0.598958, 0.651042, 0.703125, 0.755208, 0.807292, 0.859375,
         0.911458, 0.963542, 1.01562, 1.06771, 1.11979, 1.17188]
    y = [-1.25, -1.17188, -1.09375, -1.01562, -0.9375, -0.859375, -0.78125, -0.703125, -0.625, -0.546875, -0.46875,
         -0.390625, -0.3125, -0.234375, -0.15625, -0.078125, 0, 0.078125, 0.15625, 0.234375, 0.3125, 0.390625, 0.46875,
         0.546875, 0.625, 0.703125, 0.78125, 0.859375, 0.9375, 1.01562, 1.09375, 1.17188, 1.25]
    z = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.75, 1.8, 1.9, 2,
         2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.75, 2.8, 2.9, 3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.75, 3.8, 3.9]
    print(f'Sizes: x: {len(x)}, y: {len(y)}, z: {len(z)}')

    # Create a rectilinear grid by defining three arrays specifying the
    # coordinates in the x-y-z directions.
    x_coords = vtkDoubleArray()
    for i in range(0, len(x)):
        x_coords.InsertNextValue(x[i])
    y_coords = vtkDoubleArray()
    for i in range(0, len(y)):
        y_coords.InsertNextValue(y[i])
    z_coords = vtkDoubleArray()
    for i in range(0, len(z)):
        z_coords.InsertNextValue(z[i])

    # The coordinates are assigned to the rectilinear grid. Make sure that
    # the number of values in each of the x_coordinates, y_coordinates,
    # and z_coordinates is equal to what is defined in dimensions.
    rgrid = vtkRectilinearGrid(dimensions=(len(x), len(y), len(z)),
                               x_coordinates=x_coords, y_coordinates=y_coords, z_coordinates=z_coords)

    # Extract a plane from the grid to see what we've got.
    plane = vtkRectilinearGridGeometryFilter(extent=(0, len(x) - 1, 16, 16, 0, len(z) - 1))

    rgrid_mapper = vtkPolyDataMapper()
    rgrid >> plane >> rgrid_mapper

    wire_actor = vtkActor(mapper=rgrid_mapper)
    wire_actor.property.color = colors.GetColor3d('Banana')
    wire_actor.property.edge_visibility = True

    # Create the usual rendering stuff.
    renderer = vtkRenderer(background=colors.GetColor3d('Beige'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='RGrid')
    ren_win.AddRenderer(renderer)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    renderer.AddActor(wire_actor)
    renderer.ResetCamera()
    renderer.active_camera.Elevation(60.0)
    renderer.active_camera.Azimuth(30.0)
    renderer.active_camera.Zoom(1.0)

    # Interact with the data.
    ren_win.Render()
    iren.Start()


if __name__ == '__main__':
    main()
