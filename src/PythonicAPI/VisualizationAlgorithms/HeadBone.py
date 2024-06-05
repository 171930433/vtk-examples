#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkMergePoints
from vtkmodules.vtkFiltersCore import (
    vtkFlyingEdges3D,
    vtkMarchingCubes
)
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkIOImage import vtkMetaImageReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    file_name, use_flying_edges = get_program_parameters()

    colors = vtkNamedColors()

    # Create the RenderWindow, Renderer and Interactor.
    ren = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='HeadBone')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Create the pipeline.
    reader = vtkMetaImageReader(file_name=file_name)

    if use_flying_edges:
        iso = vtkFlyingEdges3D(compute_gradients=True, compute_scalars=False)
        iso.SetValue(0, 1150)
    else:
        locator = vtkMergePoints(divisions=(64, 64, 92), number_of_points_per_bucket=2, automatic=False)
        iso = vtkMarchingCubes(compute_gradients=True, compute_scalars=False, locator=locator)
        iso.SetValue(0, 1150)

    iso_mapper = vtkPolyDataMapper(scalar_visibility=False)
    reader >> iso >> iso_mapper

    iso_actor = vtkActor(mapper=iso_mapper)
    iso_actor.SetMapper(iso_mapper)
    iso_actor.property.color = colors.GetColor3d('Ivory')

    outline = vtkOutlineFilter()

    outline_mapper = vtkPolyDataMapper()
    reader >> outline >> outline_mapper

    outline_actor = vtkActor(mapper=outline_mapper)
    outline_actor.property.color = colors.GetColor3d('White')

    ren.AddActor(outline_actor)
    ren.AddActor(iso_actor)

    ren.active_camera.focal_point = (0, 0, 0)
    ren.active_camera.position = (0, -1, 0)
    ren.active_camera.view_up = (0, 0, -1)
    ren.ResetCamera()
    ren.active_camera.Dolly(1.5)
    ren.ResetCameraClippingRange()

    ren_win.Render()
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'Marching cubes surface of human bone.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='FullHead.mhd.')
    parser.add_argument('-m', '--marching_cubes', action='store_false',
                        help='Use Marching Cubes instead of Flying Edges.')
    args = parser.parse_args()
    return args.filename, args.marching_cubes


if __name__ == '__main__':
    main()
