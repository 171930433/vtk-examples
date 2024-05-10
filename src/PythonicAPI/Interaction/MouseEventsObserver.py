#!/usr/bin/env python

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


def main():

    colors = vtkNamedColors()

    source = vtkSphereSource(center=(0, 0, 0), radius=1)

    mapper = vtkPolyDataMapper()
    source >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('MistyRose')

    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    renderer.AddActor(actor)

    renwin = vtkRenderWindow(window_name='MouseEventsObserver')
    renwin.AddRenderer(renderer)

    interactor = vtkRenderWindowInteractor()
    interactor.interactor_style = vtkInteractorStyleTrackballCamera()
    interactor.render_window = renwin

    def dummy_func1(obj, ev):
        print('Before Event')

    def dummy_func2(obj, ev):
        print('After Event')

    # Printing the interator gives you a list of registered
    #  observers of the current interactor style.
    # print(interactor)

    # Adding priorities allow to control the order of observer execution
    # (highest value first! If equal, the first added observer is called first).
    interactor.RemoveObservers('LeftButtonPressEvent')
    interactor.AddObserver('LeftButtonPressEvent', dummy_func1, 1.0)
    interactor.AddObserver('LeftButtonPressEvent', dummy_func2, -1.0)
    interactor.Initialize()
    renwin.Render()
    interactor.Start()


if __name__ == '__main__':
    main()
