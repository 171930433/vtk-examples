#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOImage import vtkImageReader2Factory
from vtkmodules.vtkImagingCore import vtkImageCast
from vtkmodules.vtkImagingGeneral import vtkImageGaussianSmooth
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleImage
from vtkmodules.vtkRenderingCore import (
    vtkImageActor,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Low-pass filters can be implemented as convolution with a Gaussian kernel.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='Gourds.png.')
    args = parser.parse_args()
    return args.filename


def main():
    colors = vtkNamedColors()

    file_name = get_program_parameters()

    # Read the image.
    reader = vtkImageReader2Factory().CreateImageReader2(file_name)
    reader.file_name = file_name

    # Process the image.
    cast = vtkImageCast(output_scalar_type=ImageCastOutputScalarType.VTK_FLOAT)

    smoothing_filter = vtkImageGaussianSmooth(dimensionality=2, standard_deviations=(4.0, 4.0),
                                              radius_factors=(2.0, 2.0))

    # Create the actors.
    original_actor = vtkImageActor()
    filtered_actor = vtkImageActor()

    # Set up the pipelines.
    reader >> original_actor.mapper
    reader >> cast >> smoothing_filter >> filtered_actor.mapper

    # Define the viewport ranges.
    # (xmin, ymin, xmax, ymax)
    original_viewport = [0.0, 0.0, 0.5, 1.0]
    filtered_viewport = [0.5, 0.0, 1.0, 1.0]

    # Setup the renderers.
    original_renderer = vtkRenderer(background=colors.GetColor3d("SlateGray"), viewport=original_viewport)
    filtered_renderer = vtkRenderer(background=colors.GetColor3d("LightSlateGray"), viewport=filtered_viewport)

    original_renderer.AddActor(original_actor)
    filtered_renderer.AddActor(filtered_actor)

    original_renderer.ResetCamera()
    filtered_renderer.ResetCamera()

    render_window = vtkRenderWindow(size=(600, 300), window_name='GaussianSmooth')
    render_window.AddRenderer(original_renderer)
    render_window.AddRenderer(filtered_renderer)

    render_window_interactor = vtkRenderWindowInteractor()
    style = vtkInteractorStyleImage()

    render_window_interactor.SetInteractorStyle(style)

    render_window_interactor.SetRenderWindow(render_window)
    render_window_interactor.Initialize()

    render_window_interactor.Start()


@dataclass(frozen=True)
class ImageCastOutputScalarType:
    VTK_CHAR: int = 2
    VTK_UNSIGNED_CHAR: int = 3
    VTK_SHORT: int = 4
    VTK_UNSIGNED_SHORT: int = 5
    VTK_INT: int = 6
    VTK_UNSIGNED_INT: int = 7
    VTK_LONG: int = 8
    VTK_UNSIGNED_LONG: int = 9
    VTK_FLOAT: int = 10
    VTK_DOUBLE: int = 11


if __name__ == '__main__':
    main()
