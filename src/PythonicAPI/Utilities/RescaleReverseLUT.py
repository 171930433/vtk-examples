#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingFreeType
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkElevationFilter
from vtkmodules.vtkFiltersSources import vtkCylinderSource
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkInteractionWidgets import (
    vtkScalarBarRepresentation,
    vtkScalarBarWidget,
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDiscretizableColorTransferFunction,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty
)


def main():
    colors = vtkNamedColors()
    colors.SetColor('ParaViewBkg', 82, 87, 110, 255)

    ren_win = vtkRenderWindow(size=(640 * 2, 480 * 2), window_name='RescaleReverseLUT')
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    style = vtkInteractorStyleTrackballCamera()
    iren.interactor_style = style

    # Define titles.
    titles = ['Original', 'Rescaled', 'Reversed', 'Rescaled and Reversed']
    text_positions = get_text_positions(titles, justification=TextProperty.Justification.VTK_TEXT_CENTERED, width=0.95,
                                        height=0.1)

    # Create text properties.
    text_property = vtkTextProperty(color=colors.GetColor3d('LightGoldenrodYellow'),
                                    bold=False, italic=False, shadow=False,
                                    font_size=24,
                                    justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                    vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_CENTERED)
    title_text_property = vtkTextProperty(color=colors.GetColor3d('LightGoldenrodYellow'),
                                          bold=True, italic=False, shadow=False,
                                          font_size=24, font_family_as_string='Courier',
                                          justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                          vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_CENTERED)
    label_text_property = vtkTextProperty(color=colors.GetColor3d('LightGoldenrodYellow'),
                                          bold=False, italic=False, shadow=False,
                                          font_size=24,
                                          justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                          vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_CENTERED)

    # Set up the scalar bar properties.
    scalar_bar_properties = list()
    for i in range(0, 4):
        scalar_bar_properties.append(ScalarBarProperties())

    # Define viewport ranges.
    viewports = {'Original': (0.0, 0.5, 0.5, 1.0),
                 'Rescaled': (0.0, 0.0, 0.5, 0.5),
                 'Reversed': (0.5, 0.5, 1.0, 1.0),
                 'Rescaled and Reversed': (0.5, 0.0, 1.0, 0.5),
                 }

    ctf = dict()
    ctf['Original'] = get_ctf(False)
    ctf['Rescaled'] = rescale_ctf(ctf['Original'], 0, 1, False)
    ctf['Reversed'] = rescale_ctf(ctf['Original'], *ctf['Original'].GetRange(), True)
    ctf['Rescaled and Reversed'] = rescale_ctf(ctf['Original'], 0, 1, True)

    cylinder = vtkCylinderSource(center=(0.0, 0.0, 0.0), resolution=6)
    bounds = cylinder.update().output.bounds

    renderers = list()
    text_widgets = list()
    sb_widgets = list()

    for title in titles:
        elevation_filter = vtkElevationFilter(scalar_range=(0, 1), low_point=(0, bounds[2], 0),
                                              high_point=(0, bounds[3], 0))
        mapper = vtkPolyDataMapper(lookup_table=ctf[title], color_mode=Mapper.ColorMode.VTK_COLOR_MODE_MAP_SCALARS,
                                   interpolate_scalars_before_mapping=True)
        cylinder >> elevation_filter >> mapper
        actor = vtkActor(mapper=mapper)

        ren = vtkRenderer(viewport=viewports[title], background=colors.GetColor3d('ParaViewBkg'))
        ren.AddActor(actor)

        # Add a title.
        text_actor = vtkTextActor(input=title,
                                  text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_VIEWPORT,
                                  text_property=text_property)

        # Create the text representation. Used for positioning the text actor.
        text_representation = vtkTextRepresentation(enforce_normalized_viewport_bounds=True)
        text_representation.GetPositionCoordinate().value = text_positions[title]['p']
        text_representation.GetPosition2Coordinate().value = text_positions[title]['p2']

        # Create the text widget, setting the default renderer and interactor.
        text_widgets.append(
            vtkTextWidget(representation=text_representation, text_actor=text_actor,
                          default_renderer=ren, interactor=iren, selectable=False))

        # Add a scalar bar.
        sb_properties = ScalarBarProperties()
        sb_properties.lut = ctf[title]
        sb_properties.orientation = True
        sb_properties.number_of_labels = 7
        sb_properties.position_v = {'point1': (0.75, 0.15), 'point2': (0.2, 0.75)}

        # Create the scalar bar, setting the default renderer and interactor.
        sb_widgets.append(make_scalar_bar_widget(sb_properties, title_text_property, label_text_property,
                                                 default_renderer=ren, interactor=iren))
        renderers.append(ren)

    for i in range(0, len(renderers)):
        ren_win.AddRenderer(renderers[i])
        text_widgets[i].On()
        sb_widgets[i].On()

    ren_win.Render()
    iren.Start()


def get_ctf(modern=False):
    """
    Generate the color transfer function.

    The seven colors corresponding to the colors that Isaac Newton labelled
        when dividing the spectrum of visible light in 1672 are used.

    The modern variant of these colors can be selected and used instead.

    See: [Rainbow](https://en.wikipedia.org/wiki/Rainbow)

    :param modern: Selects either Newton's original seven colors or modern version.
    :return: The color transfer function.
    """

    # name: Rainbow, creator: Andrew Maclean
    # interpolationspace: RGB, space: rgb
    # file name:

    ctf = vtkDiscretizableColorTransferFunction(color_space=ColorTransferFunction.ColorSpace.VTK_CTF_RGB,
                                                scale=ColorTransferFunction.Scale.VTK_CTF_LINEAR,
                                                nan_color=(0.5, 0.5, 0.5),
                                                below_range_color=(0.0, 0.0, 0.0), use_below_range_color=True,
                                                above_range_color=(1.0, 1.0, 1.0), use_above_range_color=True,
                                                number_of_values=7, discretize=True)

    if modern:
        ctf.AddRGBPoint(-1.0, 1.0, 0.0, 0.0)  # Red
        ctf.AddRGBPoint(-2.0 / 3.0, 1.0, 128.0 / 255.0, 0.0)  # Orange #ff8000
        ctf.AddRGBPoint(-1.0 / 3.0, 1.0, 1.0, 0.0)  # Yellow
        ctf.AddRGBPoint(0.0, 0.0, 1.0, 0.0)  # Green #00ff00
        ctf.AddRGBPoint(1.0 / 3.0, 0.0, 1.0, 1.0)  # Cyan
        ctf.AddRGBPoint(2.0 / 3.0, 0.0, 0.0, 1.0)  # Blue
        ctf.AddRGBPoint(1.0, 128.0 / 255.0, 0.0, 1.0)  # Violet #8000ff
    else:
        ctf.AddRGBPoint(-1.0, 1.0, 0.0, 0.0)  # Red
        ctf.AddRGBPoint(-2.0 / 3.0, 1.0, 165.0 / 255.0, 0.0)  # Orange #00a500
        ctf.AddRGBPoint(-1.0 / 3.0, 1.0, 1.0, 0.0)  # Yellow
        ctf.AddRGBPoint(0.0, 0.0, 125.0 / 255.0, 0.0)  # Green #008000
        ctf.AddRGBPoint(1.0 / 3.0, 0.0, 153.0 / 255.0, 1.0)  # Blue #0099ff
        ctf.AddRGBPoint(2.0 / 3.0, 68.0 / 255.0, 0, 153.0 / 255.0)  # Indigo #4400ff
        ctf.AddRGBPoint(1.0, 153.0 / 255.0, 0.0, 1.0)  # Violet #9900ff

    return ctf


def generate_new_ctf(old_ctf, new_x, new_rgb, reverse=False):
    """
    Generate a new color transfer function from the old one,
    adding in the new x and rgb values.

    :param old_ctf: The old color transfer function.
    :param new_x: The new color x-values.
    :param new_rgb: The color RGB values.
    :param reverse: If true, reverse the colors.
    :return: The new color transfer function.
    """
    new_ctf = vtkDiscretizableColorTransferFunction(color_space=old_ctf.color_space, scale=old_ctf.scale,
                                                    nan_color=old_ctf.nan_color,
                                                    number_of_values=len(new_x), discretize=True
                                                    )
    if not reverse:
        new_ctf.below_range_color = old_ctf.below_range_color
        new_ctf.use_below_range_color = old_ctf.use_below_range_color
        new_ctf.above_range_color = old_ctf.above_range_color
        new_ctf.use_above_range_color = old_ctf.use_above_range_color
    else:
        new_ctf.below_range_color = old_ctf.above_range_color
        new_ctf.use_below_range_color = old_ctf.use_above_range_color
        new_ctf.above_range_color = old_ctf.below_range_color
        new_ctf.use_above_range_color = old_ctf.use_below_range_color

    if not reverse:
        for i in range(0, len(new_x)):
            new_ctf.AddRGBPoint(new_x[i], *new_rgb[i])
    else:
        sz = len(new_x)
        for i in range(0, sz):
            j = sz - (i + 1)
            new_ctf.AddRGBPoint(new_x[i], *new_rgb[j])

    new_ctf.Build()
    return new_ctf


def rescale(values, new_min=0, new_max=1):
    """
    Rescale the values.

    See: https://stats.stackexchange.com/questions/25894/changing-the-scale-of-a-variable-to-0-100

    :param values: The values to be rescaled.
    :param new_min: The new minimum value.
    :param new_max: The new maximum value.
    :return: The rescaled values.
    """
    res = list()
    old_min, old_max = min(values), max(values)
    for v in values:
        new_v = (new_max - new_min) / (old_max - old_min) * (v - old_min) + new_min
        # new_v1 = (new_max - new_min) / (old_max - old_min) * (v - old_max) + new_max
        res.append(new_v)
    return res


def rescale_ctf(ctf, new_min=0, new_max=1, reverse=False):
    """
    Rescale and, optionally, reverse the colors in the color transfer function.

    :param ctf: The color transfer function to rescale.
    :param new_min: The new minimum value.
    :param new_max: The new maximum value.
    :param reverse: If true, reverse the colors.
    :return: The rescaled color transfer function.
    """
    if new_min > new_max:
        r0 = new_max
        r1 = new_min
    else:
        r0 = new_min
        r1 = new_max

    xv = list()
    rgbv = list()
    nv = [0] * 6
    for i in range(0, ctf.GetNumberOfValues()):
        ctf.GetNodeValue(i, nv)
        x = nv[0]
        rgb = nv[1:4]
        xv.append(x)
        rgbv.append(rgb)
    xvr = rescale(xv, r0, r1)

    return generate_new_ctf(ctf, xvr, rgbv, reverse=reverse)


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


class ScalarBarProperties:
    """
    The properties needed for scalar bars.
    """
    named_colors = vtkNamedColors()

    lut = None
    # These are in pixels
    maximum_dimensions = {'width': 100, 'height': 260}
    title_text = '',
    number_of_labels: int = 5
    # Orientation vertical=True, horizontal=False
    orientation: bool = True
    # Horizontal and vertical positioning
    position_v = {'point1': (0.85, 0.1), 'point2': (0.1, 0.7)}
    position_h = {'point1': (0.10, 0.1), 'point2': (0.7, 0.1)}


def make_scalar_bar_widget(scalar_bar_properties, title_text_property, label_text_property, default_renderer,
                           interactor):
    """
    Make a scalar bar widget.

    :param scalar_bar_properties: The lookup table, title name, maximum dimensions in pixels and position.
    :param title_text_property: The properties for the title.
    :param label_text_property: The properties for the labels.
    :param default_renderer: The default renderer.
    :param interactor: The vtkInteractor.
    :return: The scalar bar widget.
    """
    sb_actor = vtkScalarBarActor(lookup_table=scalar_bar_properties.lut, title=scalar_bar_properties.title_text,
                                 unconstrained_font_size=True, number_of_labels=scalar_bar_properties.number_of_labels,
                                 title_text_property=title_text_property, label_text_property=label_text_property
                                 )

    sb_rep = vtkScalarBarRepresentation(enforce_normalized_viewport_bounds=True,
                                        orientation=scalar_bar_properties.orientation)

    # Set the position.
    sb_rep.position_coordinate.SetCoordinateSystemToNormalizedViewport()
    sb_rep.position2_coordinate.SetCoordinateSystemToNormalizedViewport()
    if scalar_bar_properties.orientation:
        sb_rep.position_coordinate.value = scalar_bar_properties.position_v['point1']
        sb_rep.position2_coordinate.value = scalar_bar_properties.position_v['point2']
    else:
        sb_rep.position_coordinate.value = scalar_bar_properties.position_h['point1']
        sb_rep.position2_coordinate.value = scalar_bar_properties.position_h['point2']

    widget = vtkScalarBarWidget(representation=sb_rep, scalar_bar_actor=sb_actor, default_renderer=default_renderer,
                                interactor=interactor, enabled=True)

    return widget


@dataclass(frozen=True)
class ColorTransferFunction:
    @dataclass(frozen=True)
    class ColorSpace:
        VTK_CTF_RGB: int = 0
        VTK_CTF_HSV: int = 1
        VTK_CTF_LAB: int = 2
        VTK_CTF_DIVERGING: int = 3
        VTK_CTF_LAB_CIEDE2000: int = 4
        VTK_CTF_STEP: int = 5

    @dataclass(frozen=True)
    class Scale:
        VTK_CTF_LINEAR: int = 0
        VTK_CTF_LOG10: int = 1


@dataclass(frozen=True)
class Mapper:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_MODE_DEFAULT: int = 0
        VTK_COLOR_MODE_MAP_SCALARS: int = 1
        VTK_COLOR_MODE_DIRECT_SCALARS: int = 2

    @dataclass(frozen=True)
    class ResolveCoincidentTopology:
        VTK_RESOLVE_OFF: int = 0
        VTK_RESOLVE_POLYGON_OFFSET: int = 1
        VTK_RESOLVE_SHIFT_ZBUFFER: int = 2

    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_DEFAULT: int = 0
        VTK_SCALAR_MODE_USE_POINT_DATA: int = 1
        VTK_SCALAR_MODE_USE_CELL_DATA: int = 2
        VTK_SCALAR_MODE_USE_POINT_FIELD_DATA: int = 3
        VTK_SCALAR_MODE_USE_CELL_FIELD_DATA: int = 4
        VTK_SCALAR_MODE_USE_FIELD_DATA: int = 5


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
