#!/usr/bin/env python

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import (
    vtkFlyingEdges3D,
    vtkMarchingCubes,
    vtkPolyDataConnectivityFilter
)
from vtkmodules.vtkIOLegacy import vtkStructuredPointsReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Reads a structured points dataset stored in a .vtk file and constructs a 3D model.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='E.g. brain.vtk.')
    parser.add_argument('threshold', type=int, help='The threshold, e.g. 50.')
    parser.add_argument('-a', action='store_false', default=True, help='Extract all surfaces.')
    parser.add_argument('-m', '--marching_cubes', action='store_false',
                        help='Use Marching Cubes instead of Flying Edges.')
    args = parser.parse_args()
    return args.filename, args.threshold, args.a, args.marching_cubes


def main():
    colors = vtkNamedColors()

    colors.SetColor('SkinColor', 240, 184, 160, 255)
    colors.SetColor('BackfaceColor', 255, 229, 200, 255)
    colors.SetColor('BkgColor', 51, 77, 102, 255)

    file_name, threshold, largest_surface, use_flying_edges = get_program_parameters()

    # Load data
    reader = vtkStructuredPointsReader()
    reader.SetFileName(file_name)

    # Create a 3D model using flying edges or marching cubes
    if use_flying_edges:
        mc = vtkFlyingEdges3D(compute_normals=True, compute_gradients=True)
    else:
        mc = vtkMarchingCubes(compute_normals=True, compute_gradients=True)

    mc.SetValue(0, threshold)  # The second value acts as the threshold.

    # Create a mapper
    mapper = vtkPolyDataMapper(scalar_visibility=False)
    if largest_surface:
        # To keep the largest region.
        confilter = vtkPolyDataConnectivityFilter(
            extraction_mode=ConnectivityFilter.ExtractionMode.VTK_EXTRACT_LARGEST_REGION)
        reader >> mc >> confilter >> mapper
    else:
        reader >> mc >> mapper

    # Visualize
    back_prop = vtkProperty(diffuse_color=colors.GetColor3d('BackfaceColor'))
    actor = vtkActor(mapper=mapper, backface_property=back_prop)
    actor.property.color = colors.GetColor3d('SkinColor')

    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    renderer.AddActor(actor)
    renderer.active_camera.view_up = (0.0, 0.0, 1.0)
    renderer.active_camera.position = (0.0, 1.0, 0.0)
    renderer.active_camera.focal_point = (0.0, 0.0, 0.0)
    renderer.ResetCamera()
    renderer.active_camera.Azimuth(30.0)
    renderer.active_camera.Elevation(30.0)
    ren_win = vtkRenderWindow(size=(640, 480), window_name='ExtractLargestIsosurface')
    ren_win.AddRenderer(renderer)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win
    ren_win.Render()
    iren.Initialize()
    iren.Start()


@dataclass(frozen=True)
class ConnectivityFilter:
    @dataclass(frozen=True)
    class ExtractionMode:
        VTK_EXTRACT_POINT_SEEDED_REGIONS: int = 1
        VTK_EXTRACT_CELL_SEEDED_REGIONS: int = 2
        VTK_EXTRACT_SPECIFIED_REGIONS: int = 3
        VTK_EXTRACT_LARGEST_REGION: int = 4
        VTK_EXTRACT_ALL_REGIONS: int = 5
        VTK_EXTRACT_CLOSEST_POINT_REGION: int = 6


if __name__ == '__main__':
    main()
