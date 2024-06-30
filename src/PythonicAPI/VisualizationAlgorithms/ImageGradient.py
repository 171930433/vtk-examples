#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOImage import vtkMetaImageReader
from vtkmodules.vtkImagingColor import vtkImageHSVToRGB
from vtkmodules.vtkImagingCore import (
    vtkImageCast,
    vtkImageConstantPad,
    vtkImageExtractComponents,
    vtkImageMagnify
)
from vtkmodules.vtkImagingGeneral import (
    vtkImageEuclideanToPolar,
    vtkImageGaussianSmooth,
    vtkImageGradient
)
from vtkmodules.vtkInteractionImage import vtkImageViewer
from vtkmodules.vtkRenderingCore import (
    vtkRenderWindowInteractor
)


def main():
    file_name = get_program_parameters()
    colors = vtkNamedColors()

    # Read the CT data of the human head.
    reader = vtkMetaImageReader(file_name=file_name)
    reader.update()

    cast = vtkImageCast(output_scalar_type=ImageCast.OutputScalarType.VTK_FLOAT)

    # Magnify the image.
    magnify = vtkImageMagnify(magnification_factors=(2, 2, 1), interpolate=True)

    # Smooth the data.
    # Remove high frequency artifacts due to linear interpolation.
    smooth = vtkImageGaussianSmooth(dimensionality=2, standard_deviations=(1.5, 1.5, 0.0),
                                    radius_factors=(2.01, 2.01, 0.0))

    # Compute the 2D gradient.
    gradient = vtkImageGradient(dimensionality=2)

    # Convert the data to polar coordinates.
    # The image magnitude is mapped into saturation value,
    # whilst the gradient direction is mapped into hue value.
    polar = vtkImageEuclideanToPolar(theta_maximum=255.0)

    # Add a third component to the data.
    # This is needed since the gradient filter only generates two components,
    #  and we need three components to represent color.
    pad = vtkImageConstantPad(output_number_of_scalar_components=3, constant=200)

    # At this point we have Hue, Value, Saturation.
    # Permute components so saturation will be constant.
    # Re-arrange components into HSV order.
    permute = vtkImageExtractComponents(components=(0, 2, 1))

    # Convert back into RGB values.
    rgb = vtkImageHSVToRGB(maximum=255.0)
    reader >> cast >> magnify >> smooth >> gradient >> polar >> pad >> permute >> rgb

    # Set up a viewer for the image.
    # Note that vtkImageViewer and vtkImageViewer2 are convenience wrappers around
    # vtkActor2D, vtkImageMapper, vtkRenderer, and vtkRenderWindow.
    # So all that needs to be supplied is the interactor.
    viewer = vtkImageViewer(z_slice=22, color_window=255.0, color_level=127.0,
                            input_connection=rgb.output_port)
    viewer.renderer.background = colors.GetColor3d('Silver')
    viewer.render_window.size = (512, 512)
    viewer.render_window.window_name = 'ImageGradient'

    # Create the RenderWindowInteractor.
    iren = vtkRenderWindowInteractor()
    viewer.SetupInteractor(iren)
    viewer.Render()

    iren.Initialize()
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'ImageGradient.'
    epilogue = '''
    Visualization of gradient information.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('fileName',
                        help='The file FullHead.mhd.'
                             'Note: file FullHead.raw.gz must also be present in the same folder.')
    args = parser.parse_args()
    return args.fileName


@dataclass(frozen=True)
class ImageCast:
    @dataclass(frozen=True)
    class OutputScalarType:
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
