#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkImagingCore import vtkImageCast
from vtkmodules.vtkImagingGeneral import vtkImageNormalize
from vtkmodules.vtkImagingSources import vtkImageSinusoidSource
from vtkmodules.vtkRenderingCore import (
    vtkImageActor,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Create an image.
    source = vtkImageSinusoidSource()

    # Create the filters.
    input_cast_filter = vtkImageCast(output_scalar_type=ImageCast.OutputScalarType.VTK_UNSIGNED_CHAR)
    normalize_filter = vtkImageNormalize()
    normalize_cast_filter = vtkImageCast(output_scalar_type=ImageCast.OutputScalarType.VTK_UNSIGNED_CHAR)

    # Create actors.
    input_actor = vtkImageActor()
    normalized_actor = vtkImageActor()

    # Set up the pipelines.
    source >> input_cast_filter >> input_actor.mapper
    source >> normalize_filter >> normalize_cast_filter >> normalized_actor.mapper

    # There will be one render window.
    render_window = vtkRenderWindow(size=(600, 300), window_name='ImageNormalize')

    # And one interactor
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window

    # Define viewport ranges
    # (xmin, ymin, xmax, ymax)
    left_viewport = [0.0, 0.0, 0.5, 1.0]
    right_viewport = [0.5, 0.0, 1.0, 1.0]

    # Setup both renderers
    left_renderer = vtkRenderer(background=colors.GetColor3d('Sienna'), viewport=left_viewport)

    right_renderer = vtkRenderer(background=colors.GetColor3d('SteelBlue'), viewport=right_viewport)

    render_window.AddRenderer(left_renderer)
    render_window.AddRenderer(right_renderer)

    left_renderer.AddActor(input_actor)
    right_renderer.AddActor(normalized_actor)

    left_renderer.ResetCamera()
    right_renderer.ResetCamera()

    render_window.Render()
    interactor.Start()


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
