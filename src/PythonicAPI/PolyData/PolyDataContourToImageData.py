#!/usr/bin/env python3

import math
from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonCore import VTK_UNSIGNED_CHAR
from vtkmodules.vtkCommonDataModel import (
    vtkImageData,
    vtkPlane
)
from vtkmodules.vtkFiltersCore import (
    vtkCutter,
    vtkStripper
)
from vtkmodules.vtkFiltersModeling import vtkLinearExtrusionFilter
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOImage import (
    vtkMetaImageWriter,
    vtkPNGWriter
)
from vtkmodules.vtkIOXML import (
    vtkXMLWriterBase,
    vtkXMLPolyDataWriter
)
from vtkmodules.vtkImagingStencil import (
    vtkImageStencil,
    vtkPolyDataToImageStencil
)


def main():
    # 3D source sphere.
    sphere_source = vtkSphereSource(phi_resolution=30, theta_resolution=30, center=(40, 40, 0), radius=20)

    # Generate a circle by cutting the sphere with an implicit plane
    # (through its center, axis-aligned).
    cut_plane = vtkPlane(origin=sphere_source.center, normal=(0, 0, 1))
    circle_cutter = vtkCutter(cut_function=cut_plane)

    stripper = vtkStripper()

    # That's our circle
    circle = (sphere_source >> circle_cutter >> stripper).update().output

    # Write the circle out.
    poly_data_writer = vtkXMLPolyDataWriter(file_name='circle.vtp', input_data=circle,
                                            compressor_type=vtkXMLWriterBase.NONE, data_mode=vtkXMLWriterBase.Ascii)
    poly_data_writer.Write()

    # Prepare the binary image's voxel grid.
    spacing = (0.5, 0.5, 0.5)

    bounds = circle.bounds
    dim = [0] * 3
    for i in range(3):
        dim[i] = int(math.ceil((bounds[i * 2 + 1] - bounds[i * 2]) / spacing[i])) + 1
        if dim[i] < 1:
            dim[i] = 1

    # NOTE: I am not sure if we have to add some offset!
    origin = [bounds[0], bounds[2], bounds[4]]
    # For example:
    # spacing = (0.5, 0.5, 0.5)
    # origin = [a + (b / 2.0) for a, b in zip(origin, spacing)]

    white_image = vtkImageData(spacing=spacing, dimensions=dim)
    white_image.SetExtent(0, dim[0] - 1, 0, dim[1] - 1, 0, dim[2] - 1)
    white_image.AllocateScalars(VTK_UNSIGNED_CHAR, 1)

    # Fill the image with foreground voxels:
    in_val = 255
    out_val = 0
    count = white_image.GetNumberOfPoints()
    for i in range(0, count):
        white_image.point_data.scalars.SetTuple1(i, in_val)

    # sweep polygonal data (this is the important thing with contours!)
    extruder = vtkLinearExtrusionFilter(input_data=circle, scale_factor=1.0,
                                        extrusion_type=LinearExtrusionFilter.ExtrusionType.VTK_VECTOR_EXTRUSION,
                                        vector=(0, 0, 1))

    # polygonal data -> image stencil:
    # Note: tolerance=0 is important if extruder.vector=(0, 0, 1) !!!
    pol_2_stenc = vtkPolyDataToImageStencil(tolerance=0, output_origin=origin, output_spacing=spacing,
                                            output_whole_extent=white_image.extent)
    extruder >> pol_2_stenc

    # Cut the corresponding white image and set the background:
    img_stenc = vtkImageStencil(input_data=white_image,
                                reverse_stencil=False, background_value=out_val)
    img_stenc.SetStencilConnection(pol_2_stenc.GetOutputPort())

    image_writer = vtkMetaImageWriter(file_name='labelImage.mhd', )
    img_stenc >> image_writer
    image_writer.Write()

    image_writer = vtkPNGWriter(file_name='labelImage.png')
    img_stenc >> image_writer
    image_writer.Write()


@dataclass(frozen=True)
class LinearExtrusionFilter:
    @dataclass(frozen=True)
    class ExtrusionType:
        VTK_VECTOR_EXTRUSION: int = 1
        VTK_NORMAL_EXTRUSION: int = 2
        VTK_POINT_EXTRUSION: int = 3


if __name__ == '__main__':
    main()
