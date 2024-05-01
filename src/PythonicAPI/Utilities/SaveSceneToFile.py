#!/usr/bin/env python3

from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
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


def main():
    pd_fn, scene_fn = get_program_parameters()

    colors = vtkNamedColors()

    poly_data = read_poly_data(pd_fn)

    mapper = vtkPolyDataMapper()
    poly_data >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.diffuse_color = colors.GetColor3d('Crimson')
    actor.property.specular = 0.6
    actor.property.specular_power = 30

    renderer = vtkRenderer(background=colors.GetColor3d('Silver'))
    render_window = vtkRenderWindow(window_name='SaveSceneToFieldData')
    render_window.AddRenderer(renderer)

    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    renderer.AddActor(actor)

    # Interact to change the camera.
    render_window.Render()
    render_window_interactor.Start()

    # After the interaction is done, save the scene.
    save_scene_to_file(scene_fn, actor, renderer.active_camera)
    render_window.Render()
    render_window_interactor.Start()

    # After interaction , restore the scene.
    restore_scene_from_file(scene_fn, actor, renderer.active_camera)
    render_window.Render()
    render_window_interactor.Start()


def get_program_parameters():
    import argparse
    description = 'Saving a scene to a file.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('data_file', help='A polydata file e.g. Armadillo.ply.')
    parser.add_argument('scene_file', help='The file to save the scene to.')
    args = parser.parse_args()
    return args.data_file, args.scene_file


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


def save_scene_to_file(file_name, actor, camera):
    # Actor
    #   Position, orientation, origin, scale, usrmatrix, usertransform
    # Camera
    #   FocalPoint, Position, ViewUp, ViewAngle, ClippingRange

    fp_format = '{0:.6f}'
    res = dict()
    res['Camera:FocalPoint'] = ', '.join(fp_format.format(n) for n in camera.GetFocalPoint())
    res['Camera:Position'] = ', '.join(fp_format.format(n) for n in camera.GetPosition())
    res['Camera:ViewUp'] = ', '.join(fp_format.format(n) for n in camera.GetViewUp())
    res['Camera:ViewAngle'] = fp_format.format(camera.GetViewAngle())
    res['Camera:ClippingRange'] = ', '.join(fp_format.format(n) for n in camera.GetClippingRange())

    path = Path(file_name)
    with path.open(mode='w') as f:
        for k, v in res.items():
            f.write(k + ' ' + v + '\n')


def restore_scene_from_file(file_name, actor, camera):
    import re

    # Some regular expressions.

    re_cp = re.compile(r'^Camera:Position')
    re_cfp = re.compile(r'^Camera:FocalPoint')
    re_cvu = re.compile(r'^Camera:ViewUp')
    re_cva = re.compile(r'^Camera:ViewAngle')
    re_ccr = re.compile(r'^Camera:ClippingRange')
    keys = [re_cp, re_cfp, re_cvu, re_cva, re_ccr]

    # float_number = re.compile(r'[^0-9.\-]*([0-9e.\-]*[^,])[^0-9.\-]*([0-9e.\-]*[^,])[^0-9.\-]*([0-9e.\-]*[^,])')
    # float_scalar = re.compile(r'[^0-9.\-]*([0-9.\-e]*[^,])')

    res = dict()
    path = Path(file_name)
    with path.open(mode='r') as f:
        for cnt, line in enumerate(f):
            if not line.strip():
                continue
            line = line.strip().replace(',', '').split()
            for i in keys:
                m = re.match(i, line[0])
                if m:
                    k = m.group(0)
                    if m:
                        #  Convert the rest of the line to floats.
                        v = list(map(lambda x: float(x), line[1:]))
                        if len(v) == 1:
                            res[k] = v[0]
                        else:
                            res[k] = v
    for k, v in res.items():
        if re.match(re_cp, k):
            camera.position = v
        elif re.match(re_cfp, k):
            camera.focal_point = v
        elif re.match(re_cvu, k):
            camera.view_up = v
        elif re.match(re_cva, k):
            camera.view_angle = v
        elif re.match(re_ccr, k):
            camera.clipping_range = v


if __name__ == '__main__':
    main()
