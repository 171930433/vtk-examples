#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


class VTKTimerCallback:
    def __init__(self, steps, actor, iren):
        self.timer_count = 0
        self.steps = steps
        self.actor = actor
        self.iren = iren
        self.timerId = None

    def execute(self, obj, event):
        step = 0
        while step < self.steps:
            print(self.timer_count)
            self.actor.position = (self.timer_count / 100.0, self.timer_count / 100.0, 0)
            iren = obj
            iren.render_window.Render()
            self.timer_count += 1
            step += 1
        if self.timerId:
            iren.DestroyTimer(self.timerId)


def main():
    colors = vtkNamedColors()

    # Create a sphere.
    sphere_source = vtkSphereSource(center=(0.0, 0.0, 0.0), radius=2, phi_resolution=30, theta_resolution=30)

    # Create a mapper and actor.
    mapper = vtkPolyDataMapper()
    sphere_source >> mapper
    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d("Peacock")
    actor.property.specular = 0.6
    actor.property.specular_power = 30
    actor.SetMapper(mapper)
    # actor.SetPosition(-5, -5, 0)

    # Setup a renderer, render window, and interactor.
    renderer = vtkRenderer(background=colors.GetColor3d('MistyRose'))
    render_window = vtkRenderWindow(window_name='Animation')
    render_window.AddRenderer(renderer)

    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    # Add the actor to the scene.
    renderer.AddActor(actor)

    # Render and interact
    render_window.Render()
    renderer.active_camera.Zoom(0.8)
    render_window.Render()

    # Initialize must be called prior to creating timer events.
    render_window_interactor.Initialize()

    # Sign up to receive TimerEvent.
    cb = VTKTimerCallback(200, actor, render_window_interactor)
    render_window_interactor.AddObserver('TimerEvent', cb.execute)
    cb.timerId = render_window_interactor.CreateRepeatingTimer(500)

    # start the interaction and timer.
    render_window.Render()
    render_window_interactor.Start()


if __name__ == '__main__':
    main()
