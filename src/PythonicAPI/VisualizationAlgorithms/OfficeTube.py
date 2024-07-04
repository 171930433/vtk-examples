#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkCommonMath import vtkRungeKutta4
from vtkmodules.vtkFiltersCore import (
    vtkStructuredGridOutlineFilter,
    vtkTubeFilter
)
from vtkmodules.vtkFiltersFlowPaths import vtkStreamTracer
from vtkmodules.vtkFiltersGeometry import vtkStructuredGridGeometryFilter
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
    description = 'The stream polygon. Sweeping a polygon to form a tube.'
    epilogue = '''
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('fileName', help='office.binary.vtk')
    args = parser.parse_args()
    return args.fileName


def main():
    file_name = get_program_parameters()

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
    # (with ventilation and a burning cigarette). We force an update so that we
    # can query the output for its length, i.e., the length of the diagonal
    # of the bounding box. This is useful for normalizing the data.
    reader = vtkDataSetReader(file_name=file_name)
    reader.update()

    # Now we will generate a single streamline in the data. We select the
    # integration order to use (RungeKutta order 4) and associate it with
    # the streamer. The start position is the position in world space where
    # we want to begin streamline integration; and we integrate in both
    # directions. The step length is the length of the line segments that
    # make up the streamline (i.e., related to display). The
    # IntegrationStepLength specifies the integration step length as a
    # fraction of the cell size that the streamline is in.
    integ = vtkRungeKutta4()

    streamer = vtkStreamTracer(start_position=(0.1, 2.1, 0.5), maximum_propagation=500, initial_integration_step=0.05,
                               integration_direction=vtkStreamTracer.BOTH, integrator=integ)

    # The tube is wrapped around the generated streamline. By varying the radius
    # by the inverse of vector magnitude, we are creating a tube whose radius is
    # proportional to mass flux (in incompressible flow).
    stream_tube = vtkTubeFilter(radius=0.02, number_of_sides=12,
                                vary_radius=TubeFilter.VaryRadius.VTK_VARY_RADIUS_BY_VECTOR)
    stream_tube.SetInputArrayToProcess(1, 0, 0, vtkDataObject.FIELD_ASSOCIATION_POINTS, 'vectors')
    reader >> streamer >> stream_tube

    map_stream_tube = vtkPolyDataMapper(scalar_range=reader.output.point_data.scalars.range)
    reader >> streamer >> stream_tube >> map_stream_tube

    stream_tube_actor = vtkActor(mapper=map_stream_tube)
    stream_tube_actor.property.backface_culling = True

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

    # Create the rendering window, renderer, and interactive renderer.
    ren = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(size=(640, 400), window_name='OfficeTube')
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
    ren.AddActor(stream_tube_actor)

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


@dataclass(frozen=True)
class TubeFilter:
    @dataclass(frozen=True)
    class VaryRadius:
        VTK_VARY_RADIUS_OFF: int = 0
        VTK_VARY_RADIUS_BY_SCALAR: int = 1
        VTK_VARY_RADIUS_BY_VECTOR: int = 2
        VTK_VARY_RADIUS_BY_ABSOLUTE_SCALAR: int = 3
        VTK_VARY_RADIUS_BY_VECTOR_NORM: int = 4


if __name__ == '__main__':
    main()
