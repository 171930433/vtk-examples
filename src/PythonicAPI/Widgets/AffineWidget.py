#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkCallbackCommand
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
from vtkmodules.vtkFiltersSources import (
    vtkPlaneSource,
    vtkSphereSource
)
from vtkmodules.vtkInteractionWidgets import vtkAffineWidget
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindowInteractor,
    vtkRenderWindow,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Create two spheres: a larger one and a smaller one on top of the larger one
    # to show a reference point while rotating.
    # Then append the two spheres into one vtkPolyData.
    # Create a mapper and actor for the spheres.
    sphere_mapper = vtkPolyDataMapper()
    ((vtkSphereSource(), vtkSphereSource(radius=0.075, center=(0, 0.5, 0))) >>
     vtkAppendPolyData() >> sphere_mapper)
    sphere_actor = vtkActor(mapper=sphere_mapper)
    sphere_actor.property.color = colors.GetColor3d('White')

    # Create a plane centered over the larger sphere with 4x4 subsections.
    plane_source = vtkPlaneSource(x_resolution=4, y_resolution=4, origin=(-1, -1, 0),
                                  point1=(1, -1, 0), point2=(-1, 1, 0))
    # Create a mapper and actor for the plane and show it as a wireframe.
    plane_mapper = vtkPolyDataMapper()
    plane_source >> plane_mapper
    plane_actor = vtkActor(mapper=plane_mapper)
    plane_actor.property.representation = Property.Representation.VTK_WIREFRAME
    plane_actor.property.color = colors.GetColor3d('Red')

    ren = vtkRenderer(background=colors.GetColor3d('LightSkyBlue'),
                      background2=colors.GetColor3d('MidnightBlue'),
                      gradient_background=True)
    ren_win = vtkRenderWindow(size=(640, 480), window_name='AffineWidget')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win
    iren.interactor_style.SetCurrentStyleToTrackballCamera()

    ren.AddActor(sphere_actor)
    ren.AddActor(plane_actor)

    ren_win.Render()

    # Create an affine widget to manipulate the actor
    # the widget currently only has a 2D representation and therefore applies
    # transforms in the X-Y plane only
    affine_widget = vtkAffineWidget(interactor=iren)
    affine_widget.CreateDefaultRepresentation()
    affine_widget.representation.PlaceWidget(sphere_actor.GetBounds())

    affine_widget.On()

    affine_callback = AffineCallback(sphere_actor, affine_widget.representation)

    affine_widget.AddObserver(vtkCallbackCommand.InteractionEvent, affine_callback)
    affine_widget.AddObserver(vtkCallbackCommand.EndInteractionEvent, affine_callback)

    iren.Start()


class AffineCallback(vtkCallbackCommand):
    def __init__(self, actor, affine_representation):
        super().__init__()

        self.actor = actor
        self.affine_rep = affine_representation
        self.transform = vtkTransform()

    def __call__(self, caller, ev):
        self.Execute(self, id, ev)

    def Execute(self, caller, id, event):
        self.affine_rep.GetTransform(self.transform)
        self.actor.SetUserTransform(self.transform)


@dataclass(frozen=True)
class Property:
    @dataclass(frozen=True)
    class Interpolation:
        VTK_FLAT: int = 0
        VTK_GOURAUD: int = 1
        VTK_PHONG: int = 2
        VTK_PBR: int = 3

    @dataclass(frozen=True)
    class Representation:
        VTK_POINTS: int = 0
        VTK_WIREFRAME: int = 1
        VTK_SURFACE: int = 2


if __name__ == '__main__':
    main()
