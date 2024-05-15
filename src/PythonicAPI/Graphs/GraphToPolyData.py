#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkMutableUndirectedGraph
from vtkmodules.vtkFiltersSources import vtkGraphToPolyData
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()
    # Create a graph.
    g = vtkMutableUndirectedGraph()

    # Add 4 vertices to the graph.
    v1 = g.AddVertex()
    v2 = g.AddVertex()
    v3 = g.AddVertex()
    v4 = g.AddVertex()

    # Add 3 edges to the graph.
    g.AddEdge(v1, v2)
    g.AddEdge(v1, v3)
    g.AddEdge(v1, v4)

    # Create 4 points - one for each vertex.
    points = vtkPoints()
    points.InsertNextPoint(0.0, 0.0, 0.0)
    points.InsertNextPoint(1.0, 0.0, 0.0)
    points.InsertNextPoint(0.0, 1.0, 0.0)
    points.InsertNextPoint(0.0, 0.0, 1.0)

    # Add the coordinates of the points to the graph.
    g.points = points

    # Convert the graph to a polydata.
    graph_to_poly_data = vtkGraphToPolyData(input_data=g)

    # Create a mapper and actor.
    mapper = vtkPolyDataMapper()
    graph_to_poly_data >> mapper
    actor = vtkActor(mapper=mapper)

    # Create a renderer, render window, and interactor.
    renderer = vtkRenderer(background=colors.GetColor3d('Green'))
    render_window = vtkRenderWindow(window_name='GraphToPolyData')
    render_window.AddRenderer(renderer)
    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    # Add the actor to the scene.
    renderer.AddActor(actor)

    # Render and interact.
    render_window.Render()
    render_window_interactor.Start()


if __name__ == '__main__':
    main()
