#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOImage import vtkImageReader2Factory
from vtkmodules.vtkImagingColor import vtkImageMapToWindowLevelColors
from vtkmodules.vtkImagingCore import vtkImageExtractComponents
from vtkmodules.vtkImagingFourier import (
    vtkImageButterworthHighPass,
    vtkImageFFT,
    vtkImageIdealHighPass,
    vtkImageRFFT
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleImage
from vtkmodules.vtkRenderingCore import (
    vtkImageActor,
    vtkImageProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    file_name = get_program_parameters()

    # Read the image.
    reader = vtkImageReader2Factory().CreateImageReader2(file_name)
    reader.file_name = file_name

    fft = vtkImageFFT()
    p = (reader >> fft)

    ideal_high_pass = vtkImageIdealHighPass(x_cut_off=0.1, y_cut_off=0.1)
    ideal_rfft = vtkImageRFFT()
    ideal_real = vtkImageExtractComponents(components=0)

    butterworth_high_pass = vtkImageButterworthHighPass(x_cut_off=0.1, y_cut_off=0.1)
    butterworth_rfft = vtkImageRFFT()
    butterworth_real = vtkImageExtractComponents(components=0)

    # Create the actors.
    img_property = vtkImageProperty(interpolation_type=ImageProperty.InterpolationType.VTK_NEAREST_INTERPOLATION)

    ideal_color = vtkImageMapToWindowLevelColors(window=500, level=0)

    ideal_actor = vtkImageActor(property=img_property)
    p >> ideal_high_pass >> ideal_rfft >> ideal_real >> ideal_color >> ideal_actor.mapper

    butterworth_color = vtkImageMapToWindowLevelColors(window=500, level=0)

    butterworth_actor = vtkImageActor(property=img_property)
    p >> butterworth_high_pass >> butterworth_rfft >> butterworth_real >> butterworth_color >> butterworth_actor.mapper

    # Setup the renderers.
    ideal_renderer = vtkRenderer(background=colors.GetColor3d("LightSlateGray"), viewport=(0.0, 0.0, 0.5, 1.0))
    ideal_renderer.AddActor(ideal_actor)
    ideal_renderer.ResetCamera()

    butterworth_renderer = vtkRenderer(background=colors.GetColor3d("LightSlateGray"), viewport=(0.5, 0.0, 1.0, 1.0))
    butterworth_renderer.AddActor(butterworth_actor)
    butterworth_renderer.active_camera = ideal_renderer.active_camera

    render_window = vtkRenderWindow(size=(600, 300), window_name='IdealHighPass')
    render_window.AddRenderer(ideal_renderer)
    render_window.AddRenderer(butterworth_renderer)

    render_window_interactor = vtkRenderWindowInteractor()
    style = vtkInteractorStyleImage()
    render_window_interactor.interactor_style = style

    render_window_interactor.render_window = render_window
    ideal_renderer.active_camera.Dolly(1.4)
    ideal_renderer.ResetCameraClippingRange()
    render_window_interactor.Initialize()

    render_window_interactor.Start()


def get_program_parameters():
    import argparse
    description = 'This figure shows two high-pass filters in the frequency domain.'
    epilogue = '''
    The Butterworth high-pass filter has a gradual attenuation that avoids ringing
     produced by the ideal high-pass filter with an abrupt transition.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='fullhead15.png.')
    args = parser.parse_args()
    return args.filename


@dataclass(frozen=True)
class ImageProperty:
    @dataclass(frozen=True)
    class InterpolationType:
        VTK_NEAREST_INTERPOLATION: int = 0
        VTK_LINEAR_INTERPOLATION: int = 1
        VTK_CUBIC_INTERPOLATION: int = 2


if __name__ == '__main__':
    main()
