#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOImport import vtk3DSImporter
from vtkmodules.vtkRenderingCore import (
    vtkCamera,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    file_name = get_program_parameters()

    importer = vtk3DSImporter(file_name=file_name, compute_normals=True)

    colors = vtkNamedColors()

    renderer = vtkRenderer(gradient_background=True,
                           background=colors.GetColor3d('Wheat'),
                           background2=colors.GetColor3d('Gold'))
    ren_win = vtkRenderWindow(window_name='3DSImporter')
    iren = vtkRenderWindowInteractor()

    ren_win.AddRenderer(renderer)

    iren.render_window = ren_win
    importer.render_window = ren_win
    # importer.Read()
    importer.Update()

    actors = renderer.GetActors()  # This is a vtkActorCollection
    print('There are', actors.GetNumberOfItems(), 'actors.')

    ren_win.Render()
    camera = vtkCamera()
    camera.position = (0, -1, 0)
    camera.focal_point = (0, 0, 0)
    camera.view_up = (0, 0, 1)
    camera.Azimuth(150)
    camera.Elevation(30)

    renderer.SetActiveCamera(camera)
    renderer.ResetCamera()
    renderer.ResetCameraClippingRange()

    ren_win.Render()
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'Importing a 3ds file.'
    epilogue = '''
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='iflamingo.3ds.')
    args = parser.parse_args()
    return args.filename


if __name__ == '__main__':
    main()
