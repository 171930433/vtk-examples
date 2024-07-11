#!/usr/bin/env python

from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOExport import (
    vtkX3DExporter,
    vtkGLTFExporter,
    vtkOBJExporter,
    vtkVRMLExporter,
)
from vtkmodules.vtkIOImport import (
    vtk3DSImporter,
    vtkGLTFImporter,
    vtkOBJImporter,
    vtkVRMLImporter,
)
from vtkmodules.vtkRenderingCore import (
    vtkLight,
    vtkRenderWindowInteractor,
    vtkRenderWindow,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Importing a 3ds file.'
    epilogue = '''
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('in_fn', help='iflamingo.3ds.')
    parser.add_argument('-o', '--out_fn', default=None, help='Output file name e.g. iflamingo.obj')
    # Optional additional input file and folder for the OBJ reader.
    parser.add_argument('-m', '--mtl_fn', default=None, help='Optional OBJ MTL file name e.g. iflamingo.obj')
    parser.add_argument('-t', '--texture_dir', default=None, help='Optional OBJ texture folder.')

    args = parser.parse_args()
    return args.in_fn, args.out_fn, args.mtl_fn, args.texture_dir


def main():
    ifn, ofn, mtl_fn, texture_dir = get_program_parameters()

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

    ofp = None
    if ofn:
        ofp = Path(ofn)
        if not ofp.suffix.lower() in output_suffixes:
            print(f'Available output file suffixes are: {sorted_suffixes(output_suffixes)}')
            return
        if ofp.is_file():
            print(f'Destination must not exist: {ofp}')
            return
        if ofp.suffix.lower() == '.obj':
            # We may need to create the parent folder.
            ofp.parent.mkdir(parents=True, exist_ok=True)

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
    ren_win = vtkRenderWindow(size=(640, 480), window_name='ImportToExport')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Read the file(s).
    importer = None

    if ifp.suffix.lower() == '.wrl':
        importer = vtkVRMLImporter(file_name=ifp, render_window=ren_win)
        ren_win = importer.GetRenderWindow()
        importer.active_renderer = ren

    if ifp.suffix.lower() == '.3ds':
        importer = vtk3DSImporter(file_name=ifp, render_window=ren_win, compute_normals=True)
        ren_win = importer.GetRenderWindow()
        importer.active_renderer = ren

    if ifp.suffix.lower() in ('.gltf', 'glb'):
        importer = vtkGLTFImporter(file_name=ifp, render_window=ren_win)
        ren_win = importer.GetRenderWindow()
        importer.active_renderer = ren

    if ifp.suffix.lower() == '.obj':
        importer = vtkOBJImporter(file_name=ifp, render_window=ren_win)
        ren_win = importer.GetRenderWindow()
        if mtlp:
            importer.file_name_mtl = mtlp
        if texd:
            importer.texture_path = texd

    if not importer:
        print(f'No suitable reader found for {ifp}')
        return

    importer.Update()
    # This is needed before writing out a .wrl file.
    # So we may as well render here anyway.
    ren_win.Render()

    if ofn:
        exporter = None
        if ofp.suffix == '.wrl':
            exporter = vtkVRMLExporter(file_name=ofp,
                                       active_renderer=ren, render_window=ren_win)
        if ofp.suffix.lower() in ('.gltf', 'glb'):
            exporter = vtkGLTFExporter(file_name=ofp,
                                       active_renderer=ren, render_window=ren_win)
        if ofp.suffix.lower() == '.x3d':
            exporter = vtkX3DExporter(file_name=ofp,
                                      active_renderer=ren, render_window=ren_win)
        if ofp.suffix.lower() == '.obj':
            parent_stem = ofp.parent / ofp.stem
            comment = f'Converted by ImportExport from {ifp.name}'
            exporter = vtkOBJExporter(file_prefix=parent_stem,
                                      active_renderer=ren, render_window=ren_win,
                                      obj_file_comment=comment, mtl_file_comment=comment)
        if exporter:
            print(f'Writing {ofp}')
            exporter.Write()
        else:
            print(f'Not Writing {ofp}')
            print(f'Is the extension correct?')

    actors = ren.actors
    actors.InitTraversal()
    actors_sz = actors.number_of_items
    if actors_sz < 2:
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


if __name__ == '__main__':
    main()
