#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkUnsignedCharArray
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.vtkIOImport import (
    vtk3DSImporter,
    vtkGLTFImporter,
    vtkOBJImporter,
    vtkVRMLImporter,
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkLight,
    vtkPolyDataMapper,
    vtkRenderWindowInteractor,
    vtkRenderWindow,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Combining imported actors.'
    epilogue = '''
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('in_fn', help='iflamingo.3ds.')
    # Optional additional input file and folder for the OBJ reader.
    parser.add_argument('-m', '--mtl_fn', default=None, help='Optional OBJ MTL file name e.g. iflamingo.obj')
    parser.add_argument('-t', '--texture_dir', default=None, help='Optional OBJ texture folder.')

    args = parser.parse_args()
    return args.in_fn, args.mtl_fn, args.texture_dir


def main():
    ifn, mtl_fn, texture_dir = get_program_parameters()

    input_suffixes = ('.3ds', '.glb', '.gltf', '.obj', '.wrl')
    output_suffixes = ('.glb', '.gltf', '.obj', '.wrl', '.x3d')

    def sorted_suffixes(suffixes):
        s = ', '.join(sorted(list(suffixes)))
        return f'{s}'

    # Check the files exist and have correct suffixes.
    ifp = Path(ifn)
    if not ifp.is_file():
        print(f'Nonexistent source: {ifp}')
        return
    if not ifp.suffix.lower() in input_suffixes:
        print(f'Available input file suffixes are: {sorted_suffixes(input_suffixes)}')
        return

    mtlp = None
    if mtl_fn:
        mtlp = Path(mtl_fn)
        if not mtlp.is_file():
            print(f'Nonexistent MTL path: {mtlp}')
            return
        if not mtlp.suffix.lower() == '.mtl':
            print(f'Bad mtl file suffix: {mtlp}')
            return
    texd = None
    if texture_dir:
        texd = Path(texture_dir)
        if not texd.is_dir():
            print(f'Nonexistent directory: {texd}')
            return

    colors = vtkNamedColors()

    ren = vtkRenderer(background=colors.GetColor3d('SlateGray'), background2=colors.GetColor3d('LightSkyBlue'),
                      gradient_background=True)
    ren_win = vtkRenderWindow(size=(640, 480), window_name='CombineImportedActors')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Read the file(s).
    import_ren = vtkRenderer()
    import_ren_win = vtkRenderWindow()
    import_ren_win.AddRenderer(import_ren)

    importer = get_importer(ifp, mtlp, texd, import_ren_win)

    if not importer:
        print(f'No suitable reader found for {ifp}')
        return

    importer.active_renderer = import_ren
    importer.Update()

    actors = import_ren.actors
    actors.InitTraversal()
    actors_sz = actors.number_of_items
    if actors_sz == 1:
        print(f'There is {actors_sz} actors')
    else:
        print(f'There are {actors_sz} actors')

    for a in range(0, actors_sz):
        if ifp.suffix.lower() == '.obj':
            # OBJImporter turns texture interpolation off.
            actor = actors.next_actor
            if actor.texture:
                # print('Has texture')
                # print(importer.GetOutputDescription(a))
                actor.texture.interpolate = True

    append = vtkAppendPolyData()
    for a in range(0, actors_sz):
        append_pd = vtkPolyData()
        actor = actors.next_actor
        actor.mapper.update()
        if actor.user_matrix:
            transform = vtkTransform(matrix=actor.user_matrix)
            transform_pd = vtkTransformPolyDataFilter(transform=transform)
            (actor.mapper >> transform_pd).update()
            append_pd.DeepCopy(transform_pd)
        else:
            append_pd.DeepCopy(actor.mapper.input)

        cell_data = vtkUnsignedCharArray(number_of_components=3, number_of_tuples=append_pd.number_of_cells)
        for i in range(0, append_pd.number_of_cells):
            # rgb = [0]*4
            rgb = actor.property.GetDiffuseColor()
            rgb = list(map(lambda x: int(x * 255.0), rgb))
            cell_data.InsertTuple(i, rgb)
            append_pd.cell_data.SetScalars(cell_data)
            append.AddInputData(append_pd)
    append.update()

    mapper = vtkPolyDataMapper(scalar_mode=Mapper.ScalarMode.VTK_SCALAR_MODE_USE_CELL_DATA)
    append >> mapper
    actor = vtkActor(mapper=mapper)
    actor.property.diffuse_color = colors.GetColor3d('Banana')

    ren.AddActor(actor)

    name = ifp.name
    camera = ren.active_camera
    if name == 'iflamingo.3ds':
        camera.position = (0, -1, 0)
        camera.focal_point = (0, 0, 0)
        camera.view_up = (0, 0, 1)
        camera.Azimuth(150)
        camera.Elevation(30)
        ren.ResetCamera()

    if name == 'FlightHelmet.gltf':
        head_light = vtkLight(switch=True)
        head_light.SetLightTypeToHeadlight()
        ren.AddLight(head_light)

    if name == 'trumpet.obj':
        camera.Azimuth(30)
        camera.Elevation(30)
        camera.Dolly(1.5)

    ren.ResetCameraClippingRange()

    ren_win.Render()

    iren.Start()


def get_importer(ifp, mtlp, texd, ren_win):
    importer = None

    if ifp.suffix.lower() == '.wrl':
        importer = vtkVRMLImporter(file_name=ifp, render_window=ren_win)

    if ifp.suffix.lower() == '.3ds':
        importer = vtk3DSImporter(file_name=ifp, render_window=ren_win, compute_normals=True)

    if ifp.suffix.lower() in ('.gltf', 'glb'):
        importer = vtkGLTFImporter(file_name=ifp, render_window=ren_win)

    if ifp.suffix.lower() == '.obj':
        importer = vtkOBJImporter(file_name=ifp, render_window=ren_win)
        if mtlp:
            importer.file_name_mtl = mtlp
        if texd:
            importer.texture_path = texd

    return importer


@dataclass(frozen=True)
class Mapper:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_MODE_DEFAULT: int = 0
        VTK_COLOR_MODE_MAP_SCALARS: int = 1
        VTK_COLOR_MODE_DIRECT_SCALARS: int = 2

    @dataclass(frozen=True)
    class ResolveCoincidentTopology:
        VTK_RESOLVE_OFF: int = 0
        VTK_RESOLVE_POLYGON_OFFSET: int = 1
        VTK_RESOLVE_SHIFT_ZBUFFER: int = 2

    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_DEFAULT: int = 0
        VTK_SCALAR_MODE_USE_POINT_DATA: int = 1
        VTK_SCALAR_MODE_USE_CELL_DATA: int = 2
        VTK_SCALAR_MODE_USE_POINT_FIELD_DATA: int = 3
        VTK_SCALAR_MODE_USE_CELL_FIELD_DATA: int = 4
        VTK_SCALAR_MODE_USE_FIELD_DATA: int = 5


if __name__ == '__main__':
    main()
