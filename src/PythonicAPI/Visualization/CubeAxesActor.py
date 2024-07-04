#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkSuperquadricSource
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    background_color = colors.GetColor3d('DarkSlateGray')
    actor_color = colors.GetColor3d('Tomato')
    axis1_color = colors.GetColor3d('Salmon')
    axis2_color = colors.GetColor3d('PaleGreen')
    axis3_color = colors.GetColor3d('LightSkyBlue')

    # Create a superquadric
    superquadric_source = vtkSuperquadricSource(phi_roundness=3.1, theta_roundness=1.0)
    superquadric_source.update()  # Needed to get the bounds later.

    renderer = vtkRenderer(background=background_color)

    mapper = vtkPolyDataMapper()
    superquadric_source >> mapper

    superquadric_actor = vtkActor(mapper=mapper)
    superquadric_actor.property.diffuse_color = actor_color
    superquadric_actor.property.diffuse = 0.7
    superquadric_actor.property.specular = 0.7
    superquadric_actor.property.specular_power = 50.0

    cube_axes_actor = vtkCubeAxesActor(bounds=superquadric_source.output.bounds, camera=renderer.active_camera)
    cube_axes_actor.use_text_actor_3D = True

    # After VTK Version: 20240519
    cube_axes_actor.x_axes_title_property.color = axis1_color
    cube_axes_actor.x_axes_title_property.font_size = 48
    cube_axes_actor.y_axes_title_property.color = axis2_color
    cube_axes_actor.z_axes_title_property.color = axis3_color

    cube_axes_actor.draw_x_gridlines = True
    cube_axes_actor.draw_y_gridlines = True
    cube_axes_actor.draw_z_gridlines = True
    cube_axes_actor.grid_line_location = vtkCubeAxesActor.VTK_GRID_LINES_FURTHEST

    cube_axes_actor.x_axis_minor_tick_visibility = False
    cube_axes_actor.y_axis_minor_tick_visibility = False
    cube_axes_actor.z_axis_minor_tick_visibility = False

    cube_axes_actor.fly_mode = vtkCubeAxesActor.VTK_FLY_STATIC_EDGES

    renderer.AddActor(cube_axes_actor)
    renderer.AddActor(superquadric_actor)
    renderer.active_camera.Azimuth(30)
    renderer.active_camera.Elevation(30)

    renderer.ResetCamera()

    render_window = vtkRenderWindow(size=(640, 480), window_name='CubeAxesActor')

    render_window.AddRenderer(renderer)

    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    renderer.active_camera.Zoom(0.8)
    render_window.Render()
    render_window_interactor.Start()


if __name__ == '__main__':
    main()
