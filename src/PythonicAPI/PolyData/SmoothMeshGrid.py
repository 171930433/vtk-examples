#!/usr/bin/env python3

from dataclasses import dataclass

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
    colors = vtkUnsignedCharArray(number_of_components=3)
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
    # Adding the geometry and topology to the polydata.
    triangle_poly_data = vtkPolyData(points=points, polys=triangles)
    triangle_poly_data.point_data.SetScalars(colors)

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
    text_property = vtkTextProperty(color=nc.GetColor3d('DarkSlateGray'), bold=True, italic=False, shadow=False,
                                    font_size=12, font_family_as_string='Courier',
                                    justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                    vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_CENTERED)

    text_positions = get_text_positions(list(text.values()), justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                        vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_BOTTOM
                                        )

    for k, v in text.items():
        text_actors.append(
            vtkTextActor(input=v, text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_NONE, text_property=text_property))

        # Create the text representation. Used for positioning the text actor.
        text_representations.append(vtkTextRepresentation(enforce_normalized_viewport_bounds=True))
        text_representations[k].GetPositionCoordinate().value = text_positions[v]['p']
        text_representations[k].GetPosition2Coordinate().value = text_positions[v]['p2']

        # Create the TextWidget
        text_widgets.append(
            vtkTextWidget(representation=text_representations[k], text_actor=text_actors[k],
                          default_renderer=renderers[k], interactor=render_window_interactor, selectable=False))

    render_window.Render()

    for k in text.keys():
        text_widgets[k].On()

    render_window_interactor.Start()


def get_text_positions(names, justification=0, vertical_justification=0, width=0.96, height=0.1):
    """
    Get viewport positioning information for a list of names.

    :param names: The list of names.
    :param justification: Horizontal justification of the text, default is left.
    :param vertical_justification: Vertical justification of the text, default is bottom.
    :param width: Width of the bounding_box of the text in screen coordinates.
    :param height: Height of the bounding_box of the text in screen coordinates.
    :return: A list of positioning information.
    """
    # The gap between the left or right edge of the screen and the text.
    dx = 0.02
    width = abs(width)
    if width > 0.96:
        width = 0.96

    y0 = 0.01
    height = abs(height)
    if height > 0.9:
        height = 0.9
    dy = height
    if vertical_justification == TextProperty.VerticalJustification.VTK_TEXT_TOP:
        y0 = 1.0 - (dy + y0)
        dy = height
    if vertical_justification == TextProperty.VerticalJustification.VTK_TEXT_CENTERED:
        y0 = 0.5 - (dy / 2.0 + y0)
        dy = height

    name_len_min = 0
    name_len_max = 0
    first = True
    for k in names:
        sz = len(k)
        if first:
            name_len_min = name_len_max = sz
            first = False
        else:
            name_len_min = min(name_len_min, sz)
            name_len_max = max(name_len_max, sz)
    text_positions = dict()
    for k in names:
        sz = len(k)
        delta_sz = width * sz / name_len_max
        if delta_sz > width:
            delta_sz = width

        if justification == TextProperty.Justification.VTK_TEXT_CENTERED:
            x0 = 0.5 - delta_sz / 2.0
        elif justification == TextProperty.Justification.VTK_TEXT_RIGHT:
            x0 = 1.0 - dx - delta_sz
        else:
            # Default is left justification.
            x0 = dx

        # For debugging!
        # print(
        #     f'{k:16s}: (x0, y0) = ({x0:3.2f}, {y0:3.2f}), (x1, y1) = ({x0 + delta_sz:3.2f}, {y0 + dy:3.2f})'
        #     f', width={delta_sz:3.2f}, height={dy:3.2f}')
        text_positions[k] = {'p': [x0, y0, 0], 'p2': [delta_sz, dy, 0]}

    return text_positions


@dataclass(frozen=True)
class TextProperty:
    @dataclass(frozen=True)
    class Justification:
        VTK_TEXT_LEFT: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_RIGHT: int = 2

    @dataclass(frozen=True)
    class VerticalJustification:
        VTK_TEXT_BOTTOM: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_TOP: int = 2


if __name__ == '__main__':
    main()
