#!/usr/bin/env python3

"""
Demonstrate the use of a callback.

We also add call data.
"""

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
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
    parser.add_argument('-c', '--class_cb', action='store_false',
                        help='Use a class callback instead of a function  callback.')
    args = parser.parse_args()
    return args.class_cb


def main():
    #  Decide what approach to use.
    use_function_callback = get_program_parameters()

    colors = vtkNamedColors()

    # Create the Renderer, RenderWindow and RenderWindowInteractor.
    ren = vtkRenderer(background=colors.GetColor3d('MistyRose'))
    ren_win = vtkRenderWindow(size=(640, 640), window_name='CallBack')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Use a cone as a source with the golden ratio for the height. Because we can!
    source = vtkConeSource(center=(0, 0, 0), radius=1, height=1.6180339887498948482, resolution=128)

    # Pipeline
    mapper = vtkPolyDataMapper()
    source >> mapper
    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('Peacock')
    # Lighting
    actor.property.ambient = 0.6
    actor.property.diffuse = 0.2
    actor.property.specular = 1.0
    actor.property.specular_power = 20.0

    # Get an outline of the data set for context.
    outline = vtkOutlineFilter()
    outline_mapper = vtkPolyDataMapper()
    source >> outline >> outline_mapper
    outline_actor = vtkActor(mapper=outline_mapper)
    outline_actor.property.color = colors.GetColor3d('Black')
    outline_actor.property.line_width = 2

    # Add the actors to the renderer.
    ren.AddActor(actor)
    ren.AddActor(outline_actor)

    # Set up a nice camera position.
    camera = vtkCamera()
    camera.position = (4.6, -2.0, 3.8)
    camera.focal_point = (0.0, 0.0, 0.0)
    camera.clipping_range = (3.2, 10.2)
    camera.view_up = (0.3, 1.0, 0.13)
    ren.active_camera = camera

    ren_win.Render()

    rgb = [0.0] * 4
    colors.GetColor("Carrot", rgb)
    rgb = tuple(rgb[:3])
    widget = vtkOrientationMarkerWidget(orientation_marker=make_axes_actor(),
                                        interactor=iren, default_renderer=ren,
                                        outline_color=rgb, viewport=(0.0, 0.0, 0.2, 0.2), zoom=1.5, enabled=True,
                                        interactive=True)

    # Set up the callback.
    if use_function_callback:
        # We are going to output the camera position when the event
        #   is triggered, so we add the active camera as an attribute.
        get_orientation.cam = ren.active_camera
        # Register the callback with the object that is observing.
        iren.AddObserver('EndInteractionEvent', get_orientation)
    else:
        iren.AddObserver('EndInteractionEvent', OrientationObserver(ren.active_camera))
        # Or:
        # observer = OrientationObserver(ren.active_camera)
        # iren.AddObserver('EndInteractionEvent', observer)

    iren.Initialize()
    iren.Start()


def get_orientation(caller, ev):
    """
    Print out the orientation.

    We must do this before we register the callback in the calling function.
        GetOrientation.cam = ren.active_camera

    :param caller: The caller.
    :param ev: The event.
    :return:
    """
    # Just do this to demonstrate who called callback and the event that triggered it.
    print(caller.class_name, 'Event Id:', ev)
    # Now print the camera orientation.
    camera_orientation(get_orientation.cam)


class OrientationObserver:
    def __init__(self, cam):
        self.cam = cam

    def __call__(self, caller, ev):
        # Just do this to demonstrate who called callback and the event that triggered it.
        print(caller.class_name, 'Event Id:', ev)
        # Now print the camera orientation.
        camera_orientation(self.cam)


def camera_orientation(cam):
    flt_fmt = '9.6g'
    fmt = '{:' + flt_fmt + '}'
    print(f'{"Position:":>15s},{" ".join(map(fmt.format, cam.position))}')
    print(f'{"Focal point:":>15s},{" ".join(map(fmt.format, cam.focal_point))}')
    print(f'{"Clipping range:":>15s},{" ".join(map(fmt.format, cam.clipping_range))}')
    print(f'{"View up:":>15s},{" ".join(map(fmt.format, cam.view_up))}')
    print(f'{"Distance:":>15s},{cam.distance:{flt_fmt}}')


def make_axes_actor():
    axes = vtkAxesActor(shaft_type=vtkAxesActor.CYLINDER_SHAFT, tip_type=vtkAxesActor.CONE_TIP,
                        x_axis_label_text='X', y_axis_label_text='Y', z_axis_label_text='Z',
                        total_length=(1.0, 1.0, 1.0))
    axes.cylinder_radius = 1.25 * axes.cylinder_radius
    axes.cone_radius = 1.25 * axes.cone_radius
    axes.sphere_radius = 1.5 * axes.sphere_radius

    colors = vtkNamedColors()
    axes.x_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('FireBrick')
    axes.y_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('DarkGreen')
    axes.z_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('DarkBlue')

    return axes


if __name__ == '__main__':
    main()
