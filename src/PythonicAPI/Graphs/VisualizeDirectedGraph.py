#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonDataModel import vtkMutableDirectedGraph
from vtkmodules.vtkFiltersCore import vtkGlyph3D
from vtkmodules.vtkFiltersSources import (
    vtkGlyphSource2D,
    vtkGraphToPolyData
)
from vtkmodules.vtkInfovisLayout import (
    vtkGraphLayout,
    vtkSimple2DLayoutStrategy
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper
)
from vtkmodules.vtkViewsInfovis import vtkGraphLayoutView
from vtkmodules.vtkCommonColor import vtkNamedColors


def main():

    colors = vtkNamedColors()

    g = vtkMutableDirectedGraph()

    v1 = g.AddVertex()
    v2 = g.AddVertex()
    v3 = g.AddVertex()

    g.AddEdge(v1, v2)
    g.AddEdge(v2, v3)
    g.AddEdge(v3, v1)

    strategy = vtkSimple2DLayoutStrategy()
    layout = vtkGraphLayout(input_data=g, layout_strategy=strategy)

    # Do layout manually before handing graph to the view.
    # This allows us to know the positions of edge arrows.
    graph_layout_view = vtkGraphLayoutView()

    # Tell the view to use the vertex layout we provide
    graph_layout_view.SetLayoutStrategyToPassThrough()
    # The arrows will be positioned on a straight line between two
    # vertices so tell the view not to draw arcs for parallel edges
    graph_layout_view.SetEdgeLayoutStrategyToPassThrough()

    # Add the graph to the view. This will render vertices and edges,
    # but not edge arrows.
    graph_layout_view.AddRepresentationFromInputConnection(layout.GetOutputPort())

    # Manually create an actor containing the glyphed arrows.
    # Set the position (0: edge start, 1: edge end) where
    # the edge arrows should go.
    graph_to_poly = vtkGraphToPolyData(edge_glyph_output=True, edge_glyph_position=0.98)
    layout >> graph_to_poly

    # Make a simple edge arrow for glyphing.
    arrow_source = vtkGlyphSource2D(scale=0.1, glyph_type=GlyphSource2D.GlyphType.VTK_EDGEARROW_GLYPH)

    # Use Glyph3D to repeat the glyph on all edges.
    arrow_glyph = vtkGlyph3D()
    arrow_glyph.SetInputConnection(0, graph_to_poly.GetOutputPort(1))
    arrow_glyph.SetInputConnection(1, arrow_source.GetOutputPort())

    # Add the edge arrow actor to the view.
    arrow_mapper = vtkPolyDataMapper()
    arrow_glyph >> arrow_mapper
    arrowActor = vtkActor(mapper=arrow_mapper)

    graph_layout_view.renderer.background = colors.GetColor3d('SaddleBrown')
    graph_layout_view.renderer.background2 = colors.GetColor3d('Wheat')
    graph_layout_view.renderer.AddActor(arrowActor)

    graph_layout_view.ResetCamera()
    graph_layout_view.Render()
    graph_layout_view.interactor.Start()


@dataclass(frozen=True)
class GlyphSource2D:
    @dataclass(frozen=True)
    class GlyphType:
        VTK_NO_GLYPH: int = 0
        VTK_VERTEX_GLYPH: int = 1
        VTK_DASH_GLYPH: int = 2
        VTK_CROSS_GLYPH: int = 3
        VTK_THICKCROSS_GLYPH: int = 4
        VTK_TRIANGLE_GLYPH: int = 5
        VTK_SQUARE_GLYPH: int = 6
        VTK_CIRCLE_GLYPH: int = 7
        VTK_DIAMOND_GLYPH: int = 8
        VTK_ARROW_GLYPH: int = 9
        VTK_THICKARROW_GLYPH: int = 10
        VTK_HOOKEDARROW_GLYPH: int = 11
        VTK_EDGEARROW_GLYPH: int = 12


if __name__ == '__main__':
    main()
