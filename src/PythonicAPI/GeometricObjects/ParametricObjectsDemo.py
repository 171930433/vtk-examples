#!/usr/bin/env python3

"""
    Demonstrate all the parametric objects.
"""

from collections import OrderedDict
from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingFreeType
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonComputationalGeometry import (
    vtkParametricBohemianDome,
    vtkParametricBour,
    vtkParametricBoy,
    vtkParametricCatalanMinimal,
    vtkParametricConicSpiral,
    vtkParametricCrossCap,
    vtkParametricDini,
    vtkParametricEllipsoid,
    vtkParametricEnneper,
    vtkParametricFigure8Klein,
    vtkParametricHenneberg,
    vtkParametricKlein,
    vtkParametricKuen,
    vtkParametricMobius,
    vtkParametricPluckerConoid,
    vtkParametricPseudosphere,
    vtkParametricRandomHills,
    vtkParametricRoman,
    vtkParametricSpline,
    vtkParametricSuperEllipsoid,
    vtkParametricSuperToroid,
    vtkParametricTorus
)
from vtkmodules.vtkCommonCore import (
    vtkMinimalStandardRandomSequence,
    vtkPoints
)
from vtkmodules.vtkFiltersCore import (
    vtkGlyph3D,
    vtkMaskPoints
)
from vtkmodules.vtkFiltersSources import (
    vtkArrowSource,
    vtkParametricFunctionSource
)
from vtkmodules.vtkIOImage import (
    vtkPNGWriter
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkInteractionWidgets import (
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty,
    vtkWindowToImageFilter
)


def get_program_parameters():
    import argparse
    description = 'Display the parametric surfaces.'
    epilogue = '''
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-s', '--surface_name', default=None, help='The name of the surface e.g. "Figure-8 Klein".')
    parser.add_argument('-b', '--back_face', action='store_true', help='Color the back face.')
    parser.add_argument('-n', '--normals', action='store_true', help='Display normals.')
    parser.add_argument('-l', '--limits', action='store_true', help='Display the geometric bounds of the object..')
    args = parser.parse_args()
    return args.surface_name, args.back_face, args.normals, args.limits


def main():
    surface_name, back_face, normals, limits = get_program_parameters()

    # Get the parametric functions and build the pipeline.
    pfn = get_parametric_functions()

    # Check for a single surface.
    single_surface = None
    if surface_name:
        sn = surface_name.lower()
        for t in pfn.keys():
            if sn == t.lower():
                single_surface = t
    if single_surface is None and surface_name:
        print('Nonexistent surface:', surface_name)
        print('Available surfaces are:')
        asl = sorted(list(pfn.keys()))
        asl = [asl[i].title() for i in range(0, len(asl))]
        asl = [asl[i:i + 5] for i in range(0, len(asl), 5)]
        for i in range(0, len(asl)):
            s = ', '.join(asl[i])
            if i < len(asl) - 1:
                s += ','
            print(f'   {s}')
        return

    # Now decide on the surfaces to build.
    surfaces = dict()
    if single_surface:
        surfaces[single_surface] = pfn[single_surface]
    else:
        surfaces = pfn

    if single_surface is not None:
        renderer_size = 1000
        grid_column_dimensions = 1
        grid_row_dimensions = 1
    else:
        renderer_size = 200
        grid_column_dimensions = 5
        grid_row_dimensions = 5
    size = (renderer_size * grid_column_dimensions, renderer_size * grid_row_dimensions)

    ren_win = vtkRenderWindow(size=size, window_name='ParametricObjectsDemo')
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)
    style = vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)

    colors = vtkNamedColors()

    # Create one text property for all.
    text_scale_mode = {'none': 0, 'prop': 1, 'viewport': 2}
    justification = {'left': 0, 'centered': 1, 'right': 2}
    text_property = vtkTextProperty(color=colors.GetColor3d('LavenderBlush'), bold=True, italic=True,
                                    shadow=True,
                                    font_size=renderer_size // 12, justification=justification['centered'])

    # Position text according to its length and centered in the viewport.
    surface_names = list()
    for k in surfaces.keys():
        surface_names.append(surfaces[k].class_name)
    text_positions = get_text_positions(surface_names, justification='center')

    back_property = vtkProperty(color=colors.GetColor3d('Peru'))

    bounding_boxes = dict()
    text_representations = list()
    text_widgets = list()
    surf_items = list(surfaces.items())
    glyph_vector_mode = {'use_vector': 0, 'use_normal': 1, 'vector_rotation_off': 2, 'follow_camera_direction': 3}

    for row in range(0, grid_row_dimensions):
        for col in range(0, grid_column_dimensions):
            index = row * grid_column_dimensions + col

            # Set the renderer's viewport dimensions (xmin, ymin, xmax, ymax) within the render window.
            # Note that for the Y values, we need to subtract the row index from grid_rows
            # because the viewport Y axis points upwards, but we want to draw the grid from top to down.
            viewport = (
                float(col) / grid_column_dimensions,
                float(grid_row_dimensions - row - 1) / grid_row_dimensions,
                float(col + 1) / grid_column_dimensions,
                float(grid_row_dimensions - row) / grid_row_dimensions
            )

            # Create a renderer for this grid cell.
            renderer = vtkRenderer(background=colors.GetColor3d('MidnightBlue'), viewport=viewport)

            # Add the corresponding actor and label for this grid cell, if they exist.
            if index < len(surfaces):
                name = surface_names[index]
                src = vtkParametricFunctionSource(parametric_function=surf_items[index][1], u_resolution=51,
                                                  v_resolution=51, w_resolution=51)
                mapper = vtkPolyDataMapper()
                src >> mapper
                actor = vtkActor(mapper=mapper)
                actor.property.color = colors.GetColor3d("NavajoWhite")
                if back_face:
                    actor.backface_property = back_property

                renderer.AddActor(actor)

                # Create the text actor and representation.
                text_actor = vtkTextActor(input=surf_items[index][0].title(), text_scale_mode=text_scale_mode['none'],
                                          text_property=text_property)

                # Create the text representation. Used for positioning the text actor.
                text_representations.append(vtkTextRepresentation(enforce_normalized_viewport_bounds=True))
                text_representations[index].GetPositionCoordinate().value = text_positions[name]['p']
                text_representations[index].GetPosition2Coordinate().value = text_positions[name]['p2']

                # Create the text widget, setting the default renderer and interactor.
                text_widgets.append(
                    vtkTextWidget(representation=text_representations[index], text_actor=text_actor,
                                  default_renderer=renderer, interactor=iren, selectable=False))

                bounds = src.update().output.bounds
                bounding_boxes[surf_items[index][0]] = bounds
                if normals:
                    # Glyphing
                    mask_pts = vtkMaskPoints(random_mode=True, maximum_number_of_points=150)

                    arrow = vtkArrowSource(tip_resolution=16, tip_length=0.3, tip_radius=0.1)
                    glyph = vtkGlyph3D(source_connection=arrow.output_port(),
                                       vector_mode=glyph_vector_mode['use_normal'], orient=True,
                                       scale_factor=get_maximum_length(bounds) / 10.0)

                    glyph_mapper = vtkPolyDataMapper()

                    src >> mask_pts >> glyph >> glyph_mapper

                    glyph_actor = vtkActor(mapper=glyph_mapper)
                    glyph_actor.property.color = colors.GetColor3d("GreenYellow")

                    renderer.AddActor(glyph_actor)

                renderer.ResetCamera()
                renderer.active_camera.Azimuth(30)
                renderer.active_camera.Elevation(-30)
                renderer.active_camera.Zoom(0.9)
                renderer.ResetCameraClippingRange()

                ren_win.AddRenderer(renderer)
            else:
                ren_win.AddRenderer(renderer)

    if limits:
        for k, v in bounding_boxes.items():
            display_bounding_box_and_center(k, v)

    if surface_name:
        fn = single_surface.title().replace(' ', '_')
    else:
        fn = 'ParametricObjectsDemo'

    print_callback = PrintCallback(iren, fn, 1, False)
    iren.AddObserver('KeyPressEvent', print_callback)

    for i in range(0, len(surfaces)):
        text_widgets[i].On()

    iren.Initialize()
    iren.Start()


def get_parametric_functions():
    """
    Create an ordered dictionary of the parametric functions and set some parameters.

    :return: The ordered dictionary.
    """

    # The spline needs points
    spline_points = vtkPoints()
    rng = vtkMinimalStandardRandomSequence()
    rng.SetSeed(8775070)
    for p in range(0, 10):
        xyz = [None] * 3
        for idx in range(0, len(xyz)):
            xyz[idx] = rng.GetRangeValue(-1.0, 1.0)
            rng.Next()
        spline_points.InsertNextPoint(xyz)

    pfn = dict()
    pfn['boy'] = vtkParametricBoy()
    pfn['conic spiral'] = vtkParametricConicSpiral()
    pfn['cross-cap'] = vtkParametricCrossCap()
    pfn['dini'] = vtkParametricDini()
    pfn['ellipsoid'] = vtkParametricEllipsoid(x_radius=0.5, y_radius=2.0)
    pfn['enneper'] = vtkParametricEnneper()
    pfn['figure-8 klein'] = vtkParametricFigure8Klein()
    pfn['klein'] = vtkParametricKlein()
    pfn['mobius'] = vtkParametricMobius(radius=2.0, minimum_v=-0.5, maximum_v=0.5)
    pfn['random hills'] = vtkParametricRandomHills(random_seed=1, number_of_hills=30)
    pfn['roman'] = vtkParametricRoman()
    pfn['super ellipsoid'] = vtkParametricSuperEllipsoid(n1=0.5, n2=0.4)
    pfn['super toroid'] = vtkParametricSuperToroid(n1=0.5, n2=3.0)
    pfn['torus'] = vtkParametricTorus()
    pfn['spline'] = vtkParametricSpline(points=spline_points)
    # Extra parametric surfaces.
    pfn['bohemian dome'] = vtkParametricBohemianDome(a=5.0, b=1.0, c=2.0)
    pfn['bour'] = vtkParametricBour()
    pfn['catalan minimal'] = vtkParametricCatalanMinimal()
    pfn['henneberg'] = vtkParametricHenneberg()
    pfn['kuen'] = vtkParametricKuen(delta_v0=0.001)
    pfn['plucker conoid'] = vtkParametricPluckerConoid()
    pfn['pseudosphere'] = vtkParametricPseudosphere()

    # Now set more parameters.
    pfn['random hills'].AllowRandomGenerationOn()

    keys = sorted(pfn.keys())
    ordered_pfn = OrderedDict()
    for k in keys:
        ordered_pfn[k] = pfn[k]

    return ordered_pfn


def get_centre(bounds):
    """
    Get the centre of the object from the bounding box.

    :param bounds: The bounding box of the object.
    :return:
    """
    if len(bounds) != 6:
        return None
    return [bounds[i] - (bounds[i] - bounds[i - 1]) / 2.0 for i in range(1, len(bounds), 2)]


def get_maximum_length(bounds):
    """
    Calculate the maximum length of the side bounding box.

    :param bounds: The bounding box of the object.
    :return:
    """
    if len(bounds) != 6:
        return None
    return max([bounds[i] - bounds[i - 1] for i in range(1, len(bounds), 2)])


def display_bounding_box_and_center(name, bounds):
    """
    Display the dimensions of the bounding box, maximum diagonal length
     and coordinates of the centre.

    :param name: The name of the object.
    :param bounds: The bounding box of the object.
    :return:
    """
    if len(bounds) != 6:
        return
    max_len = get_maximum_length(bounds)
    centre = get_centre(bounds)
    s = f'{name:21s}\n'
    s += f'{"  Bounds (min, max)":21s}  :'
    s += f' x:({bounds[0]:6.2f}, {bounds[1]:6.2f})'
    s += f' y:({bounds[2]:6.2f}, {bounds[3]:6.2f})'
    s += f' z:({bounds[4]:6.2f}, {bounds[5]:6.2f})\n'
    if max_len:
        s += f'  Maximum side length  : {max_len:6.2f}\n'
    if centre:
        s += f'  Centre (x, y, z)     : ({centre[0]:6.2f}, {centre[1]:6.2f}, {centre[2]:6.2f})\n'
    print(s)


class PrintCallback:
    def __init__(self, caller, file_name, image_quality=1, rgba=True):
        self.caller = caller
        self.image_quality = image_quality
        # rgba is the buffer type,
        #  (if true, there is no background in the screenshot).
        self.rgba = rgba
        parent = Path(file_name).resolve().parent
        pth = Path(parent) / file_name
        self.path = Path(str(pth)).with_suffix('.png')

    def __call__(self, caller, ev):
        # Save the screenshot.
        if caller.GetKeyCode() == "k":
            w2if = vtkWindowToImageFilter(input=caller.GetRenderWindow(), read_front_buffer=True,
                                          scale=(self.image_quality, self.image_quality))
            if self.rgba:
                w2if.SetInputBufferTypeToRGBA()
            else:
                w2if.SetInputBufferTypeToRGB()
            writer = vtkPNGWriter(file_name=self.path)
            w2if >> writer
            writer.Write()
            print('Screenshot saved to:', self.path.name)


def get_text_positions(available_surfaces, justification='center'):
    """
    Get positioning information for the names of the surfaces.

    :param available_surfaces: The surfaces
    :param justification: left, center or right
    :return: A list of positioning information.
    """
    # Position the source name according to its length and justification in the viewport.
    # Top
    # y0 = 0.79
    # Bottom
    y0 = 0.01
    dy = 0.1
    # The gap between the left or right edge of the screen and the text.
    dx = 0.01
    # The size of the maximum length of the text in screen units.
    x_scale = 0.95

    name_len_min = 0
    name_len_max = 0
    first = True
    for k in available_surfaces:
        sz = len(k)
        if first:
            name_len_min = name_len_max = sz
            first = False
        else:
            name_len_min = min(name_len_min, sz)
            name_len_max = max(name_len_max, sz)
    text_positions = dict()
    for k in available_surfaces:
        sz = len(k)
        delta_sz = x_scale * sz / name_len_max
        if delta_sz <= 2.0 * dx:
            dx = 0.01
            delta_sz -= 0.02
        else:
            delta_sz -= 2.0 * dx

        if justification.lower() in ['center', 'centre']:
            x0 = 0.5 - delta_sz / 2.0
        elif justification.lower() == 'right':
            x0 = 1.0 - delta_sz
            if dx < x0:
                x0 -= dx
            else:
                x0 = dx
            if x0 + delta_sz >= 1:
                delta_sz -= dx
                x0 -= dx
        else:
            # Default is left justification.
            x0 = dx
            if x0 + dx >= 1.0:
                x0 = dx - x0
            if x0 + delta_sz >= 1:
                delta_sz -= dx
                x0 = dx

        # For debugging!
        # print(
        #     f'{k:16s}: (x0, y0) = ({x0:3.2f}, {y0:3.2f}), (x1, y1) = ({x0 + delta_sz:3.2f}, {y0 + dy:3.2f})'
        #     f', width={delta_sz:3.2f}')
        text_positions[k] = {'p': [x0, y0, 0], 'p2': [delta_sz, dy, 0]}

    return text_positions


if __name__ == '__main__':
    main()
