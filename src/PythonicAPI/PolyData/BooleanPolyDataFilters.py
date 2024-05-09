#!/usr/bin/env python3

from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import (
    vtkCleanPolyData,
    vtkTriangleFilter
)
from vtkmodules.vtkFiltersGeneral import (
    vtkBooleanOperationPolyDataFilter,
    vtkLoopBooleanPolyDataFilter
)
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOGeometry import (
    vtkBYUReader,
    vtkOBJReader,
    vtkSTLReader
)
from vtkmodules.vtkIOLegacy import vtkPolyDataReader
from vtkmodules.vtkIOPLY import vtkPLYReader
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'How to align two vtkPolyData\'s.'
    epilogue = '''
    Try these parameters:
        ../../../src/Testing/Data/Torso.vtp ../../../src/Testing/Data/ObliqueCone.vtp -o difference
        ${DATA}/Torso.vtp difference ${DATA}/ObliqueCone.vtp
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('fn1', nargs='?', default=None,
                        help='The polydata source file name,e.g. Torso.vtp.')
    parser.add_argument('fn2', nargs='?', default=None,
                        help='The polydata target file name, e.g. ObliqueCone.vtp.')
    parser.add_argument('-o', '--operation', default='intersection',
                        help='The type of operation: union, intersection, or difference.')
    parser.add_argument('-l', '--loop', action='store_false',
                        help='Use vtkLoopBooleanPolyDataFilter instead of vtkBooleanOperationPolyDataFilter.')

    args = parser.parse_args()

    return args.fn1, args.fn2, args.operation, args.loop


def main():
    colors = vtkNamedColors()

    fn1, fn2, operation, bool_pd_filter = get_program_parameters()
    if fn1 and fn2:
        # Check that the files exist.
        src_fp = Path(fn1)
        tgt_fp = Path(fn2)
        if not src_fp.is_file():
            print(f'Nonexistent source: {src_fp}')
        if not tgt_fp.is_file():
            print(f'Nonexistent target: {tgt_fp}')
        if not src_fp.is_file() or not tgt_fp.is_file():
            return

        poly1 = read_poly_data(fn1)
        tri1 = vtkTriangleFilter()
        clean1 = vtkCleanPolyData()
        input1 = (poly1 >> tri1 >> clean1).update().output

        poly2 = read_poly_data(fn2)
        tri2 = vtkTriangleFilter()
        clean2 = vtkCleanPolyData()
        input2 = (poly2 >> tri2 >> clean2).update().output

    else:
        sphere_source1 = vtkSphereSource(center=(0.25, 0, 0), phi_resolution=21, theta_resolution=21)
        sphere_source1.Update()
        input1 = sphere_source1.GetOutput()

        sphere_source2 = vtkSphereSource()
        sphere_source2.Update()
        input2 = sphere_source2.GetOutput()

    input1_mapper = vtkPolyDataMapper(scalar_visibility=False)
    input1 >> input1_mapper
    input1_actor = vtkActor(mapper=input1_mapper)
    input1_actor.property.diffuse_color = colors.GetColor3d('Tomato')
    input1_actor.property.specular = 0.6
    input1_actor.property.specular_power = 20
    bounds = input1.bounds
    input1_actor.SetPosition(bounds[1] - bounds[0], 0, 0)

    input2_mapper = vtkPolyDataMapper(scalar_visibility=False)
    input2 >> input2_mapper
    input2_actor = vtkActor(mapper=input2_mapper)
    input2_actor.property.diffuse_color = colors.GetColor3d('Mint')
    input2_actor.property.specular = 0.6
    input2_actor.property.specular_power = 20
    input2_actor.SetPosition(bounds[0] - bounds[1], 0, 0)

    if bool_pd_filter:
        boolean_operation = vtkBooleanOperationPolyDataFilter()
        if operation.lower() == 'union':
            boolean_operation.operation = vtkBooleanOperationPolyDataFilter.VTK_UNION
        elif operation.lower() == 'intersection':
            boolean_operation.operation = vtkBooleanOperationPolyDataFilter.VTK_INTERSECTION
        elif operation.lower() == 'difference':
            boolean_operation.operation = vtkBooleanOperationPolyDataFilter.VTK_DIFFERENCE
        else:
            print('Unknown operation:', operation)
            return
    else:
        boolean_operation = vtkLoopBooleanPolyDataFilter()
        if operation.lower() == 'union':
            boolean_operation.operation = vtkLoopBooleanPolyDataFilter.VTK_UNION
        elif operation.lower() == 'intersection':
            boolean_operation.operation = vtkLoopBooleanPolyDataFilter.VTK_INTERSECTION
        elif operation.lower() == 'difference':
            boolean_operation.operation = vtkLoopBooleanPolyDataFilter.VTK_DIFFERENCE
        else:
            print('Unknown operation:', operation)
            return

    boolean_operation.SetInputData(0, input1)
    boolean_operation.SetInputData(1, input2)

    boolean_operation_mapper = vtkPolyDataMapper(scalar_visibility=False)
    boolean_operation_actor = vtkActor(mapper=boolean_operation_mapper)
    boolean_operation >> boolean_operation_mapper
    boolean_operation_actor.property.diffuse_color = colors.GetColor3d('Banana')
    boolean_operation_actor.property.specular = 0.6
    boolean_operation_actor.property.specular_power = 20

    renderer = vtkRenderer(background=colors.GetColor3d('Silver'))
    render_window = vtkRenderWindow(size=(640, 480), window_name='BooleanPolyDataFilters')
    render_window.AddRenderer(renderer)
    ren_win_interactor = vtkRenderWindowInteractor()
    ren_win_interactor.render_window = render_window

    renderer.AddViewProp(input1_actor)
    renderer.AddViewProp(input2_actor)
    renderer.AddViewProp(boolean_operation_actor)

    viewUp = (0.0, 0.0, 1.0)
    position = (0.0, -1.0, 0.0)
    PositionCamera(renderer, viewUp, position)
    renderer.active_camera.Dolly(1.4)
    renderer.ResetCameraClippingRange()

    ren_win_interactor = vtkRenderWindowInteractor()
    ren_win_interactor.render_window = render_window

    render_window.Render()
    ren_win_interactor.Start()


def read_poly_data(file_name):
    if not file_name:
        print(f'No file name.')
        return None

    valid_suffixes = ['.g', '.obj', '.stl', '.ply', '.vtk', '.vtp']
    path = Path(file_name)
    ext = None
    if path.suffix:
        ext = path.suffix.lower()
    if path.suffix not in valid_suffixes:
        print(f'No reader for this file suffix: {ext}')
        return None

    reader = None
    if ext == '.ply':
        reader = vtkPLYReader(file_name=file_name)
    elif ext == '.vtp':
        reader = vtkXMLPolyDataReader(file_name=file_name)
    elif ext == '.obj':
        reader = vtkOBJReader(file_name=file_name)
    elif ext == '.stl':
        reader = vtkSTLReader(file_name=file_name)
    elif ext == '.vtk':
        reader = vtkPolyDataReader(file_name=file_name)
    elif ext == '.g':
        reader = vtkBYUReader(file_name=file_name)

    if reader:
        reader.update()
        poly_data = reader.output
        return poly_data
    else:
        return None


def PositionCamera(renderer, viewUp, position):
    renderer.GetActiveCamera().SetViewUp(viewUp)
    renderer.GetActiveCamera().SetPosition(position)
    renderer.ResetCamera()


if __name__ == '__main__':
    main()
