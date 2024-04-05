#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


class MyInteractorStyle(vtkInteractorStyleTrackballCamera):

    def __init__(self, parent=None):
        super().__init__()

        self.AddObserver('MiddleButtonPressEvent', self.middle_button_press_event)
        self.AddObserver('MiddleButtonReleaseEvent', self.middle_button_release_event)

    def middle_button_press_event(self, obj, event):
        print('Middle Button pressed')
        self.OnMiddleButtonDown()
        return

    def middle_button_release_event(self, obj, event):
        print('Middle Button released')
        self.OnMiddleButtonUp()
        return


def main():
    colors = vtkNamedColors()

    source = vtkSphereSource(center=(0, 0, 0), radius=1)

    mapper = vtkPolyDataMapper()
    source >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('MistyRose')

    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    renderer.AddActor(actor)

    renwin = vtkRenderWindow(window_name='MouseEvents')
    renwin.AddRenderer(renderer)

    interactor = vtkRenderWindowInteractor()
    interactor.interactor_style = MyInteractorStyle()
    interactor.SetRenderWindow(renwin)

    interactor.Initialize()
    renwin.Render()
    interactor.Start()


if __name__ == '__main__':
    main()
