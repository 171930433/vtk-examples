#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkIdList
from vtkmodules.vtkFiltersCore import (
    vtkConnectivityFilter,
    vtkDecimatePro
)
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkIOGeometry import vtkMCubesReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Applying connectivity and decimation filters to remove noisy isosurfaces and reduce data size.'
    epilogue = '''
        Applying connectivity and decimation filters to remove noisy isosurfaces and reduce data size..

This example demonstrates how to use the vtkConnectivityFilter and vtkDecimate.

   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='pine_root.tri.')
    args = parser.parse_args()
    return args.filename


def main():
    def number_of_triangles(pd):
        """
        Count the number of triangles.
        :param pd: vtkPolyData.
        :return: The number of triangles.
        """
        cells = pd.GetPolys()
        num_of_triangles = 0
        id_list = vtkIdList()
        for i in range(0, cells.GetNumberOfCells()):
            cells.GetNextCell(id_list)
            # If a cell has three points it is a triangle.
            if id_list.GetNumberOfIds() == 3:
                num_of_triangles += 1
        return num_of_triangles

    colors = vtkNamedColors()

    file_name = get_program_parameters()

    # Create the pipeline.
    reader = vtkMCubesReader(file_name=file_name, flip_normals=False)
    deci = vtkDecimatePro(target_reduction=0.9, absolute_error=0.0005, feature_angle=30,
                          error_is_absolute=True, accumulate_error=True)
    deci.MaximumIterations = 6
    connect = vtkConnectivityFilter(
        extraction_mode=ConnectivityFilter.ExtractionMode.VTK_EXTRACT_LARGEST_REGION)
    iso_mapper = vtkDataSetMapper(scalar_visibility=False)
    (reader >> deci >> connect >> iso_mapper).update()
    #  Now we have done the update, we can print out the count of triangles.
    print(f'Before Decimation.\nThere are: {number_of_triangles(reader.output)} triangles')
    print(f'After Decimation.\nThere are: {number_of_triangles(deci.output)} triangles')
    print(f'After Connectivity.\nThere are: {number_of_triangles(connect.output)} triangles')
    iso_actor = vtkActor(mapper=iso_mapper)
    iso_actor.property.color = colors.GetColor3d('raw_sienna')

    # Get an outline of the data set for context.
    outline = vtkOutlineFilter()
    outline_mapper = vtkPolyDataMapper()
    reader >> outline >> outline_mapper
    outline_actor = vtkActor(mapper=outline_mapper)
    outline_actor.property.color = colors.GetColor3d('Black')

    # Create the Renderer, RenderWindow and RenderWindowInteractor.
    ren = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(size=(512, 512), window_name='PineRootDecimation')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Add the actors to the renderer, set the background and size.
    ren.AddActor(outline_actor)
    ren.AddActor(iso_actor)

    cam = ren.active_camera
    cam.focal_point = (40.6018, 37.2813, 50.1953)
    cam.position = (40.6018, -280.533, 47.0172)
    cam.ComputeViewPlaneNormal()
    cam.clipping_range = (26.1073, 1305.36)
    cam.view_angle = 20.9219
    cam.view_up = (0.0, 0.0, 1.0)

    iren.Initialize()
    ren_win.Render()
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
