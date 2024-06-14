#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOPLY import vtkPLYReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkRenderingOpenGL2 import (
    vtkRenderStepsPass,
    vtkSimpleMotionBlurPass
)


def main():
    file_name = get_program_parameters()

    colors = vtkNamedColors()

    colors.SetColor('A1Diff', 255, 204, 77, 255)
    colors.SetColor('A2Amb', 51, 51, 255, 255)
    colors.SetColor('A2Diff', 51, 255, 204, 255)
    colors.SetColor('A3Amb', 128, 166, 255, 255)
    colors.SetColor('Bkg', 77, 102, 153, 255)

    renderer = vtkRenderer(background=colors.GetColor3d('Bkg'))
    render_window = vtkRenderWindow(size=(500, 500), window_name='MotionBlur')
    render_window.AddRenderer(renderer)
    iren = vtkRenderWindowInteractor()
    iren.render_window = render_window

    reader = vtkPLYReader(file_name=file_name)

    mapper = vtkPolyDataMapper()
    reader >> mapper

    # Create three models using the same mapper.

    actor = vtkActor(mapper=mapper)
    actor.property.ambient_color = colors.GetColor3d('Red')
    actor.property.diffuse_color = colors.GetColor3d('A1Diff')
    actor.property.specular = 0.0
    actor.property.diffuse = 0.5
    actor.property.ambient = 0.3
    actor.position = (-0.1, 0.0, -0.1)
    renderer.AddActor(actor)

    actor = vtkActor(mapper=mapper)
    actor.property.ambient_color = colors.GetColor3d('A2Amb')
    actor.property.diffuse_color = colors.GetColor3d('A2Diff')
    actor.property.specular_color = colors.GetColor3d('Black')
    actor.property.specular = 0.2
    actor.property.diffuse = 0.9
    actor.property.ambient = 0.1
    actor.property.specular_power = 10.0
    renderer.AddActor(actor)

    actor = vtkActor(mapper=mapper)
    actor.property.diffuse_color = colors.GetColor3d('A3Amb')
    actor.property.specular_color = colors.GetColor3d('White')
    actor.property.specular = 0.7
    actor.property.diffuse = 0.4
    actor.property.specular_power = 60.0
    actor.position = (0.1, 0.0, 0.1)
    renderer.AddActor(actor)

    render_window.SetMultiSamples(0)

    # Create the basic VTK render steps.
    basic_passes = vtkRenderStepsPass()

    motion = vtkSimpleMotionBlurPass()
    motion.SetDelegatePass(basic_passes)

    # Tell the renderer to use our render pass pipeline.
    renderer.SetPass(motion)

    num_renders = 30

    renderer.active_camera.position = (0, 0, -1)
    renderer.active_camera.focal_point = (0, 0, 0)
    renderer.active_camera.view_up = (0, 1, 0)
    renderer.ResetCamera()
    renderer.active_camera.Azimuth(15.0)
    renderer.active_camera.Zoom(1.2)

    render_window.Render()

    for i in range(0, num_renders):
        renderer.active_camera.Azimuth(10.0 / num_renders)
        renderer.active_camera.Elevation(10.0 / num_renders)
        render_window.Render()

    iren.Start()


def get_program_parameters():
    import argparse
    description = 'Example of motion blur.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='Armadillo.ply.')
    args = parser.parse_args()
    return args.filename


if __name__ == '__main__':
    main()
