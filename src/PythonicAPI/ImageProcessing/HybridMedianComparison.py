#!/usr/bin/env python3

from collections import namedtuple
from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.util.execution_model import select_ports
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkPolyData, vtkPolyLine
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
from vtkmodules.vtkIOImage import vtkImageReader2Factory
from vtkmodules.vtkImagingCore import (
    vtkImageCast,
    vtkImageThreshold
)
from vtkmodules.vtkImagingGeneral import (
    vtkImageHybridMedian2D,
    vtkImageMedian3D
)
from vtkmodules.vtkImagingMath import vtkImageMathematics
from vtkmodules.vtkImagingSources import vtkImageNoiseSource
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
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty
)


def get_program_parameters():
    import argparse
    description = 'Comparison of median and hybrid-median filters.'
    epilogue = '''
    The hybrid filter preserves corners and thin lines, better than the median filter.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='TestPattern.png.')
    args = parser.parse_args()
    return args.filename


def main():
    colors = vtkNamedColors()

    file_name = get_program_parameters()

    # Read the image.
    reader = vtkImageReader2Factory().CreateImageReader2(file_name)
    reader.file_name = file_name
    reader.update()

    scalar_range = reader.output.point_data.scalars.range
    extent = reader.output.extent
    middle_slice = (extent[5] - extent[4]) // 2
    print(f'Range: {scalar_range}, middle slice: {middle_slice}')

    # Work with double images.
    cast = vtkImageCast(output_scalar_type=ImageCast.OutputScalarType.VTK_DOUBLE)

    original_data = vtkImageData()
    original_data.DeepCopy((reader >> cast).update().output)

    noisy_data = add_shot_noise(original_data, 2000.0, 0.1, reader.GetOutput().GetExtent())

    median = vtkImageMedian3D(input_data=noisy_data, kernel_size=(5, 5, 1))

    hybrid_median1 = vtkImageHybridMedian2D(input_data=noisy_data)
    hybrid_median = vtkImageHybridMedian2D()
    hybrid_median1 >> hybrid_median

    color_window = (scalar_range[1] - scalar_range[0]) * 0.8
    color_level = color_window / 2

    image_property = vtkImageProperty(color_window=color_window, color_level=color_level,
                                      interpolation_type=ImageProperty.InterpolationType.VTK_NEAREST_INTERPOLATION)

    display_extent = reader.data_extent[:4] + (middle_slice, middle_slice)

    # Link the actors to the pipelines.
    actors = dict()

    actors['Original'] = vtkImageActor(property=image_property, display_extent=display_extent)
    actors['Original'].mapper.input_data = original_data

    actors['Noisy'] = vtkImageActor(property=image_property, display_extent=actors['Original'].display_extent)
    actors['Noisy'].mapper.input_data = noisy_data

    actors['Hybrid Median'] = vtkImageActor(property=image_property, display_extent=actors['Original'].display_extent)
    hybrid_median >> actors['Hybrid Median'].mapper

    actors['Median'] = vtkImageActor(property=image_property, display_extent=actors['Original'].display_extent)
    median >> actors['Median'].mapper

    keys = list(actors.keys())

    # Define the size of the grid that will hold the objects.
    grid_cols = 2
    grid_rows = 2
    # Define side length (in pixels) of each renderer rectangle.
    col_size = 255
    row_size = 255
    size = (col_size * grid_cols, row_size * grid_rows)
    ren_win = vtkRenderWindow(size=size, window_name='HybridMedianComparison')

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win
    style = vtkInteractorStyleImage()
    iren.interactor_style = style

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
    renderers['Original'].active_camera.Dolly(1.1)
    renderers['Original'].ResetCameraClippingRange()
    camera = renderers['Original'].active_camera
    for k in actors.keys():
        if k != 'Original':
            renderers[k].SetActiveCamera(camera)
    ren_win.Render()

    for i in range(0, len(text_widgets)):
        text_widgets[i].On()

    iren.Initialize()
    iren.Start()


def add_shot_noise(input_image, noise_amplitude, noise_fraction, extent):
    shot_noise_source = vtkImageNoiseSource(whole_extent=extent, minimum=0.0, maximum=1.0)

    shot_noise_thresh1 = vtkImageThreshold(in_value=0, out_value=noise_amplitude)
    shot_noise_thresh1.ThresholdByLower(1.0 - noise_fraction)
    shot_noise_source >> shot_noise_thresh1

    shot_noise_thresh2 = vtkImageThreshold(in_value=1.0 - noise_amplitude, out_value=0.0)
    shot_noise_thresh2.ThresholdByLower(noise_fraction)
    shot_noise_source >> shot_noise_thresh2

    shot_noise = vtkImageMathematics(operation=ImageMathematics.Operation.VTK_ADD)
    shot_noise_thresh1 >> select_ports(shot_noise, 0)
    shot_noise_thresh2 >> select_ports(shot_noise, 1)

    add = vtkImageMathematics(operation=ImageMathematics.Operation.VTK_ADD)
    input_image >> select_ports(add, 0)
    shot_noise >> select_ports(add, 1)

    add.update()

    output_image = vtkImageData()
    output_image.DeepCopy(add.GetOutput())
    return output_image


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
class ImageCast:
    @dataclass(frozen=True)
    class OutputScalarType:
        VTK_CHAR: int = 2
        VTK_UNSIGNED_CHAR: int = 3
        VTK_SHORT: int = 4
        VTK_UNSIGNED_SHORT: int = 5
        VTK_INT: int = 6
        VTK_UNSIGNED_INT: int = 7
        VTK_LONG: int = 8
        VTK_UNSIGNED_LONG: int = 9
        VTK_FLOAT: int = 10
        VTK_DOUBLE: int = 11


@dataclass(frozen=True)
class ImageMathematics:
    @dataclass(frozen=True)
    class Operation:
        VTK_ADD: int = 0
        VTK_SUBTRACT: int = 1
        VTK_MULTIPLY: int = 2
        VTK_DIVIDE: int = 3
        VTK_INVERT: int = 4
        VTK_SIN: int = 5
        VTK_COS: int = 6
        VTK_EXP: int = 7
        VTK_LOG: int = 8
        VTK_ABS: int = 9
        VTK_SQR: int = 10
        VTK_SQRT: int = 11
        VTK_MIN: int = 12
        VTK_MAX: int = 13
        VTK_ATAN: int = 14
        VTK_ATAN2: int = 15
        VTK_MULTIPLYBYK: int = 16
        VTK_ADDC: int = 17
        VTK_CONJUGATE: int = 18
        VTK_COMPLEX_MULTIPLY: int = 19
        VTK_REPLACECBYK: int = 20


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
