#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkFloatArray,
    vtkIntArray,
    vtkLookupTable
)
from vtkmodules.vtkCommonDataModel import vtkMutableUndirectedGraph
# noinspection PyUnresolvedReferences
from vtkmodules.vtkInfovisLayout import vtkForceDirectedLayoutStrategy
from vtkmodules.vtkRenderingCore import vtkGraphToGlyphs
from vtkmodules.vtkViewsCore import vtkViewTheme
from vtkmodules.vtkViewsInfovis import (
    vtkGraphLayoutView,
    vtkRenderedGraphRepresentation
)


def main():
    colors = vtkNamedColors()

    g = vtkMutableUndirectedGraph()

    v1 = g.AddVertex()
    v2 = g.AddVertex()

    g.AddEdge(v1, v2)
    g.AddEdge(v1, v2)

    scales = vtkFloatArray(number_of_components=1, name='Scales')
    scales.InsertNextValue(2.0)
    scales.InsertNextValue(5.0)

    # Add the scale array to the graph.
    g.GetVertexData().AddArray(scales)

    # Create the color array
    vertex_colors = vtkIntArray(number_of_components=1, name='Color')
    vertex_colors.InsertNextValue(0)
    vertex_colors.InsertNextValue(1)

    # Add the color array to the graph.
    g.GetVertexData().AddArray(vertex_colors)

    lookup_table = vtkLookupTable(number_of_table_values=2)
    lookup_table.SetTableValue(0, colors.GetColor4d('Yellow'))
    lookup_table.SetTableValue(1, colors.GetColor4d('Lime'))
    lookup_table.Build()

    theme = vtkViewTheme()
    theme.SetPointLookupTable(lookup_table)

    # force_directed = vtkForceDirectedLayoutStrategy()
    layout_view = vtkGraphLayoutView(scaled_glyphs=True, color_vertices=True,
                                     scaling_array_name='Scales', vertex_color_array_name='Color')
    # If we create a layout object directly, just set the pointer through this method.
    # graph_layout_view.SetLayoutStrategy(force_directed)
    layout_view.SetLayoutStrategyToForceDirected()
    layout_view.AddRepresentationFromInput(g)
    layout_view.ApplyViewTheme(theme)
    r_graph = vtkRenderedGraphRepresentation()
    g_glyph = vtkGraphToGlyphs()
    r_graph.SafeDownCast(layout_view.GetRepresentation()).SetGlyphType(g_glyph.CIRCLE)
    layout_view.renderer.background = colors.GetColor3d('Navy')
    layout_view.renderer.background2 = colors.GetColor3d('MidnightBlue')
    layout_view.render_window.window_name = 'ScaleVertices'
    layout_view.Render()
    layout_view.ResetCamera()
    layout_view.interactor.Start()


if __name__ == '__main__':
    main()
