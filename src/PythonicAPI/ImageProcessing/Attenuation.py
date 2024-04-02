#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkSphere
from vtkmodules.vtkIOImage import vtkImageReader2Factory
from vtkmodules.vtkImagingCore import (
    vtkImageCast,
    vtkImageShiftScale
)
from vtkmodules.vtkImagingGeneral import vtkImageGaussianSmooth
from vtkmodules.vtkImagingHybrid import vtkSampleFunction
from vtkmodules.vtkImagingMath import vtkImageMathematics
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleImage
from vtkmodules.vtkRenderingCore import (
    vtkImageActor,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'This MRI image illustrates attenuation that can occur due to sensor position.'
    epilogue = '''
    The artifact is removed by dividing by the attenuation profile determined manually.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='AttenuationArtifact.pgm.')
    args = parser.parse_args()
    return args.filename


def main():
    colors = vtkNamedColors()

    file_name = get_program_parameters()

    # Read the image.
    reader = vtkImageReader2Factory().CreateImageReader2(file_name)
    reader.file_name = file_name

    cast = vtkImageCast(output_scalar_type=ImageCastOutputScalarType.VTK_DOUBLE)

    # Get rid of the discrete scalars.
    smooth = vtkImageGaussianSmooth(standard_deviations=(0.8, 0.8, 0))

    m1 = vtkSphere(center=(310, 130, 0), radius=0)
    m2 = vtkSampleFunction(implicit_function=m1, model_bounds=(0, 264, 0, 264, 0, 1), sample_dimensions=(264, 264, 1))
    m3 = vtkImageShiftScale(scale=0.000095)

    div = vtkImageMathematics(operation=ImageMathematicsOperation.VTK_MULTIPLY)

    # Create the actors.
    color_window = 256.0
    color_level = 127.5
    original_actor = vtkImageActor()
    original_actor.property.color_window = color_window
    original_actor.property.color_level = color_level

    filtered_actor = vtkImageActor()

    # Define the viewport ranges.
    # (xmin, ymin, xmax, ymax)
    original_viewport = [0.0, 0.0, 0.5, 1.0]
    filtered_viewport = [0.5, 0.0, 1.0, 1.0]

    # Set up the pipelines.
    p = reader >> cast
    p >> original_actor.mapper
    (p >> smooth, m2 >> m3) >> div >> filtered_actor.mapper

    # Set up the renderers.
    original_renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'), viewport=original_viewport)
    filtered_renderer = vtkRenderer(background=colors.GetColor3d('LightSlateGray'), viewport=filtered_viewport)

    original_renderer.AddActor(original_actor)
    filtered_renderer.AddActor(filtered_actor)

    original_renderer.ResetCamera()
    filtered_renderer.ResetCamera()

    render_window = vtkRenderWindow(size=(600, 300), window_name='Attenuation')
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


@dataclass(frozen=True)
class ImageMathematicsOperation:
    VTK_ADD: int = 0
    VTK_SUBTRACT: int = 1
    VTK_MULTIPLY: int = 2
    VTK_DIVIDE: int = 3
    VTK_INVERT: int = 4
    VTK_SIN: int = 5
    VTK_COS: int = 6
    VTK_EXP: int = 7
    VTK_LOG: int = 8
    VTK_ABS: int = 9
    VTK_SQR: int = 10
    VTK_SQRT: int = 11
    VTK_MIN: int = 12
    VTK_MAX: int = 13
    VTK_ATAN: int = 14
    VTK_ATAN2: int = 15
    VTK_MULTIPLYBYK: int = 16
    VTK_ADDC: int = 17
    VTK_CONJUGATE: int = 18
    VTK_COMPLEX_MULTIPLY: int = 19
    VTK_REPLACECBYK: int = 20


if __name__ == '__main__':
    main()
