#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkElevationFilter
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    sphere = vtkSphereSource(phi_resolution=12, theta_resolution=12)

    color_it = vtkElevationFilter(low_point=(0, 0, -1), high_point=(0, 0, 1))

    mapper = vtkDataSetMapper()
    sphere >> color_it >> mapper

    actor = vtkActor(mapper=mapper)

    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='ColoredSphere')
    ren_win.AddRenderer(renderer)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    renderer.AddActor(actor)

    ren_win.Render()

    # Interact with the data.
    iren.Start()


if __name__ == '__main__':
    main()
