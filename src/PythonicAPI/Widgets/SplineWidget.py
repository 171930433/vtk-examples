#!/usr/bin/python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2

from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkCommand
)
from vtkmodules.vtkFiltersSources import vtkCylinderSource
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkInteractionWidgets import (
    vtkCameraOrientationWidget,
    vtkSplineWidget
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main(argv):
    colors = vtkNamedColors()
    colors.SetColor('ParaViewBkg', 82, 87, 110, 255)

    window_width = 1024
    window_height = 1024

    ren_win = vtkRenderWindow(size=(window_width, window_height), window_name='SplineWidget')
    ren_win.SetSize(window_width, window_height)
    # Important: The interactor must be set prior to enabling the widgets.
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win
    style = vtkInteractorStyleTrackballCamera()
    iren.interactor_style = style

    renderer = vtkRenderer(background=colors.GetColor3d('ParaViewBkg'))

    # Create a cylinder.
    cylinder = vtkCylinderSource()
    cylinder.SetCenter(0.0, 0.0, 0.0)
    cylinder.SetRadius(3.0)
    cylinder.SetHeight(5.0)
    cylinder.SetResolution(100)

    # Create a mapper and actor
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(cylinder.GetOutputPort())
    actor = vtkActor()
    actor.GetProperty().SetColor(colors.GetColor3d('Cornsilk'))
    actor.SetMapper(mapper)
    # Add the actor to the scene
    renderer.AddActor(actor)

    ren_win.AddRenderer(renderer)

    # A spline widget
    spline_widget = vtkSplineWidget(interactor=iren)
    spline_widget.SetProp3D(actor)
    spline_widget.PlaceWidget(-2.5, 2.5, 3.5, 3.5, 0, 0, )
    spline_widget.On()

    spline_widget.AddObserver(vtkCommand.EndInteractionEvent, SplineCallback(spline_widget))

    cow = vtkCameraOrientationWidget(parent_renderer=renderer)
    cow.On()

    ren_win.Render()
    iren.Start()


class SplineCallback:
    def __init__(self, spline_widget):
        self.spline = spline_widget

    def __call__(self, caller, ev):
        spline_widget = caller
        length = spline_widget.summed_length
        print(f'Length: {length:6.2f}')


if __name__ == '__main__':
    import sys

    main(sys.argv)
