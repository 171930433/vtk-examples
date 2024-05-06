#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkDoubleArray,
    vtkIntArray
)
from vtkmodules.vtkCommonDataModel import vtkMutableUndirectedGraph
from vtkmodules.vtkInfovisLayout import vtkCircularLayoutStrategy
from vtkmodules.vtkViewsInfovis import vtkGraphLayoutView


def main():
    colors = vtkNamedColors()

    g = vtkMutableUndirectedGraph()

    # Create 3 vertices.
    v1 = g.AddVertex()
    v2 = g.AddVertex()
    v3 = g.AddVertex()

    # Create a fully connected graph.
    g.AddEdge(v1, v2)
    g.AddEdge(v2, v3)
    g.AddEdge(v1, v3)

    # Create the edge weight array.
    weights = vtkDoubleArray(number_of_components=1, name='Weights')

    # Set the edge weights
    weights.InsertNextValue(1.0)
    weights.InsertNextValue(1.0)
    weights.InsertNextValue(2.0)

    # Create an array for the vertex labels.
    vertex_ids = vtkIntArray(number_of_components=1, name='VertexIDs')

    # Set the vertex labels.
    vertex_ids.InsertNextValue(0)
    vertex_ids.InsertNextValue(1)
    vertex_ids.InsertNextValue(2)

    # Add the edge weight array to the graph.
    g.GetEdgeData().AddArray(weights)
    g.GetVertexData().AddArray(vertex_ids)

    circular_layout_strategy = vtkCircularLayoutStrategy()

    graph_layout_view = vtkGraphLayoutView(layout_strategy=circular_layout_strategy,
                                           vertex_label_visibility=True, edge_label_visibility=True,
                                           edge_label_array_name='Weights', vertex_label_array_name='VertexIDs')
    graph_layout_view.AddRepresentationFromInput(g)
    graph_layout_view.GetRepresentation().vertex_label_text_property.color = colors.GetColor3d('Yellow')
    graph_layout_view.GetRepresentation().edge_label_text_property.color = colors.GetColor3d('Lime')
    graph_layout_view.ResetCamera()
    graph_layout_view.Render()
    graph_layout_view.render_window.window_name = 'LabelVerticesAndEdges'
    graph_layout_view.interactor.Start()


if __name__ == '__main__':
    main()
