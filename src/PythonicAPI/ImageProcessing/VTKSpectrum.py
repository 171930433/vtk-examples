#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOImage import vtkImageReader2Factory
from vtkmodules.vtkImagingCore import vtkImageMapToColors
from vtkmodules.vtkImagingFourier import (
    vtkImageFFT,
    vtkImageFourierCenter
)
from vtkmodules.vtkImagingMath import (
    vtkImageLogarithmicScale,
    vtkImageMagnitude
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleImage
from vtkmodules.vtkRenderingCore import (
    vtkImageActor,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkWindowLevelLookupTable
)


def get_program_parameters():
    import argparse
    description = 'The discrete Fourier transform.'
    epilogue = '''
    This changes an image from the spatial domain into the frequency domain,
     where each pixel represents a sinusoidal function.
    This figure shows an image and its power spectrum displayed using a logarithmic transfer function.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='vtks.pgm.')
    args = parser.parse_args()
    return args.filename


def main():
    colors = vtkNamedColors()

    file_name = get_program_parameters()

    # Read the image.
    reader = vtkImageReader2Factory().CreateImageReader2(file_name)
    reader.file_name = file_name

    # The fft stuff.
    fft = vtkImageFFT()
    mag = vtkImageMagnitude()
    center = vtkImageFourierCenter()
    compress = vtkImageLogarithmicScale(constant=15)

    # Create the actors.
    original_actor = vtkImageActor()
    original_actor.property.interpolation_type = VolumeProperty_InterpolationType.VTK_NEAREST_INTERPOLATION

    compressed_actor = vtkImageActor()
    compressed_actor.property.interpolation_type = VolumeProperty_InterpolationType.VTK_NEAREST_INTERPOLATION
    create_image_actor(compressed_actor, 160, 120)

    # Set up the pipelines.
    reader >> original_actor.mapper
    reader >> fft >> mag >> center >> compress >> compressed_actor.mapper

    # Define the viewport ranges.
    # (xmin, ymin, xmax, ymax)
    original_viewport = [0.0, 0.0, 0.5, 1.0]
    compressed_viewport = [0.5, 0.0, 1.0, 1.0]

    # Setup the renderers.
    original_renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'), viewport=original_viewport)
    compressed_renderer = vtkRenderer(background=colors.GetColor3d('LightSlateGray'), viewport=compressed_viewport)

    original_renderer.AddActor(original_actor)
    compressed_renderer.AddActor(compressed_actor)

    original_renderer.ResetCamera()
    compressed_renderer.ResetCamera()

    render_window = vtkRenderWindow(size=(600, 300), window_name='VTKSpectrum')
    render_window.AddRenderer(original_renderer)
    render_window.AddRenderer(compressed_renderer)

    render_window_interactor = vtkRenderWindowInteractor()
    style = vtkInteractorStyleImage()
    render_window_interactor.SetInteractorStyle(style)
    render_window_interactor.SetRenderWindow(render_window)
    render_window_interactor.Initialize()

    render_window_interactor.Start()


def create_image_actor(actor, color_window, color_level):
    wlut = vtkWindowLevelLookupTable(window=color_window, level=color_level)
    wlut.Build()

    # Map the image through the lookup table.
    color = vtkImageMapToColors(lookup_table=wlut)
    actor.mapper.input >> color
    color >> actor.mapper
    return


@dataclass(frozen=True)
class VolumeProperty_InterpolationType:
    VTK_NEAREST_INTERPOLATION: int = 0
    VTK_LINEAR_INTERPOLATION: int = 1
    VTK_CUBIC_INTERPOLATION: int = 2


if __name__ == '__main__':
    main()
