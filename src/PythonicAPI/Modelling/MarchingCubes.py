#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkFiltersCore import (
    vtkFlyingEdges3D,
    vtkMarchingCubes
)
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOImage import vtkDICOMImageReader
from vtkmodules.vtkImagingHybrid import vtkVoxelModeller
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'The skin extracted from a CT dataset of the head.'
    epilogue = '''
    Derived from VTK/Examples/Cxx/Medical1.cxx
    This example reads a volume dataset, extracts an isosurface that
     represents the skin and displays it.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d', default=None, help='A DICOM Image directory.')
    parser.add_argument('-i', type=float, default=None, help='The iso value to use.')
    parser.add_argument('-m', action='store_false',
                        help='Use Marching Cubes instead of Flying Edges.')
    args = parser.parse_args()
    return args.d, args.i, args.m


def main():
    dicom_dir, iso_value, use_flying_edges = get_program_parameters()
    if iso_value is None and dicom_dir is not None:
        print('An ISO value is needed.')
        return ()

    colors = vtkNamedColors()

    volume = vtkImageData()
    if dicom_dir is None:
        sphere_source = vtkSphereSource(phi_resolution=20, theta_resolution=20)
        sphere_source.Update()

        bounds = list(sphere_source.GetOutput().GetBounds())
        for i in range(0, 6, 2):
            dist = bounds[i + 1] - bounds[i]
            bounds[i] = bounds[i] - 0.1 * dist
            bounds[i + 1] = bounds[i + 1] + 0.1 * dist
        voxel_modeller = vtkVoxelModeller(sample_dimensions=(50, 50, 50), model_bounds=bounds,
                                          scalar_type=VoxelModeller.ScalarType.VTK_FLOAT,
                                          maximum_distance=0.1)
        (sphere_source >> voxel_modeller).update()
        iso_value = 0.5
        volume.DeepCopy(voxel_modeller.output)
    else:
        reader = vtkDICOMImageReader(file_name=dicom_dir)
        reader.update()
        volume.DeepCopy(reader.output)

    if use_flying_edges:
        surface = vtkFlyingEdges3D(input_data=volume, compute_normals=True)
    else:
        surface = vtkMarchingCubes(input_data=volume, compute_normals=True)
    surface.SetValue(0, iso_value)

    renderer = vtkRenderer(background=colors.GetColor3d('DarkSlateGray'))
    render_window = vtkRenderWindow(window_name='MarchingCubes')
    render_window.AddRenderer(renderer)
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window

    mapper = vtkPolyDataMapper(scalar_visibility=False)
    surface >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('MistyRose')

    renderer.AddActor(actor)

    render_window.Render()
    interactor.Start()


@dataclass(frozen=True)
class VoxelModeller:
    @dataclass(frozen=True)
    class ScalarType:
        VTK_BIT: int = 1
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
