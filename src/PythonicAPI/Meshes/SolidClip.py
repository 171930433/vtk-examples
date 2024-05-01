# !/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPlane
from vtkmodules.vtkFiltersCore import vtkClipPolyData
from vtkmodules.vtkFiltersSources import vtkSuperquadricSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    # Create a superquadric
    superquadric_source = vtkSuperquadricSource(phi_roundness=3.1, theta_roundness=2.2)

    # Define a clipping plane
    clip_plane = vtkPlane(normal=(1.0, -1.0, -1.0), origin=(0.0, 0.0, 0.0))

    # Clip the source with the plane
    clipper = (
            superquadric_source >>
            vtkClipPolyData(clip_function=clip_plane, generate_clipped_output=True)
    ).update().output

    colors = vtkNamedColors()

    # Create a property to be used for the back faces. Turn off all
    # shading by specifying 0 weights for specular and diffuse. Max the
    # ambient.
    back_faces = vtkProperty(specular=0.0, diffuse=0.0, ambient=1.0, ambient_color=colors.GetColor3d('Tomato'))

    # Create a mappers and actors.
    superquadric_mapper = vtkPolyDataMapper(input_data=clipper[0])
    superquadric_actor = vtkActor(mapper=superquadric_mapper, backface_property=back_faces)

    # Here we get the polygonal data that is clipped away
    clipped_away_mapper = vtkPolyDataMapper(input_data=clipper[1], scalar_visibility=False)
    # Let us display it as a faint object
    clipped_away_actor = vtkActor(mapper=clipped_away_mapper)
    clipped_away_actor.property.diffuse_color = colors.GetColor3d('Silver')
    clipped_away_actor.property.opacity = 0.1

    # Create a renderer
    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))

    # Add the actors to the renderer
    renderer.AddActor(superquadric_actor)
    renderer.AddActor(clipped_away_actor)
    renderer.ResetCamera()
    renderer.active_camera.Dolly(1.5)
    renderer.ResetCameraClippingRange()

    render_window = vtkRenderWindow(size=(600, 600), window_name='SolidClip')
    render_window.AddRenderer(renderer)
    render_window.Render()

    # Interact with the window
    # This gives an unexpected argument warning but works.
    # render_window_interactor = vtkRenderWindowInteractor(render_window=render_window)
    # Use this instead.
    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window
    render_window_interactor.Start()


if __name__ == '__main__':
    main()
