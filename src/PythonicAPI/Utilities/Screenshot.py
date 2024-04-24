#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkWindowToImageFilter
)


def main():
    colors = vtkNamedColors()

    # create a rendering window and renderer
    ren = vtkRenderer(background=colors.GetColor3d('MistyRose'))
    ren_win = vtkRenderWindow(window_name='Screenshot')
    ren_win.AddRenderer(ren)

    # create a render window interactor
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # create source
    source = vtkSphereSource(center=(0, 0, 0), radius=5.0, phi_resolution=30, theta_resolution=30)

    # mapper
    mapper = vtkPolyDataMapper()
    source >> mapper

    # actor
    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('IndianRed')
    actor.property.specular = 0.6
    actor.property.specular_power = 30

    # assign actor to the renderer
    ren.AddActor(actor)
    ren.SetBackground(colors.GetColor3d('MistyRose'))

    ren_win.Render()

    # screenshot code:
    w2if = vtkWindowToImageFilter(input=ren_win, input_buffer_type=WindowToImageFilter.InputBufferType.VTK_RGB,
                                  read_front_buffer=False)

    writer = vtkPNGWriter(file_name='TestScreenshot.png')
    w2if >> writer
    writer.Write()

    # enable user interface interactor
    iren.Initialize()
    iren.Start()


@dataclass(frozen=True)
class WindowToImageFilter:
    @dataclass(frozen=True)
    class InputBufferType:
        VTK_RGB: int = 3
        VTK_RGBA: int = 4
        VTK_ZBUFFER: int = 5


if __name__ == '__main__':
    main()
