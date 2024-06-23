#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkInteractionWidgets import vtkBoxWidget
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

    # Create a Cone
    cone = vtkConeSource(resolution=20)
    cone_mapper = vtkPolyDataMapper()
    cone >> cone_mapper
    cone_actor = vtkActor(mapper=cone_mapper)
    cone_actor.property.color = colors.GetColor3d('BurlyWood')

    # A renderer and render window.
    renderer = vtkRenderer(background=colors.GetColor3d('Blue'))
    renderer.AddActor(cone_actor)

    ren_win = vtkRenderWindow(window_name='BoxWidget')
    ren_win.AddRenderer(renderer)
    ren_win.SetWindowName('BoxWidget')

    # An interactor.
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = ren_win

    # A Box widget
    # We use a place_factor of 1.25 to make the box 1.25x larger than the actor.
    box_widget = vtkBoxWidget(interactor=interactor, prop3d=cone_actor, place_factor=1.25)
    box_widget.PlaceWidget()
    box_widget.On()

    # Set up and register the callback with the object that it is observing.
    if use_class_callback:
        box_widget.AddObserver('InteractionEvent', BoxCallback())
        # Or:
        # box_callback = BoxCallback()
        # box_widget.AddObserver('InteractionEvent', box_callback)
    else:
        box_widget.AddObserver('EndInteractionEvent', box_callback)

    # Start
    interactor.Initialize()
    ren_win.Render()
    interactor.Start()


class BoxCallback:
    def __call__(self, caller, ev):
        # Just do this to demonstrate who called callback and the event that triggered it.
        # print(caller.class_name, 'Event Id:', ev)
        t = vtkTransform()
        caller.GetTransform(t)
        caller.prop3d.user_transform = t


def box_callback(obj, event):
    t = vtkTransform()
    obj.GetTransform(t)
    obj.prop3d.user_transform = t


if __name__ == '__main__':
    main()
