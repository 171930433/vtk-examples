#!/usr/bin/env python3

import numpy
# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkMinimalStandardRandomSequence,
    vtkPoints,
    vtkUnsignedCharArray
)
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkPolyData,
    vtkTriangle
)
from vtkmodules.vtkFiltersCore import vtkCleanPolyData
from vtkmodules.vtkFiltersModeling import (
    vtkButterflySubdivisionFilter,
    vtkLoopSubdivisionFilter
)
from vtkmodules.vtkInteractionWidgets import (
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty
)


def main():
    nc = vtkNamedColors()

    # Make a 32 x 32 grid
    size = 32

    rn = vtkMinimalStandardRandomSequence(seed=1)
    # rn.SetSeed(1)

    # Define z values for the topography (random height)
    topography = numpy.zeros([size, size])
    for i in range(size):
        for j in range(size):
            topography[i][j] = rn.GetRangeValue(0, 5)
            rn.Next()

    # Define points, triangles and colors
    colors = vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    points = vtkPoints()
    triangles = vtkCellArray()

    # Build the meshgrid manually
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
    triangle_poly_data >> clean_poly_data

    # Use a filter to smooth the data (will add triangles and smooth).
    # Use two different filters to show the difference.
    smooth_loop = vtkLoopSubdivisionFilter(number_of_subdivisions=3)

    smooth_butterfly = vtkButterflySubdivisionFilter(number_of_subdivisions=3)

    # Create a mapper and actor for the initial dataset.
    mapper = vtkPolyDataMapper()
    clean_poly_data >> mapper
    actor = vtkActor(mapper=mapper, position=(0, 8, 0))

    # Create a mapper and actor for smoothed dataset (vtkLoopSubdivisionFilter).
    mapper = vtkPolyDataMapper()
    clean_poly_data >> smooth_loop >> mapper
    actor_loop = vtkActor(mapper=mapper, position=(0, 8, 0))

    # Create a mapper and actor for smoothed dataset (vtkButterflySubdivisionFilter).
    mapper = vtkPolyDataMapper()
    clean_poly_data >> smooth_butterfly >> mapper
    actor_butterfly = vtkActor(mapper=mapper, position=(0, 8, 0))

    render_window = vtkRenderWindow(size=(900, 300))
    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    text = {0: 'Initial Terrain', 1: 'Loop Subdivision', 2: 'Butterfly Subdivision'}

    # Define viewport ranges [x_min, y_min, x_max, y_max]
    viewports = {0: [0.0, 0.0, 1.0 / 3.0, 1.0],
                 1: [1.0 / 3.0, 0.0, 2.0 / 3.0, 1.0],
                 2: [2.0 / 3.0, 0.0, 1.0, 1.0]
                 }
    camera = None
    # Build the renderers and add them to the render window.
    renderers = list()
    for k in text.keys():
        renderers.append(vtkRenderer(background=nc.GetColor3d('Cornsilk')))

        # Add the actors.
        if k == 0:
            renderers[k].AddActor(actor)
        elif k == 1:
            renderers[k].AddActor(actor_loop)
        elif k == 2:
            renderers[k].AddActor(actor_butterfly)

        if k == 0:
            camera = renderers[k].GetActiveCamera()
            camera.Elevation(-45)
        else:
            renderers[k].SetActiveCamera(camera)

        renderers[k].SetViewport(*viewports[k])
        renderers[k].ResetCamera()
        camera.Zoom(1.2)

        render_window.AddRenderer(renderers[k])

    # Create the TextActors.
    text_actors = list()
    text_representations = list()
    text_widgets = list()
    text_scale_mode = {'none': 0, 'prop': 1, 'viewport': 2}
    text_property = vtkTextProperty(color=nc.GetColor3d('DarkSlateGray'), bold=True, italic=True, shadow=True,
                                    font_size=24)
    text_positions = {0: {'p': [0.35, 0.01, 0], 'p2': [0.20, 0.15, 0]},
                      1: {'p': [0.37, 0.01, 0], 'p2': [0.27, 0.15, 0]},
                      2: {'p': [0.3, 0.01, 0], 'p2': [0.31, 0.15, 0]}
                      }
    for k, v in text.items():
        text_actors.append(
            vtkTextActor(input=v, text_scale_mode=text_scale_mode['none'], text_property=text_property))

        # Create the text representation. Used for positioning the text actor.
        text_representations.append(vtkTextRepresentation(enforce_normalized_viewport_bounds=True))
        text_representations[k].GetPositionCoordinate().value = text_positions[k]['p']
        text_representations[k].GetPosition2Coordinate().value = text_positions[k]['p2']

        # Create the TextWidget
        text_widgets.append(vtkTextWidget(representation=text_representations[k], text_actor=text_actors[k]))
        text_widgets[k].SetDefaultRenderer(renderers[k])
        text_widgets[k].SetInteractor(render_window_interactor)
        text_widgets[k].SelectableOff()

    render_window.Render()

    for k in text.keys():
        text_widgets[k].On()

    render_window_interactor.Start()


if __name__ == '__main__':
    main()
