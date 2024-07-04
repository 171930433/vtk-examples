#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonDataModel import vtkPlane
from vtkmodules.vtkFiltersCore import (
    vtkCutter,
    vtkImageAppend,
    vtkStripper,
    vtkTriangleFilter
)
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOImage import vtkPNGReader
from vtkmodules.vtkImagingStencil import (
    vtkImageStencil,
    vtkPolyDataToImageStencil
)
from vtkmodules.vtkInteractionImage import vtkImageViewer
from vtkmodules.vtkRenderingCore import vtkRenderWindowInteractor


def get_program_parameters():
    import argparse
    description = 'Converts the polydata to imagedata and masks the given imagedata.'
    epilogue = '''
        Contributed by: Peter Gruber

   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)
    parser.add_argument('filename', help='A filename e.g. fullhead15.png.')
    args = parser.parse_args()
    return args.filename


def main():
    fn = get_program_parameters()
    # A script to test the stencil filter with a polydata stencil.
    # Imaging pipeline.
    reader = vtkPNGReader(file_name=fn, data_spacing=(0.8, 0.8, 1.5), data_origin=(0.0, 0.0, 0.0))

    sphere = vtkSphereSource(phi_resolution=12, theta_resolution=12, center=(102, 102, 0), radius=60)
    triangle = vtkTriangleFilter()

    stripper = vtkStripper()

    data_to_stencil = vtkPolyDataToImageStencil(output_spacing=(0.8, 0.8, 1.5), output_origin=(0.0, 0.0, 0.0))
    sphere >> triangle >> stripper >> data_to_stencil

    stencil = vtkImageStencil(reverse_stencil=True, background_value=500)
    stencil.SetStencilConnection(data_to_stencil.GetOutputPort())
    reader >> stencil

    # Test again with a contour.
    reader2 = vtkPNGReader(file_name=fn, data_spacing=(0.8, 0.8, 1.5), data_origin=(0.0, 0.0, 0.0))
    plane = vtkPlane(origin=(0, 0, 0), normal=(0, 0, 1))
    cutter = vtkCutter(cut_function=plane)
    stripper2 = vtkStripper()
    data_to_stencil2 = vtkPolyDataToImageStencil(output_spacing=(0.8, 0.8, 1.5), output_origin=(0.0, 0.0, 0.0))
    stencil2 = vtkImageStencil()
    stencil2.SetStencilConnection(data_to_stencil2.GetOutputPort())
    stencil2.SetBackgroundValue(500)
    sphere >> cutter >> stripper2 >> data_to_stencil2
    reader2 >> stencil2

    image_append = vtkImageAppend()
    # Order is important here.
    stencil >> image_append
    image_append.AddInputConnection(stencil2.GetOutputPort())

    interator = vtkRenderWindowInteractor()
    viewer = vtkImageViewer(input_connection=image_append.output_port)
    viewer.SetupInteractor(interator)
    viewer.z_slice = 0
    viewer.color_window = 2000
    viewer.color_level = 1000
    viewer.render_window.window_name = 'PolyDataToImageDataStencil'

    viewer.Render()

    interator.Start()


if __name__ == '__main__':
    main()
