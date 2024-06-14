#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkInteractionWidgets import vtkSphereWidget
from vtkmodules.vtkRenderingCore import (
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def sphere_callback(obj, event):
    """
    The callback function.
    :param obj: The sphere widget.
    :param event:
    :return:
    """
    center = obj.center
    print(f'Center: {center[0]:6.3f}, {center[1]:6.3f}, {center[2]:6.3f}')


def main():
    colors = vtkNamedColors()

    # colors.SetColor('bkg', 0.1, 0.2, 0.4, 1.0)

    # A renderer, render window and interactor.
    renderer = vtkRenderer(background=colors.GetColor3d('MidnightBlue'))
    ren_win = vtkRenderWindow(window_name='SphereWidget')
    ren_win.AddRenderer(renderer)
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = ren_win

    # A Sphere widget
    sphere_widget = vtkSphereWidget(interactor=interactor,
                                    representation=SphereWidget.Representation.VTK_SPHERE_SURFACE)
    sphere_widget.sphere_property.color = colors.GetColor3d('BurlyWood')

    # Connect the event to a function.
    sphere_widget.AddObserver('InteractionEvent', sphere_callback)

    # Start
    interactor.Initialize()
    ren_win.Render()
    sphere_widget.On()
    interactor.Start()


@dataclass(frozen=True)
class SphereWidget:
    @dataclass(frozen=True)
    class Representation:
        VTK_SPHERE_OFF: int = 0
        VTK_SPHERE_WIREFRAME: int = 1
        VTK_SPHERE_SURFACE: int = 2


if __name__ == '__main__':
    main()
