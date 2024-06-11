#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOGeometry import (
    vtkSTLReader,
    vtkSTLWriter
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
    description = 'Generate image data, then write a .stl file.'
    epilogue = '''
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)
    parser.add_argument('filename', help='A required stl filename.', nargs='?',
                        const='TestWriteSTL.ply',
                        type=str, default='TestWriteSTL.ply')
    args = parser.parse_args()
    return args.filename


def main():
    colors = vtkNamedColors()

    filename = get_program_parameters()

    sphere_source = vtkSphereSource()

    # Write the stl file to disk.
    stl_writer = vtkSTLWriter(file_name=filename)
    sphere_source >> stl_writer
    stl_writer.Write()

    # Read and display for verification.
    reader = vtkSTLReader(file_name=filename)

    mapper = vtkPolyDataMapper()
    reader >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('MistyRose')

    # Create a renderer, rendering window and interactor.
    ren = vtkRenderer(background=colors.GetColor3d('cobalt_green'))
    ren_win = vtkRenderWindow(window_name='WriteSTL')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Assign actor to the renderer.
    ren.AddActor(actor)

    # Enable user interface interactor.
    iren.Initialize()
    ren_win.Render()
    iren.Start()


if __name__ == '__main__':
    main()
