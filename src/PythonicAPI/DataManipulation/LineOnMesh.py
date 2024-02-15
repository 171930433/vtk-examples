#!/usr/bin/env python3

import numpy as np

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonComputationalGeometry import vtkParametricSpline
from vtkmodules.vtkCommonCore import (
    mutable,
    vtkPoints,
    vtkUnsignedCharArray
)
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkCellLocator,
    vtkPolyData,
    vtkTriangle
)
from vtkmodules.vtkFiltersCore import vtkCleanPolyData
from vtkmodules.vtkFiltersModeling import vtkLoopSubdivisionFilter
from vtkmodules.vtkFiltersSources import vtkParametricFunctionSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    named_colors = vtkNamedColors()

    # Make a 32 x 32 grid.
    size = 32

    # Define z values for the topography.
    # Comment out the following line if you want a different random
    #  distribution each time the script is run.
    np.random.seed(3)
    topography = np.random.randint(0, 5, (size, size))

    # Define points, triangles and colors
    colors = vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    points = vtkPoints()
    triangles = vtkCellArray()

    # Build the meshgrid manually.
    count = 0
    for i in range(size - 1):
        for j in range(size - 1):
            z1 = topography[i][j]
            z2 = topography[i][j + 1]
            z3 = topography[i + 1][j]

            # Triangle 1
            points.InsertNextPoint(i, j, z1)
            points.InsertNextPoint(i, (j + 1), z2)
            points.InsertNextPoint((i + 1), j, z3)

            triangle = vtkTriangle()
            triangle.GetPointIds().SetId(0, count)
            triangle.GetPointIds().SetId(1, count + 1)
            triangle.GetPointIds().SetId(2, count + 2)

            triangles.InsertNextCell(triangle)

            z1 = topography[i][j + 1]
            z2 = topography[i + 1][j + 1]
            z3 = topography[i + 1][j]

            # Triangle 2
            points.InsertNextPoint(i, (j + 1), z1)
            points.InsertNextPoint((i + 1), (j + 1), z2)
            points.InsertNextPoint((i + 1), j, z3)

            triangle = vtkTriangle()
            triangle.GetPointIds().SetId(0, count + 3)
            triangle.GetPointIds().SetId(1, count + 4)
            triangle.GetPointIds().SetId(2, count + 5)

            count += 6

            triangles.InsertNextCell(triangle)

            # Add some color.
            r = [int(i / float(size) * 255), int(j / float(size) * 255), 0]
            colors.InsertNextTypedTuple(r)
            colors.InsertNextTypedTuple(r)
            colors.InsertNextTypedTuple(r)
            colors.InsertNextTypedTuple(r)
            colors.InsertNextTypedTuple(r)
            colors.InsertNextTypedTuple(r)

    # Create a polydata object.
    triangle_poly_data = vtkPolyData()

    # Add the geometry and topology to the polydata.
    triangle_poly_data.SetPoints(points)
    triangle_poly_data.GetPointData().SetScalars(colors)
    triangle_poly_data.SetPolys(triangles)

    # Clean the polydata so that the edges are shared!
    clean_poly_data = vtkCleanPolyData()

    # Use a filter to smooth the data (will add triangles and smooth).
    smooth_loop = vtkLoopSubdivisionFilter(number_of_subdivisions=3)

    # Create a mapper and actor for smoothed dataset.
    mapper = vtkPolyDataMapper()
    triangle_poly_data >> clean_poly_data >> smooth_loop >> mapper
    actor_loop = vtkActor(mapper=mapper)
    actor_loop.property.SetInterpolationToFlat()

    # Define a cellLocator to be able to compute intersections between lines.
    # and the surface
    # Also update smooth_loop so that vtkCellLocator finds cells!
    locator = vtkCellLocator(data_set=smooth_loop.update().output)
    locator.BuildLocator()

    max_loop = 1000
    dist = 20.0 / max_loop
    tolerance = 0.001

    # Make a list of points. Each point is the intersection of a vertical line
    # defined by p1 and p2 and the surface.
    points = vtkPoints()
    for i in range(max_loop):
        p1 = [2 + i * dist, 16, -1]
        p2 = [2 + i * dist, 16, 6]

        # Outputs (we need only pos which is the x, y, z position
        # of the intersection)
        t = mutable(0)
        pos = [0.0, 0.0, 0.0]
        pcoords = [0.0, 0.0, 0.0]
        sub_id = mutable(0)
        locator.IntersectWithLine(p1, p2, tolerance, t, pos, pcoords, sub_id)

        # Add a slight offset in z.
        pos[2] += 0.01
        # Add the x, y, z position of the intersection.
        points.InsertNextPoint(pos)

    # Create a spline and add the points
    spline = vtkParametricSpline(points=points)
    function_source = vtkParametricFunctionSource(u_resolution=max_loop, parametric_function=spline)

    # Map the spline
    mapper = vtkPolyDataMapper()
    function_source >> mapper

    # Define the line actor
    actor = vtkActor(mapper=mapper)
    actor.property.line_width = 3
    actor.property.SetColor(named_colors.GetColor3d('Red'))

    # Visualize
    renderer = vtkRenderer(background=named_colors.GetColor3d('Cornsilk'))
    render_window = vtkRenderWindow(size=(800, 800), window_name='LineOnMesh')
    render_window.AddRenderer(renderer)
    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Add actors and render
    renderer.AddActor(actor)
    renderer.AddActor(actor_loop)

    render_window.Render()
    renderer.active_camera.position = (-32.471276, 53.258788, 61.209332)
    renderer.active_camera.focal_point = (15.500000, 15.500000, 2.000000)
    renderer.active_camera.view_up = (0.348057, -0.636740, 0.688055)
    renderer.ResetCameraClippingRange()
    render_window.Render()

    render_window_interactor.Initialize()
    render_window_interactor.Start()


if __name__ == '__main__':
    main()
