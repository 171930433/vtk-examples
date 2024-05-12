#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPlanes
from vtkmodules.vtkFiltersGeneral import vtkShrinkPolyData
from vtkmodules.vtkFiltersSources import vtkFrustumSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkPolyDataMapper,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # camera.SetClippingRange(0.1, 0.4)
    planes_array = [0] * 24
    camera = vtkCamera(clipping_range=(0.1, 0.4))
    camera.GetFrustumPlanes(1.0, planes_array)

    planes = vtkPlanes()
    planes.SetFrustumPlanes(planes_array)

    frustum_source = vtkFrustumSource(planes=planes, show_lines=False)

    shrink = vtkShrinkPolyData(shrink_factor=0.9)

    mapper = vtkPolyDataMapper()
    frustum_source >> shrink >> mapper
    mapper.SetInputConnection(shrink.GetOutputPort())

    back = vtkProperty(color=colors.GetColor3d('Tomato'))

    actor = vtkActor(mapper=mapper)
    actor.property.edge_visibility = True
    actor.property.color = colors.GetColor3d('Banana')
    actor.backface_property = back

    # a renderer and render window
    renderer = vtkRenderer(background=colors.GetColor3d('Silver'))
    render_window = vtkRenderWindow(window_name='Frustum')
    render_window.AddRenderer(renderer)
    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    # Add the actors to the scene.
    renderer.AddActor(actor)

    # Position the camera so that we can see the frustum
    renderer.active_camera.position = (1, 0, 0)
    renderer.active_camera.focal_point = (0, 0, 0)
    renderer.active_camera.view_up = (0, 1, 0)
    renderer.active_camera.Azimuth(30)
    renderer.active_camera.Elevation(30)
    renderer.ResetCamera()

    # Render an image (lights and cameras are created automatically).
    render_window.Render()

    # Yes, we are seeing the backfaces since we are outside the frustum.
    render_window_interactor.Start()


if __name__ == '__main__':
    main()
