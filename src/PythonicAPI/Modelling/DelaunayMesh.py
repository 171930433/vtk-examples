#!/usr/bin/env python3

"""
This code is based on the VTK file: Examples/Modelling/Tcl/DelMesh.py.

This example demonstrates how to use 2D Delaunay triangulation.
We create a fancy image of a 2D Delaunay triangulation. Points are
 randomly generated.
"""

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkLogger,
    vtkMinimalStandardRandomSequence,
    vtkPoints
)
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import (
    vtkDelaunay2D,
    vtkGlyph3D,
    vtkTubeFilter
)
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

# vtkExtractEdges moved from vtkFiltersExtraction to vtkFiltersCore in
# VTK commit d9981b9aeb93b42d1371c6e295d76bfdc18430bd
try:
    from vtkmodules.vtkFiltersCore import vtkExtractEdges
except ImportError:
    from vtkmodules.vtkFiltersExtraction import vtkExtractEdges


def main():
    #  Turn of the INFO message from vtkExtractEdges
    # See: https://gitlab.kitware.com/vtk/vtk/-/issues/18785
    vtkLogger.SetStderrVerbosity(vtkLogger.VERBOSITY_OFF)

    colors = vtkNamedColors()

    # Generate some "random" points.
    points = vtkPoints()
    random_sequence = vtkMinimalStandardRandomSequence(seed=1)
    for i in range(0, 50):
        p1 = random_sequence.GetValue()
        random_sequence.Next()
        p2 = random_sequence.GetValue()
        random_sequence.Next()
        points.InsertPoint(i, p1, p2, 0.0)

    # Create a polydata with the points we just created.
    profile = vtkPolyData(points=points)

    # Perform a 2D Delaunay triangulation on them.
    delny = vtkDelaunay2D(tolerance=0.001)
    map_mesh = vtkPolyDataMapper()
    profile >> delny >> map_mesh
    mesh_actor = vtkActor(mapper=map_mesh)
    mesh_actor.property.color = colors.GetColor3d('MidnightBlue')

    # We will now create a nice looking mesh by wrapping the edges in tubes,
    # and putting fat spheres at the points.
    extract = vtkExtractEdges()
    tubes = vtkTubeFilter(radius=0.01, number_of_sides=6)
    tubes.SetInputConnection(extract.GetOutputPort())
    map_edges = vtkPolyDataMapper()
    map_edges.SetInputConnection(tubes.GetOutputPort())
    delny >> extract >> tubes >> map_edges
    edge_actor = vtkActor(mapper=map_edges)
    edge_actor.property.color = colors.GetColor3d('peacock')
    edge_actor.property.specular_color = (1, 1, 1)
    edge_actor.property.specular = 0.3
    edge_actor.property.specular_power = 20
    edge_actor.property.ambient = 0.2
    edge_actor.property.diffuse = 0.8

    ball = vtkSphereSource(radius=0.025, theta_resolution=12, phi_resolution=12)
    balls = vtkGlyph3D(source_connection=ball.output_port)
    map_balls = vtkPolyDataMapper()
    delny >> balls >> map_balls
    ball_actor = vtkActor(mapper=map_balls)
    ball_actor.property.color = colors.GetColor3d('hot_pink')
    ball_actor.property.specular_color = (1, 1, 1)
    ball_actor.property.specular = 0.3
    ball_actor.property.specular_power = 20
    ball_actor.property.ambient = 0.2
    ball_actor.property.diffuse = 0.8

    # Create the rendering window, renderer, and interactive renderer.
    ren = vtkRenderer(background=colors.GetColor3d('AliceBlue'))
    ren_win = vtkRenderWindow(size=(512, 512), window_name='DelaunayMesh')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Add the actors to the renderer, set the background and size.
    ren.AddActor(ball_actor)
    ren.AddActor(edge_actor)

    ren.ResetCamera()
    ren.GetActiveCamera().Zoom(1.3)

    # Interact with the data.
    iren.Initialize()
    ren_win.Render()
    iren.Start()


if __name__ == '__main__':
    main()
