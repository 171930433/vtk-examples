#!/usr/bin/env python3

from collections import namedtuple
from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkPolyData, vtkPolyLine
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
from vtkmodules.vtkIOImage import vtkImageReader2Factory
from vtkmodules.vtkImagingMorphological import (
    vtkImageDilateErode3D,
    vtkImageSeedConnectivity
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleImage
from vtkmodules.vtkInteractionWidgets import (
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingCore import (
    vtkActor2D,
    vtkCoordinate,
    vtkImageActor,
    vtkImageProperty,
    vtkPolyDataMapper2D,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkTextActor,
    vtkTextProperty
)


def get_program_parameters():
    import argparse
    description = 'Demonstrate various binary filters that can alter the shape of segmented regions.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='original_actor.')
    args = parser.parse_args()
    return args.filename


def main():
    colors = vtkNamedColors()

    file_name = get_program_parameters()

    # Read the image.
    reader = vtkImageReader2Factory().CreateImageReader2(file_name)
    reader.file_name = file_name

    kernel_size = (31, 31, 1)

    img_property = vtkImageProperty(interpolation_type=ImageProperty.InterpolationType.VTK_NEAREST_INTERPOLATION)

    # Dilate
    dilate = vtkImageDilateErode3D(dilate_value=0, erode_value=255, kernel_size=kernel_size)

    # Erode
    erode = vtkImageDilateErode3D(dilate_value=255, erode_value=0, kernel_size=kernel_size)

    # Opening - dilate then erode.
    dilate1 = vtkImageDilateErode3D(dilate_value=0, erode_value=255, kernel_size=kernel_size)
    erode1 = vtkImageDilateErode3D(dilate_value=255, erode_value=0, kernel_size=kernel_size)

    # Closing - erode then dilate.
    erode2 = vtkImageDilateErode3D(dilate_value=255, erode_value=0, kernel_size=kernel_size)
    dilate2 = vtkImageDilateErode3D(dilate_value=0, erode_value=255, kernel_size=kernel_size)

    # Connectivity
    con = vtkImageSeedConnectivity(input_connect_value=0, output_connected_value=0, output_unconnected_value=255)
    con.AddSeed(300, 200)

    # Link the actors to the pipelines.
    actors = dict()

    actors['Original'] = vtkImageActor(property=img_property)
    reader >> actors['Original'].mapper

    actors['Connectivity'] = vtkImageActor(property=img_property)
    reader >> con >> actors['Connectivity'].mapper

    actors['Erosion'] = vtkImageActor(property=img_property)
    reader >> erode >> actors['Erosion'].mapper

    actors['Dilation'] = vtkImageActor(property=img_property)
    reader >> dilate >> actors['Dilation'].mapper

    actors['Opening'] = vtkImageActor(property=img_property)
    reader >> erode2 >> dilate2 >> actors['Opening'].mapper

    actors['Closing'] = vtkImageActor(property=img_property)
    reader >> dilate1 >> erode1 >> actors['Closing'].mapper

    keys = list(actors.keys())

    # Define the size of the grid that will hold the objects.
    grid_cols = 2
    grid_rows = 3
    # Define side length (in pixels) of each renderer rectangle.
    col_size = 595
    row_size = 428
    size = (col_size * grid_cols, row_size * grid_rows)
    ren_win = vtkRenderWindow(size=size, window_name='MorphologyComparison')

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win
    style = vtkInteractorStyleImage()
    iren.interactor_stype = style

    viewports = dict()
    VP_Params = namedtuple('VP_Params', ['viewport', 'border'])
    last_col = False
    last_row = False
    for row in range(0, grid_rows):
        if row == grid_rows - 1:
            last_row = True
        for col in range(0, grid_cols):
            if col == grid_cols - 1:
                last_col = True
            index = row * grid_cols + col
            # (x_min, y_min, x_max, y_max)
            viewport = (
                float(col) / grid_cols,
                float(grid_rows - row - 1) / grid_rows,
                float(col + 1) / grid_cols,
                float(grid_rows - row) / grid_rows
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
            viewports[keys[index]] = vp_params

    # Add the actors to the renderers.
    renderers = dict()
    for k in actors.keys():
        renderers[k] = vtkRenderer(background=colors.GetColor3d("LightSlateGray"), viewport=viewports[k].viewport)
        renderers[k].AddActor(actors[k])
        ren_win.AddRenderer(renderers[k])

    # Create one text property for all.
    text_property = vtkTextProperty(color=colors.GetColor3d('LightGoldenrodYellow'), bold=True, italic=True,
                                    shadow=True, font_family_as_string='Courier',
                                    font_size=16, justification=TextProperty.Justification.VTK_TEXT_CENTERED)
    text_positions = get_text_positions(keys, justification=TextProperty.Justification.VTK_TEXT_CENTERED, width=0.5)

    # Create the text widgets.
    text_representations = list()
    text_actors = list()
    text_widgets = list()
    index = 0
    for k in actors.keys():
        # Create the text actor and representation.
        text_actors.append(
            vtkTextActor(input=k,
                         text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_NONE,
                         text_property=text_property))

        # Create the text representation. Used for positioning the text actor.
        text_representations.append(vtkTextRepresentation(enforce_normalized_viewport_bounds=True))
        text_representations[index].GetPositionCoordinate().value = text_positions[k]['p']
        text_representations[index].GetPosition2Coordinate().value = text_positions[k]['p2']

        # Create the text widget, setting the default renderer and interactor.
        text_widgets.append(
            vtkTextWidget(representation=text_representations[index], text_actor=text_actors[index],
                          default_renderer=renderers[k], interactor=iren, selectable=False))
        index += 1

    # Draw a line around the viewport of each renderer.
    for k in actors.keys():
        border = viewports[k].border
        draw_viewport_border(renderers[k], border=border, color=colors.GetColor3d('Yellow'), line_width=4)

    # The renderers share one camera.
    ren_win.Render()
    renderers['Original'].GetActiveCamera().Dolly(1.35)
    renderers['Original'].ResetCameraClippingRange()
    camera = renderers['Original'].GetActiveCamera()
    for k in actors.keys():
        if k != 'Original':
            renderers[k].SetActiveCamera(camera)
    ren_win.Render()

    for i in range(0, len(text_widgets)):
        text_widgets[i].On()

    iren.Initialize()
    iren.Start()


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
class ImageProperty:
    @dataclass(frozen=True)
    class InterpolationType:
        VTK_NEAREST_INTERPOLATION: int = 0
        VTK_LINEAR_INTERPOLATION: int = 1
        VTK_CUBIC_INTERPOLATION: int = 2


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
