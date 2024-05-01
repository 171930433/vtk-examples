#!/usr/bin/env python3

# Based on:
#  https://gitlab.kitware.com/vtk/vtk/-/blob/master/Rendering/Core/Testing/Cxx/TestGradientBackground.cxx?ref_type=heads
# See:
#  [New in VTK 9.3: Radial Gradient Background](https://www.kitware.com/new-in-vtk-9-3-radial-gradient-background/)

from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingFreeType
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkPolyData,
    vtkPolyLine
)
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkIOGeometry import (
    vtkBYUReader,
    vtkOBJReader,
    vtkSTLReader
)
from vtkmodules.vtkIOLegacy import vtkPolyDataReader
from vtkmodules.vtkIOPLY import vtkPLYReader
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
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
    vtkTextProperty,
    vtkViewport
)


def get_program_parameters(argv):
    import argparse
    description = 'Demonstrates the background shading options.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-f', '--file_name', default=None,
                        help='An optional file name, e.g. star-wars-vader-tie-fighter.obj.')
    args = parser.parse_args()
    return args.file_name


def main(fn):
    if fn:
        fp = Path(fn)
        if not fp.is_file():
            print(f'The path: {fp} does not exist.')
            return
    else:
        fp = None

    pd = read_poly_data(fp)
    if not pd:
        # Default to a cone if the path is empty.
        source = vtkConeSource(resolution=25, direction=(0, 1, 0), height=1)
        pd = source.update().output

    colors = vtkNamedColors()

    mapper = vtkPolyDataMapper()
    pd >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('Honeydew')
    actor.property.specular = 0.3
    actor.property.specular_power = 60.0

    # Here we select and name the colors.
    # Feel free to change colors.
    bottom_color = colors.GetColor3d('Gold')
    top_color = colors.GetColor3d('OrangeRed')
    left_color = colors.GetColor3d('Gold')
    right_color = colors.GetColor3d('OrangeRed')
    center_color = colors.GetColor3d('Gold')
    side_color = colors.GetColor3d('OrangeRed')
    corner_color = colors.GetColor3d('OrangeRed')

    # For each gradient specify the mode.
    modes = [
        vtkViewport.GradientModes.VTK_GRADIENT_RADIAL_VIEWPORT_FARTHEST_SIDE,
        vtkViewport.GradientModes.VTK_GRADIENT_RADIAL_VIEWPORT_FARTHEST_CORNER,
        vtkViewport.GradientModes.VTK_GRADIENT_VERTICAL,
        vtkViewport.GradientModes.VTK_GRADIENT_HORIZONTAL,
    ]

    viewport_titles = (
        'Radial Farthest Side',
        'Radial Farthest Corner',
        'Vertical',
        'Horizontal',
    )
    text_positions = get_text_positions(viewport_titles, justification=TextProperty.Justification.VTK_TEXT_CENTERED)

    text_property = vtkTextProperty(color=colors.GetColor3d('MidnightBlue'),
                                    bold=True, italic=False, shadow=False,
                                    font_size=12, font_family_as_string='Courier',
                                    justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                    vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_CENTERED)

    # Setup viewports for the renderers.
    x_grid_dimensions = 2
    y_grid_dimensions = 2
    width = 640
    height = 480

    # Create the renderer viewports.
    blank = len(viewport_titles)
    viewports = dict()
    VP_Params = namedtuple('VP_Params', ['viewport', 'border'])
    last_col = False
    last_row = False
    for row in range(0, y_grid_dimensions):
        if row == y_grid_dimensions - 1:
            last_row = True
        for col in range(0, x_grid_dimensions):
            if col == x_grid_dimensions - 1:
                last_col = True
            index = row * x_grid_dimensions + col
            viewport = (
                col / x_grid_dimensions,
                (y_grid_dimensions - (row + 1)) / y_grid_dimensions,
                (col + 1) / x_grid_dimensions,
                (y_grid_dimensions - row) / y_grid_dimensions,
            )

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
                viewports[viewport_titles[index]] = vp_params
            else:
                viewports[index] = vp_params

    ren_win = vtkRenderWindow(size=(width, height), window_name='GradientBackground')

    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)
    style = vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)

    text_widgets = list()
    for i, viewport_title in enumerate(viewport_titles):
        # pth = path / file
        # Create a renderer.
        viewport = viewports[viewport_title].viewport
        border = viewports[viewport_title].border
        renderer = vtkRenderer(gradient_background=True, gradient_mode=modes[i], viewport=viewport)
        draw_viewport_border(renderer, border=border, color=colors.GetColor3d('border_color'), line_width=4)
        if i == 1:
            # Horizontal
            renderer.background = left_color
            renderer.background2 = right_color
        elif i == 2:
            # Radial Farthest Side
            renderer.background = center_color
            renderer.background2 = side_color
        elif i == 3:
            # Radial Farthest Corner
            renderer.background = center_color
            renderer.background2 = corner_color
        else:
            # Vertical
            renderer.background = bottom_color
            renderer.background2 = top_color

        renderer.AddActor(actor)

        # Create the text actor and representation.
        text_actor = vtkTextActor(input=viewport_title, text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_NONE,
                                  text_property=text_property)

        # Create the text representation. Used for positioning the text actor.
        text_representation = vtkTextRepresentation(enforce_normalized_viewport_bounds=True)
        text_representation.GetPositionCoordinate().value = text_positions[viewport_title]['p']
        text_representation.GetPosition2Coordinate().value = text_positions[viewport_title]['p2']

        # Create the text widget, setting the default renderer and interactor.
        text_widget = vtkTextWidget(representation=text_representation, text_actor=text_actor,
                                    default_renderer=renderer, interactor=iren, selectable=False)
        text_widgets.append(text_widget)
        # else:
        #     print(f'Nonexistent file: {pth}')
        # renderers.append(renderer)
        ren_win.AddRenderer(renderer)

    for i in range(blank, x_grid_dimensions * y_grid_dimensions):
        viewport = viewports[i].viewport
        border = viewports[i].border
        renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'), viewport=viewport)
        draw_viewport_border(renderer, border=border, color=colors.GetColor3d('border_color'), line_width=4)
        ren_win.AddRenderer(renderer)

    for text_widget in text_widgets:
        text_widget.On()

    ren_win.Render()
    iren.UpdateSize(width * 2, height * 2)
    iren.Start()


def read_poly_data(file_name):
    if not file_name:
        print(f'No file name.')
        return None

    valid_suffixes = ['.g', '.obj', '.stl', '.ply', '.vtk', '.vtp']
    path = Path(file_name)
    ext = None
    if path.suffix:
        ext = path.suffix.lower()
    if path.suffix not in valid_suffixes:
        print(f'No reader for this file suffix: {ext}')
        return None

    reader = None
    if ext == '.ply':
        reader = vtkPLYReader(file_name=file_name)
    elif ext == '.vtp':
        reader = vtkXMLPolyDataReader(file_name=file_name)
    elif ext == '.obj':
        reader = vtkOBJReader(file_name=file_name)
    elif ext == '.stl':
        reader = vtkSTLReader(file_name=file_name)
    elif ext == '.vtk':
        reader = vtkPolyDataReader(file_name=file_name)
    elif ext == '.g':
        reader = vtkBYUReader(file_name=file_name)

    if reader:
        reader.update()
        poly_data = reader.output
        return poly_data
    else:
        return None


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
        lines.point_ids.number_of_ids = number_of_points
        for i in range(0, number_of_points):
            lines.point_ids.id = (i, i)

        cells = vtkCellArray()
        cells.InsertNextCell(lines)

        # Make the polydata and return.
        return vtkPolyData(points=points, lines=cells)

    # Use normalized viewport coordinates since
    # they are independent of window size.
    coordinate = vtkCoordinate()
    coordinate.SetCoordinateSystemToNormalizedViewport()
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
    import sys

    file_path = get_program_parameters(sys.argv)
    main(file_path)
