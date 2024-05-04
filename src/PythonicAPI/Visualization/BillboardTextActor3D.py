#!/usr/bin/env python3

import copy
from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingFreeType
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
# noinspection PyUnresolvedReferences
from vtkmodules.vtkCommonCore import vtkCommand
from vtkmodules.vtkCommonCore import (
    vtkMinimalStandardRandomSequence
)
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkBillboardTextActor3D,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # For testing
    rng = vtkMinimalStandardRandomSequence()
    # rng.seed = 8775070
    rng.seed = 5127

    # Create a renderer
    renderer = vtkRenderer(background=colors.GetColor3d('DarkSlateGray'))

    # Create a render window
    render_window = vtkRenderWindow(window_name='BillboardTextActor3D')
    render_window.AddRenderer(renderer)

    # Create an interactor
    iren = vtkRenderWindowInteractor()
    iren.render_window = render_window

    # Create a sphere
    sphere_source = vtkSphereSource(center=(0.0, 0.0, 0.0), radius=1.0)

    min_r = -10.0
    max_r = 10.0

    for i in range(0, 10):
        if i == 0:
            # Create an actor representing the origin
            mapper = vtkPolyDataMapper()
            sphere_source >> mapper

            actor = vtkActor(mapper=mapper)
            actor.position = (0, 0, 0)
            actor.property.color = colors.GetColor3d('Peacock')

            renderer.AddActor(actor)

        # Create a mapper
        mapper = vtkPolyDataMapper()
        sphere_source >> mapper

        # Create an actor
        actor = vtkActor(mapper=mapper)
        actor.position = (0, 0, 0)
        actor.property.color = colors.GetColor3d('MistyRose')

        # Set up the text and add it to the renderer
        text_actor = vtkBillboardTextActor3D()
        text_actor.input = ''
        text_actor.position = actor.position
        text_actor.text_property.font_size = 12
        text_actor.text_property.color = colors.GetColor3d('Gold')
        text_actor.text_property.justification = TextProperty.Justification.VTK_TEXT_CENTERED

        position = random_position(min_r, max_r, rng)
        actor.position = position

        # Position the text actor just above the sphere.
        dy = 1.2
        text_actor_position = copy.deepcopy(position)
        text_actor_position[1] += dy
        # If you want to use a callback, do this:
        observer = ActorCallback(text_actor, dy)
        actor.AddObserver(vtkCommand.NoEvent, observer(actor))
        # Otherwise do this:
        # label = f'{position[0]:0.3g}, {position[1]:0.3g}, {position[2]:0.3g}'
        # text_actor.position = text_actor_position
        # text_actor.input = label

        renderer.AddActor(actor)
        renderer.AddActor(text_actor)

    render_window.Render()
    iren.Start()


class ActorCallback:
    def __init__(self, text_actor, dy):
        self.text_actor = text_actor
        self.dy = dy

    def __call__(self, caller):
        position = caller.position
        text_actor_position = list(copy.deepcopy(position))
        text_actor_position[1] += self.dy
        label = f'{position[0]:0.3g}, {position[1]:0.3g}, {position[2]:0.3g}'
        self.text_actor.position = text_actor_position
        self.text_actor.input = label


def random_position(min_r, max_r, rng):
    p = list()
    for i in range(0, 3):
        p.append(rng.GetRangeValue(min_r, max_r))
        rng.Next()
    return p


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
