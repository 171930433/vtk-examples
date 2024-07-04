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
from vtkmodules.vtkFiltersSources import vtkPointSource
from vtkmodules.vtkIOLegacy import vtkDataSetReader
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
    description = 'Demonstrate the use of vtkPointSource to generate streamlines.'
    epilogue = '''
    center: An optional parameter choosing the center for the seeds.
        0 - Corresponds to Fig 9-47(a) in the VTK textbook.
        1 - A slight shift to the left.
        2 - A slight shift to the upper left (from the original code).
        3 - The default, a slight shift to the upper left.
            Roughly corresponds to Fig 9-47(b) in the VTK textbook.
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('fileName', help='office.binary.vtk')
    parser.add_argument('-c', '--center', default=3, type=int, nargs='?', help='seed center.')
    args = parser.parse_args()
    return args.fileName, args.center


def office(file_name, center):
    # These are the centers for the streamline seeds.
    seed_centers = (
        (0.0, 2.1, 0.5),  # Corresponds to Fig 9-47(a) in the VTK textbook.
        (0.1, 2.1, 0.5),  # A slight shift to the left.
        (0.1, 2.7, 0.5),  # A slight shift to the upper left (from the original code).
        (0.08, 2.7, 0.5)  # The default, a slight shift to the upper left, approximating Fig 9-47(b).
    )
    center = abs(center)
    if center >= len(seed_centers):
        center = len(seed_centers) - 1

    colors = vtkNamedColors()
    # Set the furniture colors, matching those in the VTKTextBook.
    table_top_color = (0.59, 0.427, 0.392)
    filing_cabinet_color = (0.8, 0.8, 0.6)
    book_shelf_color = (0.8, 0.8, 0.6)
    window_color = (0.3, 0.3, 0.5)
    colors.SetColor('TableTop', *table_top_color)
    colors.SetColor('FilingCabinet', *filing_cabinet_color)
    colors.SetColor('BookShelf', *book_shelf_color)
    colors.SetColor('WindowColor', *window_color)

    # We read a data file that represents a CFD analysis of airflow in an office
    # (with ventilation and a burning cigarette).
    reader = vtkDataSetReader(file_name=file_name)

    # Create the scene.
    # We generate a set of planes which correspond to
    # the geometry in the analysis; tables, bookshelves and so on.

    extent = (11, 15, 7, 9, 8, 8)
    table1_actor = get_shaded_surfaces(extent, reader, colors, 'TableTop')

    extent = (11, 15, 10, 12, 8, 8)
    table2_actor = get_shaded_surfaces(extent, reader, colors, 'TableTop')

    extent = (15, 15, 7, 9, 0, 8)
    filing_cabinet1_actor = get_shaded_surfaces(extent, reader, colors, 'FilingCabinet')

    extent = (15, 15, 10, 12, 0, 8)
    filing_cabinet2_actor = get_shaded_surfaces(extent, reader, colors, 'FilingCabinet')

    extent = (13, 13, 0, 4, 0, 11)
    bookshelf1_top_actor = get_shaded_surfaces(extent, reader, colors, 'BookShelf')
    extent = (20, 20, 0, 4, 0, 11)
    bookshelf1_bottom_actor = get_shaded_surfaces(extent, reader, colors, 'BookShelf')
    extent = (13, 20, 0, 0, 0, 11)
    bookshelf1_front_actor = get_shaded_surfaces(extent, reader, colors, 'BookShelf')
    extent = (13, 20, 4, 4, 0, 11)
    bookshelf1_back_actor = get_shaded_surfaces(extent, reader, colors, 'BookShelf')
    extent = (13, 20, 0, 4, 0, 0)
    bookshelf1_lhs_actor = get_shaded_surfaces(extent, reader, colors, 'BookShelf')
    extent = (13, 20, 0, 4, 11, 11)
    bookshelf1_rhs_actor = get_shaded_surfaces(extent, reader, colors, 'BookShelf')

    extent = (13, 13, 15, 19, 0, 11)
    bookshelf2_top_actor = get_shaded_surfaces(extent, reader, colors, 'BookShelf')
    extent = (20, 20, 15, 19, 0, 11)
    bookshelf2_bottom_actor = get_shaded_surfaces(extent, reader, colors, 'BookShelf')
    extent = (13, 20, 15, 15, 0, 11)
    bookshelf2_front_actor = get_shaded_surfaces(extent, reader, colors, 'BookShelf')
    extent = (13, 20, 19, 19, 0, 11)
    bookshelf2_back_actor = get_shaded_surfaces(extent, reader, colors, 'BookShelf')
    extent = (13, 20, 15, 19, 0, 0)
    bookshelf2_lhs_actor = get_shaded_surfaces(extent, reader, colors, 'BookShelf')
    extent = (13, 20, 15, 19, 11, 11)
    bookshelf2_rhs_actor = get_shaded_surfaces(extent, reader, colors, 'BookShelf')

    extent = (20, 20, 6, 13, 10, 13)
    window_actor = get_shaded_surfaces(extent, reader, colors, 'WindowColor')

    extent = (0, 0, 9, 10, 14, 16)
    outlet_actor = get_shaded_surfaces(extent, reader, colors, 'lamp_black')

    extent = (0, 0, 9, 10, 0, 6)
    inlet_actor = get_shaded_surfaces(extent, reader, colors, 'lamp_black')

    # Outline around the data.
    outline_filter = vtkStructuredGridOutlineFilter()
    outline_mapper = vtkPolyDataMapper()
    reader >> outline_filter >> outline_mapper
    outline_actor = vtkActor(mapper=outline_mapper)
    outline_actor.property.color = colors.GetColor3d('Black')

    # Create the source for the streamtubes.
    seeds = vtkPointSource(radius=0.075, center=seed_centers[center], number_of_points=25)
    streamers = vtkStreamTracer(input_connection=reader.output_port, source_connection=seeds.output_port,
                                maximum_propagation=500,
                                minimum_integration_step=0.1, maximum_integration_step=1.0,
                                initial_integration_step=0.2,
                                integrator_type=vtkStreamTracer.RUNGE_KUTTA45)
    streamers.update()
    map_streamers = vtkPolyDataMapper(scalar_range=reader.output.point_data.scalars.range)
    streamers >> map_streamers
    streamers_actor = vtkActor(mapper=map_streamers)

    # Create the rendering window, renderer, and interactive renderer.
    ren = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(size=(640, 400), window_name='Office')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Add the remaining actors to the renderer, set the background and size.
    ren.AddActor(table1_actor)
    ren.AddActor(table2_actor)
    ren.AddActor(filing_cabinet1_actor)
    ren.AddActor(filing_cabinet2_actor)
    ren.AddActor(bookshelf1_top_actor)
    ren.AddActor(bookshelf1_bottom_actor)
    ren.AddActor(bookshelf1_front_actor)
    ren.AddActor(bookshelf1_back_actor)
    ren.AddActor(bookshelf1_lhs_actor)
    ren.AddActor(bookshelf1_rhs_actor)
    ren.AddActor(bookshelf2_top_actor)
    ren.AddActor(bookshelf2_bottom_actor)
    ren.AddActor(bookshelf2_front_actor)
    ren.AddActor(bookshelf2_back_actor)
    ren.AddActor(bookshelf2_lhs_actor)
    ren.AddActor(bookshelf2_rhs_actor)
    ren.AddActor(window_actor)
    ren.AddActor(outlet_actor)
    ren.AddActor(inlet_actor)
    ren.AddActor(outline_actor)
    ren.AddActor(streamers_actor)

    a_camera = vtkCamera()
    a_camera.clipping_range = (0.726079, 36.3039)
    a_camera.focal_point = (2.43584, 2.15046, 1.11104)
    a_camera.position = (-4.76183, -10.4426, 3.17203)
    a_camera.ComputeViewPlaneNormal()
    a_camera.view_up = (0.0511273, 0.132773, 0.989827)
    a_camera.view_angle = 18.604
    a_camera.Zoom(1.2)

    ren.SetActiveCamera(a_camera)

    iren.Initialize()
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


def main():
    file_name, center = get_program_parameters()
    office(file_name, center)


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
