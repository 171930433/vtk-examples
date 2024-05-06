# !/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import (
    vtkConvexPointSet,
    vtkPolyData,
    vtkUnstructuredGrid
)
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkGlyph3DMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    cps = vtkConvexPointSet()
    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, 0, 0)
    points.InsertNextPoint(1, 1, 0)
    points.InsertNextPoint(0, 1, 0)
    points.InsertNextPoint(0, 0, 1)
    points.InsertNextPoint(1, 0, 1)
    points.InsertNextPoint(1, 1, 1)
    points.InsertNextPoint(0, 1, 1)
    points.InsertNextPoint(0.5, 0, 0)
    points.InsertNextPoint(1, 0.5, 0)
    points.InsertNextPoint(0.5, 1, 0)
    points.InsertNextPoint(0, 0.5, 0)
    points.InsertNextPoint(0.5, 0.5, 0)

    for i in range(0, 13):
        cps.GetPointIds().InsertId(i, i)

    ug = vtkUnstructuredGrid(points=points)
    ug.Allocate(1, 1)
    ug.InsertNextCell(cps.GetCellType(), cps.GetPointIds())

    colors = vtkNamedColors()

    mapper = vtkDataSetMapper()
    ug >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d("Tomato")
    actor.property.line_width = 3
    actor.property.edge_visibility = True

    # Glyph the points
    sphere = vtkSphereSource(radius=0.03, phi_resolution=21, theta_resolution=21)

    # Create a polydata to store everything in
    poly_data = vtkPolyData(points=points)

    point_mapper = vtkGlyph3DMapper(input_data=poly_data, source_data=sphere.update().output)

    point_actor = vtkActor(mapper=point_mapper)
    point_actor.property.color = colors.GetColor3d('Peacock')

    # Create a renderer, render window, and interactor.
    renderer = vtkRenderer(background=colors.GetColor3d('Silver'))
    render_window = vtkRenderWindow(size=(640, 480), window_name='ConvexPointSet')
    render_window.AddRenderer(renderer)
    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    # Add the actors to the scene
    renderer.AddActor(actor)
    renderer.AddActor(point_actor)

    renderer.ResetCamera()
    renderer.active_camera.Azimuth(210)
    renderer.active_camera.Elevation(30)
    renderer.ResetCameraClippingRange()

    # Render and interact
    render_window.Render()
    render_window_interactor.Start()


if __name__ == '__main__':
    main()
