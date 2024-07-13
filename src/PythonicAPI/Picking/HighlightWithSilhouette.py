# !/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkMinimalStandardRandomSequence
from vtkmodules.vtkFiltersHybrid import vtkPolyDataSilhouette
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkPropPicker,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Highlighting a selected object with a silhouette.'
    epilogue = '''
Click on the object to highlight it.
The selected object is highlighted with a silhouette.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('numberOfSpheres', nargs='?', type=int, default=10,
                        help='The number of spheres, default is 10.')
    args = parser.parse_args()
    return args.numberOfSpheres


def main():
    number_of_spheres = get_program_parameters()

    colors = vtkNamedColors()

    renderer = vtkRenderer(background=colors.GetColor3d('SteelBlue'))
    render_window = vtkRenderWindow(size=(640, 480), window_name='HighlightWithSilhouette')
    render_window.AddRenderer(renderer)

    # An interactor.
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window

    # Add the custom style.
    style = MouseInteractorHighLightActor()
    style.default_renderer = renderer

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

    # Render and interact.
    render_window.Render()

    # Create the silhouette pipeline, the input data will be set in the
    # interactor.
    silhouette = vtkPolyDataSilhouette(camera=renderer.active_camera)

    # Create mapper and actor for silhouette
    silhouette_mapper = vtkPolyDataMapper()
    silhouette >> silhouette_mapper

    silhouette_actor = vtkActor(mapper=silhouette_mapper)
    silhouette_actor.property.color = colors.GetColor3d("Tomato")
    silhouette_actor.property.line_width = 5

    # Set the custom type to use for interaction.
    style = MouseInteractorHighLightActor(silhouette, silhouette_actor)
    style.default_renderer = renderer

    # Start
    interactor.Initialize()
    interactor.interactor_style = style

    render_window.Render()

    interactor.Start()


class MouseInteractorHighLightActor(vtkInteractorStyleTrackballCamera):

    def __init__(self, silhouette=None, silhouette_actor=None):
        super().__init__()

        self.AddObserver("LeftButtonPressEvent", self.OnLeftButtonDown)

        self.last_picked_actor = None
        self.silhouette = silhouette
        self.silhouette_actor = silhouette_actor

    def OnLeftButtonDown(self, obj, event):
        click_pos = self.interactor.GetEventPosition()

        #  Pick from this location.
        picker = vtkPropPicker()
        picker.Pick(*click_pos, 0, self.default_renderer)
        self.last_picked_actor = picker.actor

        # If we picked something before, remove the silhouette actor and
        # generate a new one.
        if self.last_picked_actor:
            self.default_renderer.RemoveActor(self.silhouette_actor)

            # Highlight the picked actor by generating a silhouette.
            self.last_picked_actor.mapper.input >> self.silhouette
            self.GetDefaultRenderer().AddActor(self.silhouette_actor)

        #  Forward events
        super().OnLeftButtonDown()
        return

    def set_silhouette(self, silhouette):
        self.silhouette = silhouette

    def set_silhouette_actor(self, silhouette_actor):
        self.silhouette_actor = silhouette_actor


if __name__ == "__main__":
    main()
