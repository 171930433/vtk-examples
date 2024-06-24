#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkInteractionWidgets import (
    vtkBoxWidget2,
    vtkBoxRepresentation
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Demonstrate two ways of using callbacks.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-f', '--fn_cb', action='store_false',
                        help='Use a function callback instead of a class callback.')
    args = parser.parse_args()
    return args.fn_cb


def main():
    #  Decide what approach to use.
    use_class_callback = get_program_parameters()

    colors = vtkNamedColors()

    # Create a Cone.
    cone = vtkConeSource(resolution=20)
    cone_mapper = vtkPolyDataMapper()
    cone >> cone_mapper
    cone_actor = vtkActor(mapper=cone_mapper)
    cone_actor.property.color = colors.GetColor3d('BurlyWood')

    # A renderer and render window.
    renderer = vtkRenderer(background=colors.GetColor3d('Blue'))
    renderer.AddActor(cone_actor)

    ren_win = vtkRenderWindow(window_name='BoxWidget2')
    ren_win.AddRenderer(renderer)
    ren_win.SetWindowName('BoxWidget')

    # An interactor.
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = ren_win

    # Define a representation to add to the box widget.
    # Of course, if we create the box widget first, we can bypass this step
    # and use the default representation like this:
    # box_widget.representation.SetPlaceFactor(1.0)
    # box_widget.representation.PlaceWidget(cone_actor.bounds)
    # We use a place_factor of 1.0 to make the box 1.0x larger than the actor.
    representation = vtkBoxRepresentation(place_factor=1.0)
    representation.PlaceWidget(cone_actor.bounds)

    # A Box widget.
    box_widget = vtkBoxWidget2(interactor=interactor, representation=representation)

    # Set up and register the callback with the object that it is observing.
    if use_class_callback:
        box_widget.AddObserver('InteractionEvent', BoxCallback(cone_actor))
        # Or:
        # box_callback = BoxCallback(cone_actor)
        # box_widget.AddObserver('InteractionEvent', box_callback)
    else:
        # We are going to update the cone actor when the event
        #   is triggered, so we add the cone actor as an attribute.
        box_callback.actor = cone_actor
        box_widget.AddObserver('EndInteractionEvent', box_callback)

    # Start
    ren_win.Render()
    # After the render we can turn on the box widget.
    box_widget.On()

    interactor.Start()


class BoxCallback:
    def __init__(self, actor):
        self.actor = actor

    def __call__(self, caller, ev):
        # Just do this to demonstrate who called callback and the event that triggered it.
        # print(caller.class_name, 'Event Id:', ev)
        t = vtkTransform()
        caller.representation.GetTransform(t)
        self.actor.user_transform = t


def box_callback(obj, ev):
    # Just do this to demonstrate who called callback and the event that triggered it.
    # print(obj.class_name, 'Event Id:', ev)
    t = vtkTransform()
    obj.representation.GetTransform(t)
    # Remember to add the actor as an attribute before registering
    # this callback with the object that it is observing.
    box_callback.actor.user_transform = t


if __name__ == '__main__':
    main()
