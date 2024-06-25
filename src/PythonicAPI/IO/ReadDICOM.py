#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOImage import vtkDICOMImageReader
from vtkmodules.vtkInteractionImage import vtkImageViewer2
from vtkmodules.vtkRenderingCore import vtkRenderWindowInteractor


def get_program_parameters():
    import argparse
    description = 'Read DICOM image data.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='prostate.img')
    args = parser.parse_args()
    return args.filename


def main():
    colors = vtkNamedColors()

    input_filename = get_program_parameters()

    # Read the DICOM file
    reader = vtkDICOMImageReader(file_name=input_filename)

    # Visualize
    image_viewer = vtkImageViewer2(input_connection=reader.output_port)
    render_window_interactor = vtkRenderWindowInteractor()
    image_viewer.SetupInteractor(render_window_interactor)
    image_viewer.Render()
    image_viewer.renderer.background = colors.GetColor3d('SlateGray')
    image_viewer.render_window.window_name = 'ReadDICOM'
    image_viewer.renderer.ResetCamera()
    image_viewer.Render()

    render_window_interactor.Start()


if __name__ == '__main__':
    main()
