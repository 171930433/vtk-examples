#!/usr/bin/env python3

import math

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkCommand,
    vtkMath
)
from vtkmodules.vtkInteractionWidgets import (
    vtkCompassRepresentation,
    vtkCompassWidget
)
from vtkmodules.vtkRenderingAnnotation import vtkAnnotatedCubeActor
from vtkmodules.vtkRenderingCore import (
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def compass_widget_value_changed_callback(widget, event):
    """
    Callback to set the camera position according to the position parameters given by the vtkCompassWidget.
    """
    try:
        camera = widget.GetCurrentRenderer().active_camera
    except AttributeError:
        return

    # calculate new camera position from compass widget parameters
    distance = widget.distance
    tilt = vtkMath.RadiansFromDegrees(widget.tilt)
    heading = vtkMath.RadiansFromDegrees(widget.heading)

    x = distance * math.cos(heading) * math.cos(tilt)
    y = distance * math.sin(heading) * math.cos(tilt)
    z = distance * math.sin(tilt)

    camera.position = (x, y, z)
    camera.focal_point = (0, 0, 0)
    camera.view_up = (0, 0, 1)
    camera.clipping_range = (0.1, distance + 1)

    widget.current_renderer.Render()


def main():
    colors = vtkNamedColors()

    actor = vtkAnnotatedCubeActor()
    actor.cube_property.color = colors.GetColor3d('PeachPuff')

    renderer = vtkRenderer()
    render_window = vtkRenderWindow()
    render_window.AddRenderer(renderer)

    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    # Create the widget and its representation.
    compass_representation = vtkCompassRepresentation(minimum_distance=2, maximum_distance=10)

    compass_widget = vtkCompassWidget(interactor=render_window_interactor, representation=compass_representation,
                                      distance=5, tilt_speed=45, distance_speed=2,
                                      default_renderer=renderer)

    # Add a callback to update the camera position on vtkCommand::WidgetValueChangedEvent.
    compass_widget.AddObserver(vtkCommand.WidgetValueChangedEvent, compass_widget_value_changed_callback)

    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d('MidnightBlue'))

    render_window.SetSize(640, 480)
    render_window.SetWindowName('CompassWidget')

    render_window.Render()
    compass_widget.EnabledOn()

    # No interactor style - camera is moved by widget callback.
    render_window_interactor.interactor_style = None
    # Set camera to the initial position.
    compass_widget.InvokeEvent(vtkCommand.WidgetValueChangedEvent)

    render_window_interactor.Start()


if __name__ == '__main__':
    main()
