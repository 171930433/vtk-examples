#!/usr/bin/env python3


# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import vtkGlyph2D
from vtkmodules.vtkFiltersSources import vtkRegularPolygonSource
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleImage
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, 1, 0)
    points.InsertNextPoint(2, 2, 0)

    polydata = vtkPolyData()
    polydata.SetPoints(points)

    # Create anything you want here, we will use a polygon for the demo.
    polygon_source = vtkRegularPolygonSource()  # default is 6 sides

    glyph_2d = vtkGlyph2D(input_data=polydata)
    glyph_2d.SetSourceConnection(polygon_source.GetOutputPort())

    mapper = vtkPolyDataMapper()
    glyph_2d >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('Salmon')

    # Visualize
    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    render_window = vtkRenderWindow(window_name='Glyph2D')
    render_window.AddRenderer(renderer)
    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window
    style = vtkInteractorStyleImage()
    render_window_interactor.interactor_style = style

    renderer.AddActor(actor)

    render_window.Render()
    render_window_interactor.Start()


if __name__ == '__main__':
    main()
