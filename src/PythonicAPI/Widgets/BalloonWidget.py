#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import (
    vtkRegularPolygonSource,
    vtkSphereSource
)
from vtkmodules.vtkInteractionWidgets import (
    vtkBalloonRepresentation,
    vtkBalloonWidget
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextProperty
)


def main():
    colors = vtkNamedColors()

    # Sphere.
    sphere_source = vtkSphereSource(center=(-4.0, 0.0, 0.0), radius=4.0)
    sphere_mapper = vtkPolyDataMapper()
    sphere_source >> sphere_mapper

    sphere_actor = vtkActor(mapper=sphere_mapper)
    sphere_actor.property.color = colors.GetColor3d('MistyRose')

    # Regular Polygon.
    regular_polygon_source = vtkRegularPolygonSource(center=(4.0, 0.0, 0.0), radius=4.0)
    regular_polygon_mapper = vtkPolyDataMapper()

    regular_polygon_source >> regular_polygon_mapper
    regular_polygon_actor = vtkActor(mapper=regular_polygon_mapper)
    regular_polygon_actor.property.color = colors.GetColor3d('Cornsilk')

    # A renderer and render window.
    ren = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(window_name='BalloonWidget')
    ren_win.AddRenderer(ren)

    # An interactor.
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    # Create the widget.
    # Do not set the justification.
    text_property = vtkTextProperty(color=colors.GetColor3d('Black'),
                                    bold=False, italic=False, shadow=False,
                                    font_size=16,
                                    )

    balloon_rep = vtkBalloonRepresentation(balloon_layout=vtkBalloonRepresentation.ImageRight,
                                           text_property=text_property)

    balloon_widget = vtkBalloonWidget(interactor=iren, representation=balloon_rep)
    balloon_widget.AddBalloon(sphere_actor, 'This is a sphere')
    balloon_widget.AddBalloon(regular_polygon_actor, 'This is a regular polygon')

    # Add the actors to the scene.
    ren.AddActor(sphere_actor)
    ren.AddActor(regular_polygon_actor)

    # Render an image (lights and cameras are created automatically).
    ren_win.Render()
    balloon_widget.enabled = True

    # Begin mouse interaction.
    iren.Start()
    iren.Initialize()


@dataclass(frozen=True)
class TextProperty:
    @dataclass(frozen=True)
    class Justification:
        VTK_TEXT_LEFT: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_RIGHT: int = 2

    @dataclass(frozen=True)
    class VerticalJustification:
        VTK_TEXT_BOTTOM: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_TOP: int = 2


if __name__ == '__main__':
    main()
