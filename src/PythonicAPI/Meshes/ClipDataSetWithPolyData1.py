#!/usr/bin/env python3

from dataclasses import dataclass

import numpy as np
# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkFloatArray
from vtkmodules.vtkCommonDataModel import vtkRectilinearGrid
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
    cone = vtkConeSource(resolution=20)

    # Implicit function that will be used to slice the mesh.
    implicit_poly_data_distance = vtkImplicitPolyDataDistance(input=cone.update().output)

    # Create a grid.
    x_coords = vtkFloatArray()
    for x, i in enumerate(np.linspace(-1.0, 1.0, 15)):
        x_coords.InsertNextValue(i)

    y_coords = vtkFloatArray()
    for y, i in enumerate(np.linspace(-1.0, 1.0, 15)):
        y_coords.InsertNextValue(i)

    z_coords = vtkFloatArray()
    for z, i in enumerate(np.linspace(-1.0, 1.0, 15)):
        z_coords.InsertNextValue(i)

    # The coordinates are assigned to the rectilinear grid. Make sure that
    # the number of values in each of the x_coordinates, y_coordinates,
    # and z_coordinates is equal to what is defined in dimensions.
    rgrid = vtkRectilinearGrid(dimensions=(x + 1, y + 1, z + 1),
                               x_coordinates=x_coords, y_coordinates=y_coords, z_coordinates=z_coords)

    # Create an array to hold distance information.
    signed_distances = vtkFloatArray(number_of_components=1, name='SignedDistances')

    # Evaluate the signed distance function at all the grid points.
    for pointId in range(rgrid.GetNumberOfPoints()):
        p = rgrid.GetPoint(pointId)
        signed_distance = implicit_poly_data_distance.EvaluateFunction(p)
        signed_distances.InsertNextValue(signed_distance)

    # Add the SignedDistances to the grid.
    rgrid.GetPointData().SetScalars(signed_distances)

    # Use vtkClipDataSet to slice the grid with the polydata.
    clipper = vtkClipDataSet(input_data=rgrid, inside_out=True, value=0.0)

    # --- mappers, actors, render, etc. ---
    # Mapper and actor to view the cone.
    cone_mapper = vtkPolyDataMapper()
    cone >> cone_mapper
    cone_actor = vtkActor(mapper=cone_mapper)
    cone_actor.property.opacity = 0.1

    # Geometry filter to view the background grid.
    geometry_filter = vtkRectilinearGridGeometryFilter(input_data=rgrid,
                                                       extent=(0, x + 1, 0, y + 1, (z + 1) // 2, (z + 1) // 2))

    rgrid_mapper = vtkPolyDataMapper(scalar_visibility=True)
    geometry_filter >> rgrid_mapper

    wire_actor = vtkActor()
    wire_actor.SetMapper(rgrid_mapper)
    wire_actor.property.representation = Property.Representation.VTK_WIREFRAME
    wire_actor.property.color = colors.GetColor3d('Black')

    # Mapper and actor to view the clipped mesh.
    clipper_mapper = vtkDataSetMapper(scalar_visibility=True)
    clipper >> clipper_mapper

    clipper_actor = vtkActor(mapper=clipper_mapper)
    clipper_actor.property.representation = Property.Representation.VTK_WIREFRAME
    clipper_actor.property.color = colors.GetColor3d('Black')
    clipper_actor.property.opacity = 0.1

    # A renderer and render window.
    renderer = vtkRenderer(background=colors.GetColor3d('Snow'))

    # Add the actors.
    # renderer.AddActor(cone_actor)
    renderer.AddActor(wire_actor)
    renderer.AddActor(clipper_actor)

    ren_win = vtkRenderWindow(window_name='ClipDataSetWithPolyData')
    ren_win.AddRenderer(renderer)

    # An interactor.
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = ren_win

    # Start
    interactor.Initialize()
    ren_win.Render()
    renderer.active_camera.position = (0, -1, 0)
    renderer.active_camera.focal_point = (0, 0, 0)
    renderer.active_camera.view_up = (0, 0, 1)
    renderer.active_camera.Azimuth(30)
    renderer.active_camera.Elevation(30)
    renderer.ResetCamera()
    ren_win.Render()
    interactor.Start()


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
