#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkPolyData
)
from vtkmodules.vtkFiltersCore import (
    vtkStripper,
    vtkTubeFilter
)
from vtkmodules.vtkFiltersModeling import vtkRotationalExtrusionFilter
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Create the RenderWindow, Renderer and Interactor.
    renderer = vtkRenderer(background=colors.GetColor3d('Burlywood'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='Bottle')
    ren_win.AddRenderer(renderer)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Create the bottle profile.
    points = vtkPoints()
    points.InsertPoint(0, 0.01, 0.0, 0.0)
    points.InsertPoint(1, 1.5, 0.0, 0.0)
    points.InsertPoint(2, 1.5, 0.0, 3.5)
    points.InsertPoint(3, 1.25, 0.0, 3.75)
    points.InsertPoint(4, 0.75, 0.0, 4.00)
    points.InsertPoint(5, 0.6, 0.0, 4.35)
    points.InsertPoint(6, 0.7, 0.0, 4.65)
    points.InsertPoint(7, 1.0, 0.0, 4.75)
    points.InsertPoint(8, 1.0, 0.0, 5.0)
    points.InsertPoint(9, 0.2, 0.0, 5.0)

    lines = vtkCellArray()
    lines.InsertNextCell(10)  # The number of points.
    for i in range(0, 10):
        lines.InsertCellPoint(i)

    profile = vtkPolyData(points=points, lines=lines)

    # Extrude the profile to make the bottle.
    extrude = vtkRotationalExtrusionFilter(input_data=profile, resolution=60)

    mapper = vtkPolyDataMapper()
    extrude >> mapper

    bottle = vtkActor(mapper=mapper)
    bottle.property.color = colors.GetColor3d('Mint')

    # Display the profile.
    stripper = vtkStripper(input_data=profile)

    tubes = vtkTubeFilter(number_of_sides=11, radius=0.05)

    profile_mapper = vtkPolyDataMapper()
    stripper >> tubes >> profile_mapper

    profile_actor = vtkActor()
    profile_actor.SetMapper(profile_mapper)
    profile_actor.property.color = colors.GetColor3d('Tomato')

    # Add the actors to the renderer, set the background and size.
    renderer.AddActor(bottle)
    renderer.AddActor(profile_actor)
    renderer.SetBackground(colors.GetColor3d('Burlywood'))

    ren_win.Render()

    renderer.active_camera.position = (1, 0, 0)
    renderer.active_camera.focal_point = (0, 0, 0)
    renderer.active_camera.view_up = (0, 0, 1)
    renderer.ResetCamera()
    renderer.active_camera.Azimuth(30)
    renderer.active_camera.Elevation(30)

    # Render the image.
    ren_win.Render()
    iren.Start()


if __name__ == '__main__':
    main()
