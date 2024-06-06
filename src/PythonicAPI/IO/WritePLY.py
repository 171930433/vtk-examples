# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOPLY import (
    vtkPLYReader,
    vtkPLYWriter
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
    description = 'Generate image data, then write a .ply file.'
    epilogue = '''
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)
    parser.add_argument('filename', help='A required ply filename.', nargs='?',
                        const='TestWritePLY.ply',
                        type=str, default='TestWritePLY.ply')
    args = parser.parse_args()
    return args.filename


def main():
    colors = vtkNamedColors()

    file_name = get_program_parameters()

    sphere_source = vtkSphereSource()

    ply_writer = vtkPLYWriter(file_name=file_name)
    sphere_source >> ply_writer
    ply_writer.Write()

    # Read and display for verification.
    reader = vtkPLYReader(file_name=file_name)

    mapper = vtkPolyDataMapper()
    reader >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('MistyRose')

    renderer = vtkRenderer()
    render_window = vtkRenderWindow(window_name='WritePLY')
    render_window.AddRenderer(renderer)

    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d('cobalt_green'))

    render_window.Render()
    render_window_interactor.Start()


if __name__ == '__main__':
    main()
