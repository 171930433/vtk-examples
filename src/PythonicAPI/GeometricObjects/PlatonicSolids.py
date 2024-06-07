#!/usr/bin/env python3

from collections import namedtuple
from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingFreeType
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkLookupTable,
    vtkPoints
)
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkPolyData,
    vtkPolyLine
)
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
from vtkmodules.vtkFiltersSources import vtkPlatonicSolidSource
from vtkmodules.vtkInteractionWidgets import (
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkActor2D,
    vtkCoordinate,
    vtkPolyDataMapper,
    vtkPolyDataMapper2D,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty
)


def main():
    colors = vtkNamedColors()

    name_orientation = get_name_orientation()
    lut = get_platonic_lut()

    # Set up the viewports.
    x_grid_dimensions = 3
    y_grid_dimensions = 2
    renderer_size = 300
    size = (x_grid_dimensions * renderer_size, y_grid_dimensions * renderer_size)

    viewports = dict()
    VP_Params = namedtuple('VP_Params', ['viewport', 'border'])
    last_col = False
    last_row = False
    blank = len(name_orientation)

    for row in range(0, y_grid_dimensions):
        if row == y_grid_dimensions - 1:
            last_row = True
        for col in range(0, x_grid_dimensions):
            if col == x_grid_dimensions - 1:
                last_col = True
            index = row * x_grid_dimensions + col
            # (xmin, ymin, xmax, ymax)
            viewport = (float(col) / x_grid_dimensions,
                        float(y_grid_dimensions - (row + 1)) / y_grid_dimensions,
                        float(col + 1) / x_grid_dimensions,
                        float(y_grid_dimensions - row) / y_grid_dimensions)

            if last_row and last_col:
                border = ViewPort.Border.TOP_LEFT_BOTTOM_RIGHT
                last_row = False
                last_col = False
            elif last_col:
                border = ViewPort.Border.RIGHT_TOP_LEFT
                last_col = False
            elif last_row:
                border = ViewPort.Border.TOP_LEFT_BOTTOM
            else:
                border = ViewPort.Border.TOP_LEFT
            vp_params = VP_Params(viewport, border)
            if index < blank:
                viewports[name_orientation[index].name] = vp_params
            else:
                viewports[index] = vp_params

    # Create the render window and interactor.
    ren_win = vtkRenderWindow(size=size, window_name='PlatonicSolids')

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Create one text property for all.
    text_property = vtkTextProperty(color=colors.GetColor3d('AliceBlue'), bold=True, italic=True,
                                    shadow=True, font_family_as_string='Courier',
                                    font_size=16, justification=TextProperty.Justification.VTK_TEXT_CENTERED)

    titles = list()
    for n in name_orientation:
        titles.append(n.name)
    # Position text according to its length and centered in the viewport.
    text_positions = get_text_positions(titles, justification=TextProperty.Justification.VTK_TEXT_CENTERED)

    text_representations = list()
    text_actors = list()
    text_widgets = list()
    renderers = list()

    # Create and link the mappers actors and renderers together.
    for i in range(0, len(name_orientation)):
        viewport = viewports[name_orientation[i].name].viewport
        border = viewports[name_orientation[i].name].border
        renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'), viewport=viewport)
        draw_viewport_border(renderer, border=border, color=colors.GetColor3d('Yellow'), line_width=4)

        platonic_solid = vtkPlatonicSolidSource(solid_type=i)
        mapper = vtkPolyDataMapper(lookup_table=lut, scalar_range=(0, 19))
        platonic_solid >> mapper
        actor = vtkActor(mapper=mapper)
        renderer.AddActor(actor)

        # Create the text actor and representation.
        text_actors.append(
            vtkTextActor(input=name_orientation[i].name,
                         text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_NONE,
                         text_property=text_property))

        # Create the text representation. Used for positioning the text actor.
        text_representations.append(vtkTextRepresentation(enforce_normalized_viewport_bounds=True))
        text_representations[i].GetPositionCoordinate().value = text_positions[name_orientation[i].name]['p']
        text_representations[i].GetPosition2Coordinate().value = text_positions[name_orientation[i].name]['p2']

        # Create the text widget, setting the default renderer and interactor.
        text_widgets.append(
            vtkTextWidget(representation=text_representations[i], text_actor=text_actors[i],
                          default_renderer=renderer, interactor=iren, selectable=False))

        # Orient the view.
        renderer.ResetCamera()
        renderer.active_camera.Azimuth(name_orientation[i].azimuth)
        renderer.active_camera.Elevation(name_orientation[i].elevation)
        renderer.active_camera.Zoom(name_orientation[i].zoom)
        renderer.ResetCameraClippingRange()

        renderers.append(renderer)
        ren_win.AddRenderer(renderers[i])

    for i in range(blank, x_grid_dimensions * y_grid_dimensions):
        viewport = viewports[i].viewport
        border = viewports[i].border
        renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'), viewport=viewport)
        draw_viewport_border(renderer, border=border, color=colors.GetColor3d('Yellow'), line_width=4)
        ren_win.AddRenderer(renderer)

    for i in range(0, len(name_orientation)):
        text_widgets[i].On()

    iren.Initialize()
    ren_win.Render()
    iren.Start()


def get_name_orientation():
    """
    Get the platonic solid names and initial orientations.

    :return: The solids and their initial orientations.
    """

    # [[name, azimuth, elevation, zoom] ...]
    res = [['Tetrahedron', 45.0, 30.0, 1.0],
           ['Cube', -60.0, 45.0, 0.8],
           ['Octahedron', -15.0, 10.0, 1.0],
           ['Icosahedron', 4.5, 18.0, 1.0],
           ['Dodecahedron', 171.0, 22.0, 1.0]]

    platonic_solids = namedtuple('platonic_solids', ('name', 'azimuth', 'elevation', 'zoom'))
    # Convert res to a list of named tuples.
    res = [platonic_solids(*row) for row in res]
    return res


def get_platonic_lut():
    """
    Get a specialised lookup table for the platonic solids.

    Since each face of a vtkPlatonicSolidSource has a different
    cell scalar, we create a lookup table with a different colour
    for each face.
    The colors have been carefully chosen so that adjacent cells
    are colored distinctly.

    :return: The lookup table.
    """
    lut = vtkLookupTable(number_of_table_values=20, table_range=(0.0, 19.0))
    # lut.SetNumberOfTableValues(20)
    # lut.SetTableRange(0.0, 19.0)
    lut.Build()
    lut.SetTableValue(0, 0.1, 0.1, 0.1)
    lut.SetTableValue(1, 0, 0, 1)
    lut.SetTableValue(2, 0, 1, 0)
    lut.SetTableValue(3, 0, 1, 1)
    lut.SetTableValue(4, 1, 0, 0)
    lut.SetTableValue(5, 1, 0, 1)
    lut.SetTableValue(6, 1, 1, 0)
    lut.SetTableValue(7, 0.9, 0.7, 0.9)
    lut.SetTableValue(8, 0.5, 0.5, 0.5)
    lut.SetTableValue(9, 0.0, 0.0, 0.7)
    lut.SetTableValue(10, 0.5, 0.7, 0.5)
    lut.SetTableValue(11, 0, 0.7, 0.7)
    lut.SetTableValue(12, 0.7, 0, 0)
    lut.SetTableValue(13, 0.7, 0, 0.7)
    lut.SetTableValue(14, 0.7, 0.7, 0)
    lut.SetTableValue(15, 0, 0, 0.4)
    lut.SetTableValue(16, 0, 0.4, 0)
    lut.SetTableValue(17, 0, 0.4, 0.4)
    lut.SetTableValue(18, 0.4, 0, 0)
    lut.SetTableValue(19, 0.4, 0, 0.4)
    return lut


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


def draw_viewport_border(renderer, border, color=(0, 0, 0), line_width=2):
    """
    Draw a border around the viewport of a renderer.

    :param renderer: The renderer.
    :param border: The border to draw, it must be one of the constants in ViewPort.Border.
    :param color: The color.
    :param line_width: The line width of the border.
    :return:
    """

    def generate_border_lines(border_type):
        """
        Generate the lines for the border.

        :param border_type:  The border type to draw, it must be one of the constants in ViewPort.Border
        :return: The points and lines.
        """
        if border_type >= ViewPort.Border.NUMBER_OF_BORDER_TYPES:
            print('Not a valid border type.')
            return None

        # Points start at upper right and proceed anti-clockwise.
        pts = (
            (1, 1, 0),
            (0, 1, 0),
            (0, 0, 0),
            (1, 0, 0),
            (1, 1, 0),
        )
        pt_orders = {
            ViewPort.Border.TOP: (0, 1),
            ViewPort.Border.LEFT: (1, 2),
            ViewPort.Border.BOTTOM: (2, 3),
            ViewPort.Border.RIGHT: (3, 4),
            ViewPort.Border.LEFT_BOTTOM: (1, 2, 3),
            ViewPort.Border.BOTTOM_RIGHT: (2, 3, 4),
            ViewPort.Border.RIGHT_TOP: (3, 4, 1),
            ViewPort.Border.RIGHT_TOP_LEFT: (3, 4, 1, 2),
            ViewPort.Border.TOP_LEFT: (0, 1, 2),
            ViewPort.Border.TOP_LEFT_BOTTOM: (0, 1, 2, 3),
            ViewPort.Border.TOP_LEFT_BOTTOM_RIGHT: (0, 1, 2, 3, 4)
        }
        pt_order = pt_orders[border_type]
        number_of_points = len(pt_order)
        points = vtkPoints(number_of_points=number_of_points)
        i = 0
        for pt_id in pt_order:
            points.InsertPoint(i, *pts[pt_id])
            i += 1

        lines = vtkPolyLine()
        lines.point_ids.SetNumberOfIds(number_of_points)
        for i in range(0, number_of_points):
            lines.point_ids.id = (i, i)

        cells = vtkCellArray()
        cells.InsertNextCell(lines)

        # Make the polydata and return.
        return vtkPolyData(points=points, lines=cells)

    # Use normalized viewport coordinates since
    # they are independent of window size.
    coordinate = vtkCoordinate(coordinate_system=Coordinate.CoordinateSystem.VTK_NORMALIZED_VIEWPORT)
    poly = vtkAppendPolyData()
    if border == ViewPort.Border.TOP_BOTTOM:
        (
            generate_border_lines(ViewPort.Border.TOP),
            generate_border_lines(ViewPort.Border.BOTTOM)
        ) >> poly
    elif border == ViewPort.Border.LEFT_RIGHT:
        (
            generate_border_lines(ViewPort.Border.LEFT),
            generate_border_lines(ViewPort.Border.RIGHT)
        ) >> poly
    else:
        generate_border_lines(border) >> poly

    mapper = vtkPolyDataMapper2D(transform_coordinate=coordinate)
    poly >> mapper
    actor = vtkActor2D(mapper=mapper)
    actor.property.color = color
    # Line width should be at least 2 to be visible at the extremes.
    actor.property.line_width = line_width

    renderer.AddViewProp(actor)


@dataclass(frozen=True)
class Coordinate:
    @dataclass(frozen=True)
    class CoordinateSystem:
        VTK_DISPLAY: int = 0
        VTK_NORMALIZED_DISPLAY: int = 1
        VTK_VIEWPORT: int = 2
        VTK_NORMALIZED_VIEWPORT: int = 3
        VTK_VIEW: int = 4
        VTK_POSE: int = 5
        VTK_WORLD: int = 6
        VTK_USERDEFINED: int = 7


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


@dataclass(frozen=True)
class ViewPort:
    @dataclass(frozen=True)
    class Border:
        TOP: int = 0
        LEFT: int = 1
        BOTTOM: int = 2
        RIGHT: int = 3
        LEFT_BOTTOM: int = 4
        BOTTOM_RIGHT: int = 5
        RIGHT_TOP: int = 6
        RIGHT_TOP_LEFT: int = 7
        TOP_LEFT: int = 8
        TOP_LEFT_BOTTOM: int = 9
        TOP_LEFT_BOTTOM_RIGHT: int = 10
        TOP_BOTTOM: int = 11
        LEFT_RIGHT: int = 12
        NUMBER_OF_BORDER_TYPES: int = 13


if __name__ == '__main__':
    main()
