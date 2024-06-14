#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkStructuredGridOutlineFilter
from vtkmodules.vtkFiltersFlowPaths import vtkStreamTracer
from vtkmodules.vtkFiltersGeometry import vtkStructuredGridGeometryFilter
from vtkmodules.vtkFiltersSources import vtkLineSource, vtkPlaneSource
from vtkmodules.vtkIOLegacy import vtkStructuredGridReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Flow velocity computed for a small kitchen (top and side view).'
    epilogue = '''
    Forty streamlines start along the rake positioned under the window.
    Some eventually travel over the hot stove and are convected upwards.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='kitchen.vtk')
    args = parser.parse_args()
    return args.filename


def main():
    file_name = get_program_parameters()

    colors = vtkNamedColors()

    # Set the furniture colors.
    colors.SetColor('Furniture', 204, 204, 153, 255)

    scalar_range = [0.0, 0.0]
    max_time = 0

    # Read the data.
    reader = vtkStructuredGridReader(file_name=file_name)
    # Force a read to occur.
    reader.update()

    if reader.output.point_data.scalars:
        scalar_range = reader.output.point_data.scalars.GetRange()

    if reader.output.point_data.vectors:
        length = reader.output.length
        max_velocity = reader.output.point_data.vectors.GetMaxNorm()
        max_time = 4.0 * length / max_velocity

    # Outline around the data.
    outline_filter = vtkStructuredGridOutlineFilter()
    outline_mapper = vtkPolyDataMapper()
    reader >> outline_filter >> outline_mapper
    outline = vtkActor(mapper=outline_mapper)
    outline.property.color = colors.GetColor3d('LampBlack')

    # Set up shaded surfaces (i.e., supporting geometry).
    extent = (27, 27, 14, 18, 0, 11)
    door = get_shaded_surfaces(extent, reader, colors, 'Burlywood')

    extent = (0, 0, 9, 18, 6, 12)
    window1 = get_shaded_surfaces(extent, reader, colors, 'SkyBlue')
    window1.property.opacity = 0.6

    extent = (5, 12, 23, 23, 6, 12)
    window2 = get_shaded_surfaces(extent, reader, colors, 'SkyBlue')
    window2.property.opacity = 0.6

    extent = (17, 17, 0, 11, 0, 6)
    cabinet1 = get_shaded_surfaces(extent, reader, colors, 'EggShell')

    extent = (19, 19, 0, 11, 0, 6)
    cabinet2 = get_shaded_surfaces(extent, reader, colors, 'EggShell')

    extent = (17, 19, 0, 0, 0, 6)
    cabinet3 = get_shaded_surfaces(extent, reader, colors, 'EggShell')

    extent = (17, 19, 11, 11, 0, 6)
    cabinet4 = get_shaded_surfaces(extent, reader, colors, 'EggShell')

    extent = (17, 19, 0, 11, 0, 0)
    cabinet5 = get_shaded_surfaces(extent, reader, colors, 'EggShell')

    extent = (17, 19, 0, 7, 6, 6)
    cabinet6 = get_shaded_surfaces(extent, reader, colors, 'EggShell')

    extent = (17, 19, 9, 11, 6, 6)
    cabinet7 = get_shaded_surfaces(extent, reader, colors, 'EggShell')

    extent = (17, 17, 0, 11, 11, 16)
    hood1 = get_shaded_surfaces(extent, reader, colors, 'Silver')

    extent = (19, 19, 0, 11, 11, 16)
    hood2 = get_shaded_surfaces(extent, reader, colors, 'Furniture')

    extent = (17, 19, 0, 0, 11, 16)
    hood3 = get_shaded_surfaces(extent, reader, colors, 'Furniture')

    extent = (17, 19, 11, 11, 11, 16)
    hood4 = get_shaded_surfaces(extent, reader, colors, 'Furniture')

    extent = (17, 19, 0, 7, 11, 11)
    hood5 = get_shaded_surfaces(extent, reader, colors, 'Furniture')

    extent = (17, 19, 0, 11, 16, 16)
    hood6 = get_shaded_surfaces(extent, reader, colors, 'Furniture')

    extent = (17, 19, 9, 11, 11, 11)
    hood7 = get_shaded_surfaces(extent, reader, colors, 'Furniture')

    extent = (17, 19, 7, 9, 6, 6)
    cooking_plate = get_shaded_surfaces(extent, reader, colors, 'Tomato')

    extent = (17, 19, 7, 9, 11, 11)
    sg_filter = get_shaded_surfaces(extent, reader, colors, 'Silver')
    sg_filter.property.opacity = 0.75

    # For fun, lets put a screen across the sg_filter.
    bounds = sg_filter.GetBounds()
    origin = (bounds[0], bounds[2], bounds[4])
    p1 = (bounds[1], bounds[2], bounds[4])
    p2 = (bounds[0], bounds[3], bounds[4])
    resolution = (20, 20)
    sg_scr_src = vtkPlaneSource(origin=origin, point1=p1, point2=p2, resolution=resolution)
    sg_scr_mapper = vtkPolyDataMapper(scalar_visibility=False)
    sg_scr_src >> sg_scr_mapper
    sg_screen = vtkActor(mapper=sg_scr_mapper)
    sg_screen.property.representation = Property.Representation.VTK_WIREFRAME
    sg_screen.property.color = colors.GetColor3d('LampBlack')
    sg_screen.property.line_width = 1

    # Regular streamlines.
    line = vtkLineSource()
    line.SetResolution(39)
    line.SetPoint1(0.08, 2.50, 0.71)
    line.SetPoint2(0.08, 4.50, 0.71)
    line.update()
    rake_mapper = vtkPolyDataMapper()
    line >> rake_mapper
    rake = vtkActor(mapper=rake_mapper)

    streamers = vtkStreamTracer(integrator_type=vtkStreamTracer.RUNGE_KUTTA45,
                                source_data=line.update().output,
                                maximum_propagation=max_time,
                                initial_integration_step=0.5, minimum_integration_step=0.1)

    streamers_mapper = vtkPolyDataMapper(scalar_range=scalar_range)
    reader >> streamers >> streamers_mapper

    lines = vtkActor(mapper=streamers_mapper)
    # lines.property.color = colors.GetColor3d('Black')

    ren = vtkRenderer(background=colors.GetColor3d('SlateGray'), two_sided_lighting=True)
    ren_win = vtkRenderWindow(size=(640, 512), window_name='Kitchen')
    ren_win.AddRenderer(ren)

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Add the actors to the renderer.
    ren.AddActor(outline)
    ren.AddActor(door)
    ren.AddActor(window1)
    ren.AddActor(window2)
    ren.AddActor(cabinet1)
    ren.AddActor(cabinet2)
    ren.AddActor(cabinet3)
    ren.AddActor(cabinet4)
    ren.AddActor(cabinet5)
    ren.AddActor(cabinet6)
    ren.AddActor(cabinet7)
    ren.AddActor(hood1)
    ren.AddActor(hood2)
    ren.AddActor(hood3)
    ren.AddActor(hood4)
    ren.AddActor(hood5)
    ren.AddActor(hood6)
    ren.AddActor(hood7)
    ren.AddActor(cooking_plate)
    ren.AddActor(sg_filter)
    ren.AddActor(sg_screen)
    ren.AddActor(lines)
    ren.AddActor(rake)

    camera = vtkCamera()
    ren.active_camera = camera
    ren.ResetCamera()

    camera.focal_point = (3.505, 2.505, 1.255)
    camera.position = (3.505, 24.6196, 1.255)
    camera.view_up = (0, 0, 1)
    camera.Azimuth(60)
    camera.Elevation(30)
    camera.Dolly(1.4)
    ren.ResetCameraClippingRange()

    ren_win.Render()

    # Interact with the data.
    iren.Start()


def get_shaded_surfaces(extent, reader, colors, color: str):
    """
    Set up shaded surfaces (the supporting geometry).

    :param extent: The extent of the geometry.
    :param reader: The data source.
    :param colors: vtkColors object.
    :param color: The color.
    :return:
    """
    geometry = vtkStructuredGridGeometryFilter(extent=extent)
    mapper = vtkPolyDataMapper(scalar_visibility=False)
    reader >> geometry >> mapper
    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d(color)
    return actor


@dataclass(frozen=True)
class Property:
    @dataclass(frozen=True)
    class Interpolation:
        VTK_FLAT: int = 0
        VTK_GOURAUD: int = 1
        VTK_PHONG: int = 2
        VTK_PBR: int = 3

    @dataclass(frozen=True)
    class Representation:
        VTK_POINTS: int = 0
        VTK_WIREFRAME: int = 1
        VTK_SURFACE: int = 2


if __name__ == '__main__':
    main()
