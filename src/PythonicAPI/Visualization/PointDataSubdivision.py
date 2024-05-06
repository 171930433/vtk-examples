#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import (
    vtkColorSeries,
    vtkNamedColors
)
from vtkmodules.vtkCommonComputationalGeometry import (
    vtkParametricBoy,
    vtkParametricEllipsoid,
    vtkParametricMobius,
    vtkParametricRandomHills,
    vtkParametricTorus
)
from vtkmodules.vtkCommonDataModel import vtkColor3ub
from vtkmodules.vtkFiltersCore import (
    vtkCleanPolyData,
    vtkElevationFilter,
    vtkGlyph3D,
    vtkMaskPoints,
    vtkPolyDataNormals,
    vtkTriangleFilter
)
from vtkmodules.vtkFiltersHybrid import vtkRenderLargeImage
from vtkmodules.vtkFiltersModeling import (
    vtkButterflySubdivisionFilter,
    vtkLinearSubdivisionFilter
)
from vtkmodules.vtkFiltersSources import (
    vtkArrowSource,
    vtkConeSource,
    vtkParametricFunctionSource,
    vtkSphereSource,
    vtkSuperquadricSource
)
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkInteractionWidgets import (
    vtkOrientationMarkerWidget,
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkColorTransferFunction,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty
)

nc = vtkNamedColors()


def get_program_parameters():
    import argparse
    description = 'Demonstrates point data subdivision with the glyphing of normals on the surface.'
    epilogue = '''
        This program takes a surface and displays three surfaces.

        The first surface is the original surface and the second and third surfaces have
         had linear and butterfly interpolation applied respectively.
        The user can control the object to use, normals generation, type of shading
         and number of points to use for the normals.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)
    parser.add_argument('sourceToUse', help='The surface to use.', nargs='?', default='Boy')
    parser.add_argument('-g', '--glyphPoints', help='Number of points to be used for glyphing.', nargs='?', default=50,
                        type=int)
    parser.add_argument('--no-normals', help='Do not display normals.', dest='displayNormals', action='store_false')
    parser.add_argument('--no-gouraud', help='Use flat interpolation. Gouraud interpolation is used by default.',
                        dest='gouraudInterpolation', action='store_false')
    parser.set_defaults(displayNormals=True)
    parser.set_defaults(gouraudInterpolation=True)
    args = parser.parse_args()
    return args.sourceToUse, args.displayNormals, args.gouraudInterpolation, args.glyphPoints


class Sources:
    """
    This class acts as a storage vehicle for the various sources.

    If you add more sources, you may need to provide one or all of these filters:
     - A Triangle filter
     - A Normal filter
     - An elevation filter.
     - A CleanPolyData filter.
     - For parametric sources, we may need to apply one of both of JoinUOff() or JoinVOff().

    Use the representative sources provided here as templates.
    """

    def __init__(self):
        # If you add more sources update this dictionary.
        self.sources = {'parametric torus': self.parametric_torus_source(),
                        'parametric ellipsoid': self.ellipsoid_source(),
                        'boy': self.boy_source(), 'sphere': self.sphere_source(), 'mobius': self.mobius_source(),
                        'cone': self.cone_source(), 'random hills': self.parametric_random_hills(),
                        'superquadric': self.superquadric_source()}

    @staticmethod
    def parametric_torus_source():
        torus = vtkParametricTorus(join_u=False, join_v=False)
        source = vtkParametricFunctionSource(parametric_function=torus)
        source.SetScalarModeToZ()
        return source

    @staticmethod
    def ellipsoid_source():
        ellipsoid = vtkParametricEllipsoid(x_radius=0.5, y_radius=1.0, z_radius=2.0,
                                           join_u=False, join_v=False)
        source = vtkParametricFunctionSource(parametric_function=ellipsoid)  #
        source.SetScalarModeToZ()
        return source

    @staticmethod
    def boy_source():
        boy = vtkParametricBoy(join_u=False, join_v=False)
        source = vtkParametricFunctionSource(parametric_function=boy)
        source.SetScalarModeToZ()
        return source

    @staticmethod
    def mobius_source():
        mobius = vtkParametricMobius(radius=2.0, minimum_v=-0.5, maximum_v=0.5,
                                     join_u=False, join_v=False)
        source = vtkParametricFunctionSource(parametric_function=mobius)
        source.SetScalarModeToX()
        return source

    @staticmethod
    def parametric_random_hills():
        random_hills = vtkParametricRandomHills(random_seed=1, number_of_hills=30)
        source = vtkParametricFunctionSource(parametric_function=random_hills,
                                             u_resolution=10, v_resolution=10)
        source.SetScalarModeToZ()
        return source

    @staticmethod
    def sphere_source():
        sphere = vtkSphereSource(phi_resolution=11, theta_resolution=11)
        sphere_bounds = sphere.update().output.bounds

        elev = vtkElevationFilter(low_point=(0, sphere_bounds[2], 0), high_point=(0, sphere_bounds[3], 0))
        elev.SetInputConnection(sphere.GetOutputPort())
        return sphere >> elev

    @staticmethod
    def superquadric_source():
        """
        Make a torus as the source.
        """
        source = vtkSuperquadricSource(center=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0),
                                       phi_resolution=64, theta_resolution=64, theta_roundness=1.0,
                                       size=10, toroidal=True)

        # The quadric is made of strips, so pass it through a triangle filter as
        # the curvature filter only operates on polys
        tri = vtkTriangleFilter()

        # The quadric has nasty discontinuities from the way the edges are generated
        # so let's pass it though a CleanPolyDataFilter and merge any points which
        # are coincident, or very close
        cleaner = vtkCleanPolyData(tolerance=0.005)
        source >> tri >> cleaner
        cleaner_bounds = cleaner.update().output.bounds

        elev = vtkElevationFilter(low_point=(0, cleaner_bounds[2], 0),
                                  high_point=(0, cleaner_bounds[3], 0))
        return cleaner >> elev

    @staticmethod
    def cone_source():
        cone = vtkConeSource()
        cone.SetResolution(6)
        cone.CappingOn()
        cone.Update()
        coneBounds = cone.GetOutput().GetBounds()

        coneNormals = vtkPolyDataNormals()
        coneNormals.SetInputConnection(cone.GetOutputPort())

        elev = vtkElevationFilter()
        elev.SetInputConnection(coneNormals.GetOutputPort())
        elev.SetLowPoint(coneBounds[0], 0, 0)
        elev.SetHighPoint(coneBounds[1], 0, 0)

        # vtkButterflySubdivisionFilter and vtkLinearSubdivisionFilter operate on triangles.
        tf = vtkTriangleFilter()
        tf.SetInputConnection(elev.GetOutputPort())
        tf.Update()
        return tf


def make_lut(scalarRange):
    """
    Make a lookup table using a predefined color series.

    :param scalarRange: The range of the scalars to be coloured.
    :return:  A lookup table.
    """
    color_series = vtkColorSeries()
    # Select a color scheme.
    # for i in range(0,62):
    #     color_series.SetColorScheme(i)
    #     s = f'Colour scheme {color_series.GetColorScheme():2d}: {color_series.GetColorSchemeName():s}'
    #     print(s)

    # Colour scheme 61: Brewer Qualitative Set3
    color_series.color_scheme = 61
    # We use this colour series to create the transfer function.
    lut = vtkColorTransferFunction()
    lut.SetColorSpaceToHSV()
    num_colors = color_series.GetNumberOfColors()
    for i in range(0, num_colors):
        color = vtkColor3ub(color_series.GetColor(i))
        c = list()
        for j in range(0, 3):
            c.append(color[j] / 255.0)
        t = scalarRange[0] + (scalarRange[1] - scalarRange[0]) / (num_colors - 1) * i
        lut.AddRGBPoint(t, *c)
    return lut


def glyph_actor(source, glyph_points, scalar_range, scale_factor, lut):
    """
    Create the actor for glyphing the normals.

    :param: source: the surface.
    :param: glyph_points: The number of points used by the mask filter.
    :param: scalar_range: The range in terms of scalar minimum and maximum.
    :param: scale_factor: The scaling factor for the glyph.
    :param: lut: The lookup table to use.

    :return: The glyph actor.
    """
    arrow_source = vtkArrowSource()
    # Subsample the dataset.
    mask_pts = vtkMaskPoints(random_mode=True,
                             on_ratio=source.update().output.number_of_points // glyph_points)
    source >> mask_pts

    arrow_glyph = vtkGlyph3D(source_connection=arrow_source.output_port,
                             scale_factor=scale_factor,
                             vector_mode=Glyph3D.VectorMode.VTK_USE_NORMAL,
                             color_mode=Glyph3D.ColorMode.VTK_COLOR_BY_SCALAR,
                             scale_mode=Glyph3D.ScaleMode.VTK_SCALE_BY_VECTOR,
                             orient=True)

    # Colour by scalars.
    arrow_glyph_mapper = vtkDataSetMapper(scalar_range=scalar_range,
                                          scalar_visibility=True, lookup_table=lut)
    arrow_glyph_mapper.SetColorModeToMapScalars()
    mask_pts >> arrow_glyph >> arrow_glyph_mapper

    glyph_actor = vtkActor(mapper=arrow_glyph_mapper)
    return glyph_actor


def make_surface_actor(surface, scalar_range, lut):
    """
    Create the actor for a surface.

    :param: surface: The surface.
    :param: scalarRange: The range in terms of scalar minimum and maximum.
    :param: lut: The lookup table to use.

    :return: The actor for the surface.
    """
    mapper = vtkPolyDataMapper(lookup_table=lut, scalar_range=scalar_range)
    surface >> mapper
    mapper.SetColorModeToMapScalars()
    mapper.ScalarVisibilityOn()
    actor = vtkActor()
    actor.SetMapper(mapper)
    return actor


def make_axes_actor():
    """
    Make an axis actor.

    :return: The axis actor.
    """
    axes = vtkAxesActor(shaft_type=vtkAxesActor.CYLINDER_SHAFT, tip_type=vtkAxesActor.CONE_TIP,
                        x_axis_label_text='X', y_axis_label_text='Y', z_axis_label_text='Z',
                        total_length=(1.0, 1.0, 1.0))
    axes.cylinder_radius = 1.0 * axes.cylinder_radius
    axes.cone_radius = 1.75 * axes.cone_radius
    axes.sphere_radius = 1.0 * axes.sphere_radius

    # Set the font properties.
    tprop = axes.x_axis_caption_actor2d.caption_text_property
    tprop.ItalicOn()
    tprop.ShadowOn()
    tprop.SetFontFamilyToTimes()

    # Use the same text properties on the other two axes.
    axes.y_axis_caption_actor2d.caption_text_property.ShallowCopy(tprop)
    axes.z_axis_caption_actor2d.caption_text_property.ShallowCopy(tprop)

    # Now color the labels.
    colors = vtkNamedColors()
    axes.x_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('FireBrick')
    axes.y_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('DarkGreen')
    axes.z_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('DarkBlue')

    return axes


def make_orientation_marker(renderer, iren):
    """
    Create an orientation marker for a given renderer.

    :param renderer: The renderer.
    :param iren: The interactor.

    :return: The orientation marker.
    """
    om = vtkOrientationMarkerWidget()
    om.SetOrientationMarker(make_axes_actor())
    # Position lower left in the viewport.
    om.SetViewport(0, 0, 0.2, 0.2)
    om.SetInteractor(iren)
    om.SetDefaultRenderer(renderer)
    om.EnabledOn()
    om.InteractiveOn()
    renderer.ResetCamera()
    return om


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


def write_png(ren, fn, magnification=1):
    """
    Save the image as a PNG
    :param: ren - the renderer.
    :param: fn - the file name.
    :param: magnification - the magnification, usually 1.
    """
    ren_lge_im = vtkRenderLargeImage(input=ren, magnification=magnification)
    # ren_lge_im.SetInput(ren)
    # ren_lge_im.SetMagnification(magnification)
    img_writer = vtkPNGWriter(file_name=fn)
    # img_writer.SetInputConnection(ren_lge_im.GetOutputPort())
    ren_lge_im >> img_writer
    # img_writer.SetFileName(fn)
    img_writer.Write()


def main():
    def flat_interpolation():
        for actor in actors:
            actor.property.SetInterpolationToFlat()
        ren_win.Render()

    def gouraud_interpolation():
        for actor in actors:
            actor.property.SetInterpolationToGouraud()
        ren_win.Render()

    source_to_use, display_normals, use_gouraud_interpolation, glyph_points = get_program_parameters()

    available_sources = ['boy', 'cone', 'parametric ellipsoid', 'mobius',
                         'random hills', 'parametric torus', 'sphere', 'superquadric']
    source_names = [available_sources[i].title() for i in range(0, len(available_sources))]
    source_name = ' '.join(source_to_use.lower().replace('_', ' ').split())
    if source_name.lower() not in available_sources:
        print('Nonexistent surface:', source_name)
        print('Available sources are:')
        asl = sorted(available_sources)
        asl = [asl[i].title() for i in range(0, len(asl))]
        asl = [asl[i:i + 5] for i in range(0, len(asl), 5)]
        for i in range(0, len(asl)):
            s = ', '.join(asl[i])
            if i < len(asl) - 1:
                s += ','
            print(f'   {s}')
        print('If a name has spaces in it, delineate the name with quotes e.g. "random hills"')
        return

    src = Sources().sources[source_name]

    # The size of the render window.
    ren_win_x_size = 1200
    ren_win_y_size = ren_win_x_size // 3
    min_ren_win_dim = min(ren_win_x_size, ren_win_y_size)

    src_pd = src.update().output
    # [xMin, xMax, yMin, yMax, zMin, zMax]
    bounds = src_pd.bounds
    # Use this to scale the normal glyph.
    scale_factor = min(map(lambda x, y: x - y, bounds[1::2], bounds[::2])) * 0.2
    src_pd.point_data.GetScalars().SetName("Elevation")
    scalar_range = src_pd.scalar_range

    text = {0: 'Original', 1: 'Linear Subdivision', 2: 'Butterfly Subdivision'}

    # Define viewport ranges [x_min, y_min, x_max, y_max]
    viewports = {0: [0.0, 0.0, 1.0 / 3.0, 1.0],
                 1: [1.0 / 3.0, 0.0, 2.0 / 3.0, 1.0],
                 2: [2.0 / 3.0, 0.0, 1.0, 1.0]
                 }

    butterfly = vtkButterflySubdivisionFilter(number_of_subdivisions=3)
    src >> butterfly

    linear = vtkLinearSubdivisionFilter(number_of_subdivisions=3)
    src >> linear

    lut = make_lut(scalar_range)

    # Make the actors.
    actors = list()
    actors.append(make_surface_actor(src, scalar_range, lut))
    actors.append(make_surface_actor(linear, scalar_range, lut))
    actors.append(make_surface_actor(butterfly, scalar_range, lut))

    # Let's visualise the normals.
    glyph_actors = list()
    if display_normals:
        glyph_actors.append(glyph_actor(src, glyph_points, scalar_range, scale_factor, lut))
        glyph_actors.append(glyph_actor(linear, glyph_points, scalar_range, scale_factor, lut))
        glyph_actors.append(glyph_actor(butterfly, glyph_points, scalar_range, scale_factor, lut))

    ren_win = vtkRenderWindow(size=(ren_win_x_size, ren_win_y_size), window_name='PointDataSubdivision')
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    style = vtkInteractorStyleTrackballCamera()
    iren.interactor_style = style

    # Position the source name according to its length.
    title = source_name.title()
    title_positions = get_text_positions(source_names,
                                         justification=TextProperty.Justification.VTK_TEXT_LEFT,
                                         vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_TOP,
                                         width=0.65)

    title_property = vtkTextProperty(color=nc.GetColor3d('Gold'), bold=True, italic=True, shadow=True,
                                     font_size=16,
                                     justification=TextProperty.Justification.VTK_TEXT_LEFT)
    title_actor = vtkTextActor(input=title, text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_NONE,
                               text_property=title_property)
    # Create the text representation. Used for positioning the text actor.
    title_representation = vtkTextRepresentation(enforce_normalized_viewport_bounds=True)
    title_representation.GetPositionCoordinate().value = title_positions[title]['p']
    title_representation.GetPosition2Coordinate().value = title_positions[title]['p2']

    text_property = vtkTextProperty(color=nc.GetColor3d('Gold'), bold=True, italic=False, shadow=False,
                                    font_size=12, font_family_as_string='Courier',
                                    justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                    vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_CENTERED)

    text_positions = get_text_positions(list(text.values()), justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                        vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_BOTTOM,
                                        width=0.6
                                        )

    # Build the renderers, orientation markers and text widgets
    # adding them to the render window.
    # Create the TextActors.
    text_actors = list()
    text_representations = list()
    text_widgets = list()
    om = list()
    camera = None
    for k in text.keys():
        renderer = vtkRenderer(background=nc.GetColor3d('SlateGray'), viewport=viewports[k])

        # Add the actors.
        renderer.AddActor(actors[k])
        if display_normals:
            renderer.AddActor(glyph_actors[k])

        if k == 0:
            camera = renderer.active_camera
        else:
            renderer.active_camera = camera

        renderer.ResetCamera()

        ren_win.AddRenderer(renderer)

        # Text actors.
        label = text[k]
        text_actors.append(
            vtkTextActor(input=label, text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_NONE, text_property=text_property))

        # Create the text representation. Used for positioning the text actor.
        text_representations.append(vtkTextRepresentation(enforce_normalized_viewport_bounds=True))
        text_representations[k].GetPositionCoordinate().value = text_positions[label]['p']
        text_representations[k].GetPosition2Coordinate().value = text_positions[label]['p2']

        # Create the TextWidget for the subdivision names.
        text_widgets.append(
            vtkTextWidget(representation=text_representations[k], text_actor=text_actors[k],
                          default_renderer=renderer, interactor=iren, selectable=False))

        if k == 0:
            # The title.
            title_widget = vtkTextWidget(representation=title_representation, text_actor=title_actor,
                                         default_renderer=renderer, interactor=iren, selectable=False)
            title_widget.On()

        # Orientation marker.
        om.append(make_orientation_marker(renderer, iren))

    if use_gouraud_interpolation:
        gouraud_interpolation()
    else:
        flat_interpolation()

    ren_win.Render()
    for k in text.keys():
        text_widgets[k].On()

    iren.Initialize()
    # write_png(iren.GetRenderWindow().GetRenderers().GetFirstRenderer(), 'TestPointDataSubdivision.png')
    iren.Start()


@dataclass(frozen=True)
class Glyph3D:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_BY_SCALE: int = 0
        VTK_COLOR_BY_SCALAR: int = 1
        VTK_COLOR_BY_VECTOR: int = 2

    @dataclass(frozen=True)
    class IndexMode:
        VTK_INDEXING_OFF: int = 0
        VTK_INDEXING_BY_SCALAR: int = 1
        VTK_INDEXING_BY_VECTOR: int = 2

    @dataclass(frozen=True)
    class ScaleMode:
        VTK_SCALE_BY_SCALAR: int = 0
        VTK_SCALE_BY_VECTOR: int = 1
        VTK_SCALE_BY_VECTORCOMPONENTS: int = 2
        VTK_DATA_SCALING_OFF: int = 3

    @dataclass(frozen=True)
    class VectorMode:
        VTK_USE_VECTOR: int = 0
        VTK_USE_NORMAL: int = 1
        VTK_VECTOR_ROTATION_OFF: int = 2
        VTK_FOLLOW_CAMERA_DIRECTION: int = 3


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
