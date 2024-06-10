#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPolyhedron
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    dodecahedron = make_dodecahedron()

    # Visualize
    mapper = vtkPolyDataMapper(input_data=dodecahedron.poly_data)

    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('PapayaWhip')

    renderer = vtkRenderer(background=colors.GetColor3d('CadetBlue'))
    render_window = vtkRenderWindow(window_name='Dodecahedron')
    render_window.AddRenderer(renderer)
    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    renderer.AddActor(actor)
    renderer.active_camera.Azimuth(30)
    renderer.active_camera.Elevation(30)

    renderer.ResetCamera()

    render_window.Render()
    render_window_interactor.Start()


def make_dodecahedron():
    dodecahedron = vtkPolyhedron()

    for i in range(0, 20):
        dodecahedron.GetPointIds().InsertNextId(i)

    dodecahedron.points.InsertNextPoint(1.21412, 0, 1.58931)
    dodecahedron.points.InsertNextPoint(0.375185, 1.1547, 1.58931)
    dodecahedron.points.InsertNextPoint(-0.982247, 0.713644, 1.58931)
    dodecahedron.points.InsertNextPoint(-0.982247, -0.713644, 1.58931)
    dodecahedron.points.InsertNextPoint(0.375185, -1.1547, 1.58931)
    dodecahedron.points.InsertNextPoint(1.96449, 0, 0.375185)
    dodecahedron.points.InsertNextPoint(0.607062, 1.86835, 0.375185)
    dodecahedron.points.InsertNextPoint(-1.58931, 1.1547, 0.375185)
    dodecahedron.points.InsertNextPoint(-1.58931, -1.1547, 0.375185)
    dodecahedron.points.InsertNextPoint(0.607062, -1.86835, 0.375185)
    dodecahedron.points.InsertNextPoint(1.58931, 1.1547, -0.375185)
    dodecahedron.points.InsertNextPoint(-0.607062, 1.86835, -0.375185)
    dodecahedron.points.InsertNextPoint(-1.96449, 0, -0.375185)
    dodecahedron.points.InsertNextPoint(-0.607062, -1.86835, -0.375185)
    dodecahedron.points.InsertNextPoint(1.58931, -1.1547, -0.375185)
    dodecahedron.points.InsertNextPoint(0.982247, 0.713644, -1.58931)
    dodecahedron.points.InsertNextPoint(-0.375185, 1.1547, -1.58931)
    dodecahedron.points.InsertNextPoint(-1.21412, 0, -1.58931)
    dodecahedron.points.InsertNextPoint(-0.375185, -1.1547, -1.58931)
    dodecahedron.points.InsertNextPoint(0.982247, -0.713644, -1.58931)

    faces = [12,  # number of faces
             5, 0, 1, 2, 3, 4,  # number of ids on face, ids
             5, 0, 5, 10, 6, 1,
             5, 1, 6, 11, 7, 2,
             5, 2, 7, 12, 8, 3,
             5, 3, 8, 13, 9, 4,
             5, 4, 9, 14, 5, 0,
             5, 15, 10, 5, 14, 19,
             5, 16, 11, 6, 10, 15,
             5, 17, 12, 7, 11, 16,
             5, 18, 13, 8, 12, 17,
             5, 19, 14, 9, 13, 18,
             5, 19, 18, 17, 16, 15]

    dodecahedron.faces = faces
    dodecahedron.Initialize()

    return dodecahedron


if __name__ == '__main__':
    main()
