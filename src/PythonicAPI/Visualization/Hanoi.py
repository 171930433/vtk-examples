#!/usr/bin/env python3

#  Translated from Hanoi.cxx.

from dataclasses import dataclass
from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkMinimalStandardRandomSequence
from vtkmodules.vtkFiltersSources import (
    vtkCylinderSource,
    vtkPlaneSource
)
from vtkmodules.vtkIOImage import (
    vtkBMPWriter,
    vtkJPEGWriter,
    vtkPNGWriter,
    vtkPNMWriter,
    vtkPostScriptWriter,
    vtkTIFFWriter
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkWindowToImageFilter
)


def get_program_parameters():
    import argparse
    description = 'Towers of Hanoi. .'
    epilogue = '''
Where:  -p specifies the number of pucks.
        -s specifies the number of steps (the speed of the simulation).
        -r specifies the puck resolution (number of sides).
        -c specifies configuration.
            0 final configuration.
            1 initial configuration.
            2 intermediate configuration.
            3 final configuration and save images
Defaults:  -p 5 -s 5 -r 48 -c 0
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--number_of_pucks', '-p', default=5, type=int, nargs='?',
                        help='The number of pucks.')
    parser.add_argument('--number_of_steps', '-s', default=5, type=int, nargs='?',
                        help='The number of steps (the speed of the simulation).')
    parser.add_argument('--puck_resolution', '-r', default=48, type=int, nargs='?',
                        help='The puck resolution (number of sides).')
    parser.add_argument('--configuration', '-c', default=0, type=int, nargs='?',
                        help='The configuration.')
    args = parser.parse_args()
    return args.number_of_pucks, args.number_of_steps, args.puck_resolution, args.configuration


class GV:
    """
    Used to store global variables.
    """

    def __init__(self, number_of_pucks=5, number_of_steps=5, puck_resolution=48, configuration=0):
        self.number_of_pucks = number_of_pucks
        self.number_of_steps = number_of_steps
        self.puck_resolution = puck_resolution
        self.configuration = configuration
        self.got_figure2 = False  # Used to bail out of recursion if configuration == 2.
        self.puck_height = 1.0  # Puck height.
        self.peg_height = 1.1 * self.number_of_pucks * self.puck_height  # Peg height.
        self.peg_radius = 0.5  # Peg radius.
        self.r_min = 4.0 * self.peg_radius  # The minimum allowable radius of disks.
        self.r_max = 12.0 * self.peg_radius  # The maximum allowable radius of disks
        self.distance_between_pegs = 1.1 * 1.25 * self.r_max  # The distance between the pegs.
        self.number_of_moves = 0

    def update(self, number_of_pucks, number_of_steps, puck_resolution, configuration):
        self.number_of_pucks = number_of_pucks
        self.number_of_steps = number_of_steps
        self.puck_resolution = puck_resolution
        self.configuration = configuration
        self.peg_height = 1.1 * self.number_of_pucks * self.puck_height  # Peg height.


# Globals
gv = GV()
ren_win = vtkRenderWindow(size=(1200, 750), window_name='Hanoi')

"""
   For peg_stack we use a list of lists where the sublist correspond to the
      source, target and helper pegs.
   Python lists can be used as a stack since they have append() (corresponding
      to push()) and pop().
"""
peg_stack = [[vtkActor], [vtkActor], [vtkActor]]


def hanoi():

    colors = vtkNamedColors()

    # Create the renderer and render window interactor.
    ren = vtkRenderer(background=colors.GetColor3d('PapayaWhip'))
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    camera = vtkCamera()
    camera.position = (41.0433, 27.9637, 30.442)
    camera.focal_point = (11.5603, -1.51931, 0.95899)
    camera.clipping_range = (18.9599, 91.6042)
    camera.view_up = (0, 1, 0)

    ren.SetActiveCamera(camera)

    # Create the geometry for the table, pegs, and pucks.
    peg_geometry = vtkCylinderSource(resolution=8)
    peg_mapper = vtkPolyDataMapper()
    peg_geometry >> peg_mapper

    puck_geometry = vtkCylinderSource(resolution=gv.puck_resolution)
    puck_mapper = vtkPolyDataMapper()
    puck_geometry >> puck_mapper

    table_top_geometry = vtkPlaneSource(resolution=(10, 10))
    table_mapper = vtkPolyDataMapper()
    table_top_geometry >> table_mapper

    # Create the actors: table_top, pegs, and pucks
    # The table
    table_top = vtkActor(mapper=table_mapper)
    ren.AddActor(table_top)
    # table_top.property.color = (0.9569, 0.6431, 0.3765)
    table_top.property.color = colors.GetColor3d('SaddleBrown')
    table_top.AddPosition(gv.distance_between_pegs, 0, 0)
    table_top.scale = (4 * gv.distance_between_pegs, 2 * gv.distance_between_pegs, 3 * gv.distance_between_pegs)
    table_top.RotateX(90)

    # The pegs (using cylinder geometry).  Note that the pegs have to translated
    # in the y-direction because the cylinder is centered about the origin.
    gv.peg_height = 1.1 * gv.number_of_pucks * gv.puck_height
    for i in range(0, 3):
        peg = vtkActor(mapper=peg_mapper)
        peg.property.color = colors.GetColor3d('Lavender')
        peg.AddPosition(i * gv.distance_between_pegs, gv.peg_height / 2, 0)
        peg.scale = (1, gv.peg_height, 1)
        ren.AddActor(peg)

    # The pucks (using cylinder geometry). Always loaded on peg# 0.
    random_sequence = vtkMinimalStandardRandomSequence()
    random_sequence.SetSeed(1)
    for i in range(0, gv.number_of_pucks):
        puck_actor: vtkActor = vtkActor(mapper=puck_mapper)
        color = [0, 0, 0]
        for j in range(0, 3):
            color[j] = random_sequence.GetValue()
            random_sequence.Next()
        puck_actor.property.color = color
        puck_actor.AddPosition(0, i * gv.puck_height + gv.puck_height / 2, 0)
        scale = gv.r_max - i * (gv.r_max - gv.r_min) / (gv.number_of_pucks - 1)
        puck_actor.scale = (scale, 1, scale)
        ren.AddActor(puck_actor)
        peg_stack[0].append(puck_actor)

    # Reset the camera to view all actors.
    ren_win.Render()

    if gv.configuration == 3:
        write_image('hanoi0.png', ren_win, rgba=False)

    if gv.configuration != 1:
        # Begin recursion.
        tower_of_hanoi(gv.number_of_pucks - 1, 0, 2, 1)
        tower_of_hanoi(1, 0, 1, 2)
        if not gv.got_figure2:
            tower_of_hanoi(gv.number_of_pucks - 1, 2, 1, 0)

            ren_win.Render()
            if gv.configuration == 3:
                write_image('hanoi2.png', ren_win, rgba=False)
        # Report output.
        s = 'Number of moves: {:d}\nPolygons rendered each frame: {:d}\nTotal number of frames: {:d}'
        print(s.format(gv.number_of_moves, 3 * 8 + 1 + gv.number_of_pucks * (2 + gv.puck_resolution),
                       gv.number_of_moves * 3 * gv.number_of_steps))

    iren.AddObserver('EndInteractionEvent', OrientationObserver(ren.active_camera))

    # Render the image.
    iren.Initialize()
    iren.Start()


def verify_parameters(max_pucks):
    number_of_pucks, number_of_steps, puck_resolution, configuration = get_program_parameters()
    number_of_pucks = abs(number_of_pucks)
    number_of_steps = abs(number_of_steps)
    puck_resolution = abs(puck_resolution)
    configuration = abs(configuration)
    check = True
    if number_of_pucks < 2:
        print('Please use more pucks!')
        check = False
    if number_of_pucks > max_pucks:
        print('Too many pucks specified! Maximum is', max_pucks)
        check = False
    if number_of_steps < 3:
        print('Please use more steps!')
        check = False
    if configuration > 3:
        print('0 >= configuration <= 3')
        check = False
    if check:
        gv.update(number_of_pucks, number_of_steps, puck_resolution, configuration)
    return check


def move_puck(peg1, peg2):
    """
    This routine is responsible for moving pucks from peg1 to peg2.
    :param peg1: Initial peg.
    :param peg2: Final peg.
    :return:
    """
    gv.number_of_moves += 1

    # Get the actor to move
    moving_actor = peg_stack[peg1].pop()

    # Get the distance to move up.
    position = (0, (gv.peg_height - (gv.puck_height * (len(peg_stack[peg1]) - 1)) + gv.r_max) / gv.number_of_steps, 0)

    for i in range(0, gv.number_of_steps):
        moving_actor.AddPosition(position)
        ren_win.Render()

    # Get the distance to move across
    distance = (peg2 - peg1) * gv.distance_between_pegs / gv.number_of_steps
    flip_angle = 180.0 / gv.number_of_steps
    for i in range(0, gv.number_of_steps):
        moving_actor.AddPosition(distance, 0, 0)
        moving_actor.RotateX(flip_angle)
        if gv.number_of_moves == 13 and i == 3:  # For making the book image.
            if gv.configuration == 3 or gv.configuration == 2:
                cam = ren_win.renderers.first_renderer.active_camera
                camera1 = vtkCamera()
                camera1.position = (54.7263, 41.6467, 44.125)
                camera1.focal_point = (11.5603, -1.51931, 0.95899)
                camera1.clipping_range = (42.4226, 115.659)
                camera1.view_up = (0, 1, 0)
                ren_win.renderers.first_renderer.active_camera = camera1
                if gv.configuration == 3:
                    write_image('hanoi1.png', ren_win, rgba=False)
                if gv.configuration == 2:
                    gv.got_figure2 = True
                    break
                ren_win.renderers.first_renderer.active_camera = cam
                ren_win.Render()
    if gv.got_figure2:
        peg_stack[peg2].append(moving_actor)
        return

    # Get the distance to move down.
    position = (0, ((gv.puck_height * (len(peg_stack[peg2]) - 1)) - gv.peg_height - gv.r_max) / gv.number_of_steps, 0)

    for i in range(0, gv.number_of_steps):
        moving_actor.AddPosition(position)
        ren_win.Render()
    peg_stack[peg2].append(moving_actor)


def tower_of_hanoi(n, peg1, peg2, peg3):
    """
    Tower of Hanoi.
    :param n: Number of disks.
    :param peg1: Source
    :param peg2: Target
    :param peg3: Helper
    :return:
    """
    # If got_figure2 is true, we break out of the recursion.
    if gv.got_figure2:
        return
    if n != 1:
        tower_of_hanoi(n - 1, peg1, peg3, peg2)
        if gv.got_figure2:
            return
        tower_of_hanoi(1, peg1, peg2, peg3)
        tower_of_hanoi(n - 1, peg3, peg2, peg1)
    else:
        move_puck(peg1, peg2)


class OrientationObserver:
    def __init__(self, cam):
        self.cam = cam

    def __call__(self, caller, ev):
        # Just do this to demonstrate who called callback and the event that triggered it.
        print(caller.class_name, 'Event Id:', ev)
        # Now print the camera orientation.
        camera_orientation(self.cam)


def camera_orientation(cam):
    res = f'\tcamera = ren.active_camera\n'
    res += f'\tcamera.position = ({", ".join(map("{0:0.6f}".format, cam.position))})\n'
    res += f'\tcamera.focal_point = ({", ".join(map("{0:0.6f}".format, cam.focal_point))})\n'
    res += f'\tcamera.view_up = ({", ".join(map("{0:0.6f}".format, cam.view_up))})\n'
    res += f'\tcamera.distance = {"{0:0.6f}".format(cam.GetDistance())}\n'
    res += f'\tcamera.clipping_range = ({", ".join(map("{0:0.6f}".format, cam.clipping_range))})\n'
    print(res)


def write_image(file_name, ren_window, rgba=True):
    """
    Write the render window view to an image file.

    Image types supported are:
     BMP, JPEG, PNM, PNG, PostScript, TIFF.
    The default parameters are used for all writers, change as needed.

    :param file_name: The file name, if no extension then PNG is assumed.
    :param ren_window: The render window.
    :param rgba: Used to set the buffer type.
    :return:
    """

    if file_name:
        valid_suffixes = ['.bmp', '.jpg', '.png', '.pnm', '.ps', '.tiff']
        # Select the writer to use.
        parent = Path(file_name).resolve().parent
        path = Path(parent) / file_name
        if path.suffix:
            ext = path.suffix.lower()
        else:
            ext = '.png'
            path = Path(str(path)).with_suffix(ext)
        if path.suffix not in valid_suffixes:
            print(f'No writer for this file suffix: {ext}')
            return

        if ext == '.ps':
            rgba = False

        wtif = vtkWindowToImageFilter(input=ren_window, scale=1)
        if rgba:
            wtif.input_buffer_type = WindowToImageFilter.InputBufferType.VTK_RGBA
        else:
            wtif.SetInputBufferTypeToRGB()
            wtif.input_buffer_type = WindowToImageFilter.InputBufferType.VTK_RGB
            # Do not read from the front buffer.
            wtif.read_front_buffer = False
            wtif.update()

        if ext == '.bmp':
            writer = vtkBMPWriter(file_name=path)
        elif ext == '.jpg':
            writer = vtkJPEGWriter(file_name=path)
        elif ext == '.pnm':
            writer = vtkPNMWriter(file_name=path)
        elif ext == '.ps':
            writer = vtkPostScriptWriter(file_name=path)
        elif ext == '.tiff':
            writer = vtkTIFFWriter(file_name=path)
        else:
            writer = vtkPNGWriter(file_name=path)

        wtif >> writer
        writer.Write()
    else:
        raise RuntimeError('Need a filename.')


@dataclass(frozen=True)
class WindowToImageFilter:
    @dataclass(frozen=True)
    class InputBufferType:
        VTK_RGB: int = 3
        VTK_RGBA: int = 4
        VTK_ZBUFFER: int = 5


def main():
    max_pucks = 20
    if not verify_parameters(max_pucks):
        return
    hanoi()

if __name__ == '__main__':
    main()
