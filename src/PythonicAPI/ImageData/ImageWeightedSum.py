#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkImagingCore import vtkImageCast
from vtkmodules.vtkImagingMath import vtkImageWeightedSum
from vtkmodules.vtkImagingSources import (
    vtkImageMandelbrotSource,
    vtkImageSinusoidSource
)
from vtkmodules.vtkRenderingCore import (
    vtkImageActor,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Create image 1.
    source1 = vtkImageMandelbrotSource(whole_extent=(0, 255, 0, 255, 0, 0))
    # We need this for the image weighted sum.
    source1_double = vtkImageCast(output_scalar_type=ImageCast.OutputScalarType.VTK_DOUBLE)
    # Create image 2.
    source2 = vtkImageSinusoidSource(whole_extent=(0, 255, 0, 255, 0, 0))
    # Do the sum.
    # A weight is (id, weight).
    weights = ((0, 0.8), (1, 0.2))
    sum_filter = vtkImageWeightedSum()
    for weight in weights:
        sum_filter.SetWeight(*weight)

    # Display the images.
    source1_cast_filter = vtkImageCast(output_scalar_type=ImageCast.OutputScalarType.VTK_UNSIGNED_CHAR)
    source2_cast_filter = vtkImageCast(output_scalar_type=ImageCast.OutputScalarType.VTK_UNSIGNED_CHAR)
    summed_cast_filter = vtkImageCast(output_scalar_type=ImageCast.OutputScalarType.VTK_UNSIGNED_CHAR)

    # Create actors.
    source1_actor = vtkImageActor()
    source2_actor = vtkImageActor()
    summed_actor = vtkImageActor()

    # Set up the pipelines.
    source1 >> source1_cast_filter >> source1_actor.mapper
    source2 >> source2_cast_filter >> source2_actor.mapper
    (source1 >> source1_double, source2) >> sum_filter >> summed_cast_filter >> summed_actor.mapper

    # There will be one render window.
    render_window = vtkRenderWindow(size=(600, 300), window_name='ImageWeightedSum')

    # And one interactor.
    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Define viewport ranges.
    # (xmin, ymin, xmax, ymax)
    left_viewport = [0.0, 0.0, 0.33, 1.0]
    center_viewport = [0.33, 0.0, .66, 1.0]
    right_viewport = [0.66, 0.0, 1.0, 1.0]

    # Setup renderers.
    left_renderer = vtkRenderer(background=colors.GetColor3d('Peru'), viewport=left_viewport)
    center_renderer = vtkRenderer(background=colors.GetColor3d('DarkTurquoise'), viewport=center_viewport)
    right_renderer = vtkRenderer(background=colors.GetColor3d('SteelBlue'), viewport=right_viewport)

    render_window.AddRenderer(left_renderer)
    render_window.AddRenderer(center_renderer)
    render_window.AddRenderer(right_renderer)

    left_renderer.AddActor(source1_actor)
    center_renderer.AddActor(source2_actor)
    right_renderer.AddActor(summed_actor)

    left_renderer.ResetCamera()
    center_renderer.ResetCamera()
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
