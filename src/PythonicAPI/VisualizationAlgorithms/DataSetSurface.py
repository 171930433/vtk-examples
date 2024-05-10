#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkHexahedron,
    vtkPlane,
    vtkUnstructuredGrid
)
from vtkmodules.vtkFiltersCore import vtkCutter
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Set up the coordinates of eight points
    # (the two faces must be in counterclockwise order as viewed from the
    # outside)
    point_coords = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 0.0, 1.0],
        [1.0, 1.0, 1.0],
        [0.0, 1.0, 1.0]
    ]

    # Create the points and a hexahedron from the points.
    points = vtkPoints()
    hexa = vtkHexahedron()
    for i, pointCoord in enumerate(point_coords):
        points.InsertNextPoint(pointCoord)
        hexa.GetPointIds().SetId(i, i)

    # Add the hexahedron to a cell array.
    hexs = vtkCellArray()
    hexs.InsertNextCell(hexa)

    # Add the points and hexahedron to an unstructured grid.
    u_grid = vtkUnstructuredGrid()
    u_grid.SetPoints(points)
    u_grid.InsertNextCell(hexa.GetCellType(), hexa.GetPointIds())

    # Extract the outer (polygonal) surface.
    surface = vtkDataSetSurfaceFilter()

    a_beam_mapper = vtkDataSetMapper()
    u_grid >> surface >> a_beam_mapper
    a_beam_property = vtkProperty(color=colors.GetColor3d('Yellow'), opacity=0.60, edge_visibility=True,
                                  edge_color=colors.GetColor3d('Black'), line_width=1.5)
    a_beam_actor = vtkActor(mapper=a_beam_mapper, property=a_beam_property)
    a_beam_actor.AddPosition(0, 0, 0)

    # Create a plane to cut, here it cuts in the XZ direction
    # (XZ normal=(1,0,0) XY =(0,0,1), YZ =(0,1,0)
    plane = vtkPlane(origin=(0.5, 0, 0), normal=(1, 0, 0))

    # Create cutter.
    cutter = vtkCutter(cut_function=plane, input_data=a_beam_actor.mapper.input)
    cutter_mapper = vtkPolyDataMapper()
    cutter >> cutter_mapper

    # Create plane actor.
    plane_actor = vtkActor(mapper=cutter_mapper)
    plane_actor.property.color = colors.GetColor3d('Red')
    plane_actor.property.line_width = 2

    # Create a renderer, render window, and interactor.
    renderer = vtkRenderer(background=colors.GetColor3d('Seashell'))
    render_window = vtkRenderWindow(window_name='DatasetSurface')
    render_window.AddRenderer(renderer)

    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    # Add the actors to the scene.
    renderer.AddActor(a_beam_actor)
    renderer.AddActor(plane_actor)

    renderer.ResetCamera()
    renderer.GetActiveCamera().Azimuth(-25)
    renderer.GetActiveCamera().Elevation(30)

    # Render and interact.
    render_window.Render()
    render_window_interactor.Start()


if __name__ == '__main__':
    main()
