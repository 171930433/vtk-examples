#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import (
    vtkColorSeries,
    vtkNamedColors
)
from vtkmodules.vtkFiltersSources import (
    vtkConeSource,
    vtkCubeSource,
    vtkCylinderSource,
    vtkSphereSource
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    source_names = ['sphere', 'cone', 'cube', 'cylinder']

    # We store background colors in a dictionary. Then we extract the red, green and
    # blue components for use later when coloring the render background.
    color_series = vtkColorSeries()
    color_series.SetColorSchemeByName('Brewer Qualitative Pastel2')
    renderer_colors = {'sphere': color_series.GetColor(0),
                       'cone': color_series.GetColor(1),
                       'cube': color_series.GetColor(2),
                       'cylinder': color_series.GetColor(3)
                       }

    viewports = {'sphere': (0, 0, 0.5, 0.5),
                 'cone': (0.5, 0, 1, 0.5),
                 'cube': (0, 0.5, 0.5, 1),
                 'cylinder': (0.5, 0.5, 1, 1)
                 }

    render_window = vtkRenderWindow(window_name='ShareCamera')
    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    first_run = True

    for src_name in source_names:
        if src_name == 'sphere':
            source = vtkSphereSource(center=(0.0, 0.0, 0.0))
        elif src_name == 'cone':
            source = vtkConeSource(center=(0.0, 0.0, 0.0))
        elif src_name == 'cube':
            source = vtkCubeSource(center=(0.0, 0.0, 0.0))
        else:
            source = vtkCylinderSource(center=(0.0, 0.0, 0.0))

        mapper = vtkPolyDataMapper()
        source >> mapper

        actor = vtkActor(mapper=mapper)
        actor.property.color = colors.GetColor3d('Tomato')

        r = renderer_colors[src_name].red / 255.0
        g = renderer_colors[src_name].green / 255.0
        b = renderer_colors[src_name].blue / 255.0
        renderer = vtkRenderer(background=(r, g, b), viewport=viewports[src_name])
        renderer.AddActor(actor)

        if first_run:
            camera = renderer.active_camera
            camera.Azimuth(30)
            camera.Elevation(30)
            first_run = False
        else:
            renderer.SetActiveCamera(camera)

        renderer.ResetCamera()
        render_window.AddRenderer(renderer)

    render_window.Render()
    render_window.SetWindowName('ShareCamera')

    render_window_interactor.Start()


if __name__ == '__main__':
    main()
