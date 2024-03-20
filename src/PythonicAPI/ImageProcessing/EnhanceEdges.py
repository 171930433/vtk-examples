#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkIOImage import vtkImageReader2Factory
from vtkmodules.vtkImagingColor import vtkImageMapToWindowLevelColors
from vtkmodules.vtkImagingCore import vtkImageCast
from vtkmodules.vtkImagingGeneral import vtkImageLaplacian
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
    description = 'High-pass filters can extract and enhance edges in an image.'
    epilogue = '''
    Subtraction of the Laplacian (middle) from the original image (left) results
     in edge enhancement or a sharpening operation (right).
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='FullHead.mhd.')
    args = parser.parse_args()
    return args.filename


def main():
    file_name = get_program_parameters()

    # Read the image.
    reader = vtkImageReader2Factory().CreateImageReader2(file_name)
    reader.file_name = file_name
    reader.update()

    scalar_range = list()
    for i in range(0, 2):
        scalar_range.append(reader.GetOutput().GetPointData().GetScalars().GetRange()[i])
    print("Range:", scalar_range)
    middle_slice = 22

    # Work with triple images.
    cast = vtkImageCast(output_scalar_type=ImageCastOutputScalarType().VTK_DOUBLE)

    laplacian = vtkImageLaplacian(dimensionality=3)

    enhance = vtkImageMathematics(operation=ImageMathematicsOperation().VTK_SUBTRACT)

    color_window = (scalar_range[1] - scalar_range[0])
    color_level = color_window / 2

    # Map the image through the lookup table.
    original_color = vtkImageMapToWindowLevelColors(window=color_window, level=color_level)

    display_extent = list()
    data_extent = reader.data_extent
    for i in range(0, 4):
        display_extent.append(data_extent[i])
    for i in range(0, 2):
        display_extent.append(middle_slice)

    original_actor = vtkImageActor(display_extent=display_extent)
    original_actor.property.interpolation_type = VolumePropertyInterpolationType().VTK_NEAREST_INTERPOLATION

    laplacian_color = vtkImageMapToWindowLevelColors(window=1000, level=0)
    laplacian_actor = vtkImageActor(display_extent=original_actor.GetDisplayExtent())
    laplacian_actor.property.interpolation_type = VolumePropertyInterpolationType().VTK_NEAREST_INTERPOLATION

    enhanced_color = vtkImageMapToWindowLevelColors(window=color_window, level=color_level)
    enhanced_actor = vtkImageActor(display_extent=original_actor.GetDisplayExtent())
    enhanced_actor.property.interpolation_type = VolumePropertyInterpolationType().VTK_NEAREST_INTERPOLATION

    # Set up the pipelines.
    reader >> original_color >> original_actor.mapper
    p = reader >> cast
    q = p >> laplacian
    q >> laplacian_color >> laplacian_actor.mapper
    (p, q) >> enhance >> enhanced_color >> enhanced_actor.mapper

    # Setup the renderers.
    original_renderer = vtkRenderer()
    laplacian_renderer = vtkRenderer()
    enhanced_renderer = vtkRenderer()

    original_renderer.AddActor(original_actor)
    laplacian_renderer.AddActor(laplacian_actor)
    enhanced_renderer.AddActor(enhanced_actor)

    renderers = list()
    renderers.append(original_renderer)
    renderers.append(laplacian_renderer)
    renderers.append(enhanced_renderer)

    # Setup viewports for the renderers.
    renderer_size = 400
    x_grid_dimensions = 3
    y_grid_dimensions = 1

    ren_win_size = (renderer_size * x_grid_dimensions, renderer_size * y_grid_dimensions)
    render_window = vtkRenderWindow(size=ren_win_size, window_name='EnhanceEdges')
    # render_window.SetSize(renderer_size * x_grid_dimensions, renderer_size * y_grid_dimensions)
    for row in range(0, y_grid_dimensions):
        for col in range(x_grid_dimensions):
            index = row * x_grid_dimensions + col
            # (xmin, ymin, xmax, ymax)
            viewport = [float(col) / x_grid_dimensions, float(y_grid_dimensions - (row + 1)) / y_grid_dimensions,
                        float(col + 1) / x_grid_dimensions, float(y_grid_dimensions - row) / y_grid_dimensions]
            renderers[index].SetViewport(viewport)
            render_window.AddRenderer(renderers[index])

    render_window_interactor = vtkRenderWindowInteractor()
    style = vtkInteractorStyleImage()

    render_window_interactor.SetInteractorStyle(style)
    render_window_interactor.SetRenderWindow(render_window)

    # Renderers share one camera.
    render_window.Render()
    renderers[0].GetActiveCamera().Dolly(1.5)
    renderers[0].ResetCameraClippingRange()

    for r in range(1, len(renderers)):
        renderers[r].SetActiveCamera(renderers[0].GetActiveCamera())
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


@dataclass(frozen=True)
class VolumePropertyInterpolationType:
    VTK_NEAREST_INTERPOLATION: int = 0
    VTK_LINEAR_INTERPOLATION: int = 1
    VTK_CUBIC_INTERPOLATION: int = 2


if __name__ == '__main__':
    main()
