#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkMinimalStandardRandomSequence
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkPropPicker,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

colors = vtkNamedColors()


def get_program_parameters():
    import argparse
    description = 'Highlighting a selected object by changing its color and adding edge visibility.'

    epilogue = '''
Click on the object to highlight it.
The selected object is highlighted in red and the edges are visible.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('numberOfSpheres', nargs='?', type=int, default=10,
                        help='The number of spheres, default is 10.')
    args = parser.parse_args()
    return args.numberOfSpheres


def main():
    number_of_spheres = get_program_parameters()

    # A renderer and render window.
    renderer = vtkRenderer(background=colors.GetColor3d('SteelBlue'))
    renwin = vtkRenderWindow(size=(640, 480), window_name='HighlightPickedActor')
    renwin.AddRenderer(renderer)

    # An interactor.
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = renwin

    # Add the custom style.
    style = MouseInteractorHighLightActor()
    style.default_renderer = renderer
    interactor.interactor_style = style

    random_sequence = vtkMinimalStandardRandomSequence()
    # random_sequence.seed = 1043618065
    # random_sequence.seed = 5170
    random_sequence.seed = 8775070

    # Add spheres to play with.
    for i in range(number_of_spheres):
        # Random position and radius.
        x = random_sequence.GetRangeValue(-5.0, 5.0)
        random_sequence.Next()
        y = random_sequence.GetRangeValue(-5.0, 5.0)
        random_sequence.Next()
        z = random_sequence.GetRangeValue(-5.0, 5.0)
        random_sequence.Next()
        radius = random_sequence.GetRangeValue(0.5, 1.0)
        random_sequence.Next()

        source = vtkSphereSource(radius=radius, center=(x, y, z), phi_resolution=11, theta_resolution=21)

        mapper = vtkPolyDataMapper()
        source >> mapper
        actor = vtkActor(mapper=mapper)

        r = random_sequence.GetRangeValue(0.4, 1.0)
        random_sequence.Next()
        g = random_sequence.GetRangeValue(0.4, 1.0)
        random_sequence.Next()
        b = random_sequence.GetRangeValue(0.4, 1.0)
        random_sequence.Next()

        actor.property.diffuse_color = (r, g, b)
        actor.property.diffuse = 0.8
        actor.property.specular = 0.5
        actor.property.specular_color = colors.GetColor3d('White')
        actor.property.specular_power = 30.0

        renderer.AddActor(actor)

    # Start
    interactor.Initialize()
    renwin.Render()
    interactor.Start()


class MouseInteractorHighLightActor(vtkInteractorStyleTrackballCamera):

    def __init__(self, parent=None):
        super().__init__()

        self.AddObserver("LeftButtonPressEvent", self.left_button_press_event)

        self.new_picked_actor = None
        self.last_picked_actor = None
        self.last_picked_property = vtkProperty()

    def left_button_press_event(self, obj, event):
        click_pos = self.interactor.GetEventPosition()

        picker = vtkPropPicker()
        picker.Pick(*click_pos, 0, self.default_renderer)

        # Get the new actor.
        self.new_picked_actor = picker.actor

        # If something was selected.
        if self.new_picked_actor:
            # If we picked something before, reset its property.
            if self.last_picked_actor:
                self.last_picked_actor.GetProperty().DeepCopy(self.last_picked_property)

            # Save the property of the picked actor so that we can
            # restore it next time.
            self.last_picked_property.DeepCopy(self.new_picked_actor.property)
            # Highlight the picked actor by changing its properties.
            self.new_picked_actor.property.color = colors.GetColor3d('Red')
            self.new_picked_actor.property.diffuse = 1.0
            self.new_picked_actor.property.specular = 0.0
            self.new_picked_actor.property.edge_visibility = True

            # Save the last picked actor.
            self.last_picked_actor = self.new_picked_actor

        self.OnLeftButtonDown()
        return


if __name__ == '__main__':
    main()
