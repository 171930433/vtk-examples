#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkClipPolyData
from vtkmodules.vtkFiltersGeometry import vtkImageDataGeometryFilter
from vtkmodules.vtkIOImage import vtkPNMReader
from vtkmodules.vtkImagingGeneral import vtkImageGaussianSmooth
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    file_name = get_program_parameters()

    # Now create the RenderWindow, Renderer and Interactor.
    ren = vtkRenderer(background=colors.GetColor3d('WhiteSmoke'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='CreateBFont')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    image_in = vtkPNMReader(file_name=file_name)

    gaussian = vtkImageGaussianSmooth(standard_deviations=(2, 2), dimensionality=2, radius_factors=(1, 1))

    geometry = vtkImageDataGeometryFilter()

    a_clipper = vtkClipPolyData(value=127.5, generate_clip_scalars=False, inside_out=True)
    a_clipper.output.point_data.copy_scalars = False

    mapper = vtkPolyDataMapper(scalar_visibility=False)
    image_in >> gaussian >> geometry >> a_clipper >> mapper

    letter = vtkActor(mapper=mapper)
    letter.property.diffuse_color = colors.GetColor3d('LampBlack')
    letter.property.representation = Property.Representation.VTK_WIREFRAME

    ren.AddActor(letter)

    ren.ResetCamera()
    ren.active_camera.Dolly(1.2)
    ren.ResetCameraClippingRange()

    # Render the image.
    ren_win.Render()
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'A scanned image clipped with a scalar value.'
    epilogue = '''
    A scanned image clipped with a scalar value of 1/2 its maximum intensity
     produces a mixture of quadrilaterals and triangles.
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='B.pgm.')
    args = parser.parse_args()
    return args.filename


@dataclass(frozen=True)
class Property:
    @dataclass(frozen=True)
    class Interpolation:
        VTK_FLAT: int = 0
        VTK_GOURAUD: int = 1
        VTK_PHONG: int = 2
        VTK_PBR: int = 3

    @dataclass(frozen=True)
    class Representation:
        VTK_POINTS: int = 0
        VTK_WIREFRAME: int = 1
        VTK_SURFACE: int = 2


if __name__ == '__main__':
    main()
