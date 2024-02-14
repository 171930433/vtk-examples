#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersGeneral import vtkAxes
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkFollower,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkRenderingFreeType import vtkVectorText


def main():
    colors = vtkNamedColors()

    # Create the axes and the associated mapper and actor.
    axes = vtkAxes(origin=(0, 0, 0))
    axes_mapper = vtkPolyDataMapper()
    axes >> axes_mapper
    axes_actor = vtkActor(mapper=axes_mapper)

    # Create the 3D text and the associated mapper and follower (a type of actor).
    # Position the text so that it is displayed over the origin of the axes.
    the_text = vtkVectorText(text='Origin')
    text_mapper = vtkPolyDataMapper()
    the_text >> text_mapper
    text_actor = vtkFollower(mapper=text_mapper, scale=(0.2, 0.2, 0.2), position=(0, -0.1, 0))
    text_actor.property.color = colors.GetColor3d('Peacock')

    # Create the Renderer, RenderWindow, and RenderWindowInteractor.
    renderer = vtkRenderer(background=colors.GetColor3d('Silver'))
    # Add the actors to the renderer.
    renderer.AddActor(axes_actor)
    renderer.AddActor(text_actor)
    # Zoom in closer.
    renderer.ResetCamera()
    renderer.active_camera.Zoom(1.6)
    # Reset the clipping range of the camera; set the camera of the follower; render.
    renderer.ResetCameraClippingRange()
    text_actor.camera = renderer.active_camera

    render_window = vtkRenderWindow(size=(640, 480), window_name='TextOrigin')
    render_window.AddRenderer(renderer)
    render_window.Render()

    style = vtkInteractorStyleTrackballCamera()

    # interactor = vtkRenderWindowInteractor(interactor_style=style, render_window=render_window)
    interactor = vtkRenderWindowInteractor()
    interactor.interactor_style = style
    interactor.render_window = render_window
    interactor.Initialize()
    interactor.Start()


if __name__ == '__main__':
    main()
