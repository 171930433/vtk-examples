#!/usr/bin/env python3

from dataclasses import dataclass

import numpy as np
# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkFloatArray
from vtkmodules.vtkCommonDataModel import (
    vtkCellTypes,
    vtkRectilinearGrid
)
from vtkmodules.vtkFiltersCore import vtkImplicitPolyDataDistance
from vtkmodules.vtkFiltersGeneral import vtkClipDataSet
from vtkmodules.vtkFiltersGeometry import vtkRectilinearGridGeometryFilter
from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Create polydata that will be used to slice the grid.
    # In this case, use a cone.
    # This could be any polydata including an stl file.
    cone = vtkConeSource(resolution=50, direction=(0, 0, -1), height=3.0, capping=True)

    # Implicit function that will be used to slice the mesh.
    implicit_poly_data_distance = vtkImplicitPolyDataDistance(input=cone.update().output)

    # Create a grid.
    dimension = 51
    x_coords = vtkFloatArray()
    for x, i in enumerate(np.linspace(-1.0, 1.0, dimension)):
        x_coords.InsertNextValue(i)

    y_coords = vtkFloatArray()
    for y, i in enumerate(np.linspace(-1.0, 1.0, dimension)):
        y_coords.InsertNextValue(i)

    z_coords = vtkFloatArray()
    for z, i in enumerate(np.linspace(-1.0, 1.0, dimension)):
        z_coords.InsertNextValue(i)

    # create a grid - if not using numpy
    dimension = 51
    x_coords = vtkFloatArray()
    for i in range(0, dimension):
        x_coords.InsertNextValue(-1.0 + i * 2.0 / (dimension - 1))

    y_coords = vtkFloatArray()
    for i in range(0, dimension):
        y_coords.InsertNextValue(-1.0 + i * 2.0 / (dimension - 1))

    z_coords = vtkFloatArray()
    for i in range(0, dimension):
        z_coords.InsertNextValue(-1.0 + i * 2.0 / (dimension - 1))

    # The coordinates are assigned to the rectilinear grid. Make sure that
    # the number of values in each of the x_coordinates, y_coordinates,
    # and z_coordinates is equal to what is defined in dimensions.
    dimensions = (x_coords.number_of_tuples, y_coords.number_of_tuples, z_coords.number_of_tuples)
    rgrid = vtkRectilinearGrid(dimensions=dimensions,
                               x_coordinates=x_coords, y_coordinates=y_coords, z_coordinates=z_coords)

    # Create an array to hold distance information.
    signed_distances = vtkFloatArray(number_of_components=1, name='SignedDistances')

    # Evaluate the signed distance function at all of the grid points
    for pointId in range(0, rgrid.GetNumberOfPoints()):
        p = rgrid.GetPoint(pointId)
        signed_distance = implicit_poly_data_distance.EvaluateFunction(p)
        signed_distances.InsertNextValue(signed_distance)

    # Add the SignedDistances to the grid.
    rgrid.GetPointData().SetScalars(signed_distances)

    # Use vtkClipDataSet to slice the grid with the polydata.
    # For some reason we cannot just use:
    # clipper = vtkClipDataSet(input_data=rgrid, inside_out=True, value=0.0, generate_clipped_output=True)

    # Instead we have to:
    clipper = vtkClipDataSet(input_data=rgrid, inside_out=True, value=0.0, generate_clipped_output=False)
    # Then define a new clipper for the outside clip.
    clipper1 = vtkClipDataSet(input_data=rgrid, inside_out=False, value=0.0, generate_clipped_output=False)

    # --- mappers, actors, render, etc. ---
    # Mapper and actor to view the cone.
    cone_mapper = vtkPolyDataMapper()
    cone >> cone_mapper
    cone_actor = vtkActor(mapper=cone_mapper)
    cone_actor.property.opacity = 0.1

    geometry_filter = vtkRectilinearGridGeometryFilter(input_data=rgrid,
                                                       extent=(0, dimension, 0, dimension, int(dimension / 2),
                                                               int(dimension / 2)))

    rgrid_mapper = vtkPolyDataMapper(scalar_range=rgrid.point_data.GetArray('SignedDistances').range,
                                     scalar_visibility=True)
    geometry_filter >> rgrid_mapper
    wire_actor = vtkActor(mapper=rgrid_mapper)
    wire_actor.property.representation = Property.Representation.VTK_WIREFRAME

    # Mapper and actor to view the clipped mesh.
    clipper_mapper = vtkDataSetMapper(scalar_visibility=False, input_connection=clipper.output_port)
    clipper_actor = vtkActor(mapper=clipper_mapper)
    clipper_actor.property.color = colors.GetColor3d('Banana')

    clipper_outside_mapper = vtkDataSetMapper(scalar_visibility=False, input_connection=clipper1.output_port)
    clipper_outside_actor = vtkActor(mapper=clipper_outside_mapper)
    clipper_outside_actor.property.color = colors.GetColor3d('Banana')

    # A renderer and render window
    # Create a renderer, render window, and interactor.
    left_viewport = (0.0, 0.0, 0.5, 1.0)
    left_renderer = vtkRenderer(background=colors.GetColor3d('SteelBlue'), viewport=left_viewport)

    right_viewport = (0.5, 0.0, 1.0, 1.0)
    right_renderer = vtkRenderer(background=colors.GetColor3d('CadetBlue'), viewport=right_viewport)

    # Add the actors.
    left_renderer.AddActor(wire_actor)
    left_renderer.AddActor(clipper_actor)
    # left_renderer.AddActor(cone_actor)

    right_renderer.AddActor(clipper_outside_actor)
    # right_renderer.AddActor(cone_actor)

    ren_win = vtkRenderWindow(size=(640, 480), window_name='ClipDataSetWithPolyData')
    ren_win.AddRenderer(left_renderer)
    ren_win.AddRenderer(right_renderer)

    # An interactor.
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = ren_win

    # Share the camera.

    left_renderer.active_camera.position = (0, -1, 0)
    left_renderer.active_camera.focal_point = (0, 0, 0)
    left_renderer.active_camera.view_up = (0, 0, 1)
    left_renderer.active_camera.Azimuth(30)
    left_renderer.active_camera.Elevation(30)
    left_renderer.ResetCamera()

    right_renderer.active_camera = left_renderer.active_camera

    ren_win.Render()
    interactor.Start()

    # Generate a report.
    ct = vtkCellTypes()

    number_of_cells = clipper.output.number_of_cells
    print('------------------------')
    print(f'The clipped dataset(inside) contains a {clipper.output.class_name} that has {number_of_cells} cells')
    cell_map = dict()
    for i in range(0, number_of_cells):
        cell_map[clipper.output.GetCellType(i)] = cell_map.get(clipper.output.GetCellType(i), 0) + 1

    for k, v in cell_map.items():
        print(' Cell type ', ct.GetClassNameFromTypeId(k), 'occurs', v, 'times.')

    number_of_cells = clipper1.output.number_of_cells
    print('------------------------')
    print(f'The clipped dataset(outside) contains a {clipper1.output.class_name} that has {number_of_cells} cells')
    outside_cell_map = dict()
    for i in range(0, number_of_cells):
        outside_cell_map[clipper1.output.GetCellType(i)] = outside_cell_map.get(clipper1.output.GetCellType(i), 0) + 1

    for k, v in outside_cell_map.items():
        print(' Cell type ', ct.GetClassNameFromTypeId(k), 'occurs', v, 'times.')


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
