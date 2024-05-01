#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkLogger
from vtkmodules.vtkFiltersCore import vtkMergeFilter
from vtkmodules.vtkFiltersGeneral import vtkWarpScalar
from vtkmodules.vtkFiltersGeometry import vtkImageDataGeometryFilter
from vtkmodules.vtkIOImage import vtkBMPReader
from vtkmodules.vtkImagingColor import vtkImageLuminance
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    # This turns off the merge filter warnings.
    vtkLogger.SetStderrVerbosity(vtkLogger.VERBOSITY_OFF)

    file_name = get_program_parameters()

    colors = vtkNamedColors()

    # Set the background color.
    colors.SetColor('BkgColor', 60, 93, 144, 255)

    # Read in an image and compute a luminance value. The image is extracted
    # as a set of polygons (vtkImageDataGeometryFilter). We then will
    # warp the plane using the scalar (luminance) values.
    reader = vtkBMPReader(file_name=file_name)
    # Convert the image to a grey scale.
    luminance = vtkImageLuminance()
    # Pass the data to the pipeline as polygons.
    geometry = vtkImageDataGeometryFilter()
    # Warp the data in a direction perpendicular to the image plane.
    warp = vtkWarpScalar(scale_factor=-0.1)
    reader >> luminance >> geometry >> warp

    # Use vtkMergeFilter to combine the original image with the warped geometry.
    merge = vtkMergeFilter(geometry_connection=warp.GetOutputPort(), scalars_connection=reader.GetOutputPort())
    mapper = vtkDataSetMapper(scalar_range=(0, 255))
    merge >> mapper
    actor = vtkActor(mapper=mapper)

    # Create the rendering window, renderer, and interactive renderer.
    ren = vtkRenderer(background=colors.GetColor3d('BkgColor'))
    ren_win = vtkRenderWindow(size=(512, 512), window_name='ImageWarp')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Add the actors to the renderer, set the background and size.
    ren.AddActor(actor)
    ren.ResetCamera()
    # ren.active_camera.Azimuth(20)
    # ren.active_camera.Elevation(30)
    # ren.ResetCameraClippingRange()
    # ren.active_camera.Zoom(1.3)
    ren.active_camera.position = (-100, -130, 325)
    ren.active_camera.focal_point = (105, 114, -29)
    ren.active_camera.view_up = (0.51, 0.54, 0.67)
    ren.ResetCameraClippingRange()

    # Render the image.
    iren.Initialize()
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'ImageWarp.'
    epilogue = '''
This example shows how to combine data from both the imaging
 and graphics pipelines. The vtkMergeData filter is used to
 merge the data from each together.
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('fileName', help='Path to the masonry.bmp file.')
    args = parser.parse_args()
    return args.fileName


if __name__ == '__main__':
    main()
