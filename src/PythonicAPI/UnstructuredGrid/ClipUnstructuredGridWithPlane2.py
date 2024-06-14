#!/usr/bin/env python3

import collections

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import (
    vtkCellTypes,
    vtkPlane
)
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersGeneral import vtkClipDataSet
from vtkmodules.vtkIOLegacy import vtkUnstructuredGridReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Use a vtkClipDataSet to clip a vtkUnstructuredGrid..'
    epilogue = '''
 Use a vtkClipDataSet to clip a vtkUnstructuredGrid..
 The resulting output and clipped output are presented in yellow and red respectively.
 To illustrate the clipped interfaces, the example uses a vtkTransform to rotate each
    output about their centers.
 Note: This clipping filter does not retain the original cells if they are not clipped.
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='treemesh.vtk')
    args = parser.parse_args()
    return args.filename


def main():
    filename = get_program_parameters()

    # Create the reader for the data.
    reader = vtkUnstructuredGridReader(file_name=filename)
    reader.update()

    bounds = reader.output.bounds
    center = reader.output.center

    colors = vtkNamedColors()

    renderer = vtkRenderer(background=colors.GetColor3d('Wheat'))
    renderer.UseHiddenLineRemovalOn()
    render_window = vtkRenderWindow(size=(640, 480), window_name='ClipUnstructuredGridWithPlane2')
    render_window.AddRenderer(renderer)
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window

    x_norm = [-1.0, -1.0, 1.0]

    clip_plane = vtkPlane(origin=center, normal=x_norm)
    clipper = vtkClipDataSet(clip_function=clip_plane, input_data=reader.output,
                             value=0.0, generate_clipped_output=True)
    clipper.update()

    inside_mapper = vtkDataSetMapper(scalar_visibility=False, input_data=clipper.output)
    inside_actor = vtkActor(mapper=inside_mapper)
    inside_actor.property.diffuse_color = colors.GetColor3d('Banana')
    inside_actor.property.ambient = 0.3
    inside_actor.property.edge_visibility = True

    clipped_mapper = vtkDataSetMapper(scalar_visibility=False, input_data=clipper.clipped_output)
    clipped_actor = vtkActor(mapper=clipped_mapper)
    clipped_actor.property.diffuse_color = colors.GetColor3d('Tomato')
    clipped_actor.property.ambient = 0.3
    clipped_actor.property.edge_visibility = True

    # Create transforms to make a better visualization
    # Reverse the sign of each element in center.
    rev_center = tuple(-i for i in center)

    inside_transform = vtkTransform()
    inside_transform.Translate(-(bounds[1] - bounds[0]) * 0.75, 0, 0)
    inside_transform.Translate(*center)
    inside_transform.RotateY(-120.0)
    inside_transform.Translate(*rev_center)
    inside_actor.user_transform = inside_transform

    clipped_transform = vtkTransform()
    clipped_transform.Translate((bounds[1] - bounds[0]) * 0.75, 0, 0)
    clipped_transform.Translate(*center)
    clipped_transform.RotateY(-120.0)
    clipped_transform.Translate(*rev_center)
    clipped_actor.user_transform = clipped_transform

    renderer.AddViewProp(clipped_actor)
    renderer.AddViewProp(inside_actor)

    renderer.ResetCamera()
    renderer.GetActiveCamera().Dolly(1.4)
    renderer.ResetCameraClippingRange()
    render_window.Render()

    interactor.Start()

    # Generate a report.
    number_of_cells = clipper.GetOutput().GetNumberOfCells()
    print('------------------------')
    print(f'The inside dataset contains a {clipper.output.class_name} that has {number_of_cells} cells')
    cell_map = dict()
    for i in range(0, number_of_cells):
        cell_map.setdefault(clipper.output.GetCellType(i), 0)
        cell_map[clipper.output.GetCellType(i)] += 1
    # Sort by key and put into an OrderedDict.
    # An OrderedDict remembers the order in which the keys have been inserted.
    for k, v in collections.OrderedDict(sorted(cell_map.items())).items():
        print(f' Cell type {vtkCellTypes.GetClassNameFromTypeId(k)} occurs {v} times.')

    number_of_cells = clipper.GetClippedOutput().GetNumberOfCells()
    print('------------------------')
    print(f'The clipped dataset contains a {clipper.output.class_name} that has {number_of_cells} cells')
    outside_cell_map = dict()
    for i in range(0, number_of_cells):
        outside_cell_map.setdefault(clipper.GetClippedOutput().GetCellType(i), 0)
        outside_cell_map[clipper.GetClippedOutput().GetCellType(i)] += 1
    for k, v in collections.OrderedDict(sorted(outside_cell_map.items())).items():
        print(f' Cell type {vtkCellTypes.GetClassNameFromTypeId(k)} occurs {v} times.')


if __name__ == '__main__':
    main()
