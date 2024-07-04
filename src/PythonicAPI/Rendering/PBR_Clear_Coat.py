#!/usr/bin/env python3

import json
from dataclasses import dataclass
from pathlib import Path

from vtkmodules.util.execution_model import select_ports
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import (
    vtkPolyDataTangents,
    vtkTriangleFilter
)
from vtkmodules.vtkFiltersSources import vtkCubeSource
from vtkmodules.vtkIOImage import (
    vtkHDRReader,
    vtkImageReader2Factory,
    vtkPNGReader
)
from vtkmodules.vtkImagingCore import vtkImageFlip
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkLight,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkSkybox,
    vtkTexture
)
from vtkmodules.vtkRenderingOpenGL2 import vtkOpenGLRenderer


def get_program_parameters():
    import argparse
    description = 'Render a cube with custom texture mapping and a coat normal texture.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('file_name',
                        help='The path to the JSON file e.g. PBR_Parameters.json.')
    parser.add_argument('-e', '--use_equirectangular', action='store_true',
                        help='Use the equirectangular entry in the json file.')
    args = parser.parse_args()
    return args.file_name, args.use_equirectangular


def main():
    fn, use_cubemap = get_program_parameters()
    use_cubemap = not use_cubemap
    fn_path = Path(fn)
    if not fn_path.suffix:
        fn_path = fn_path.with_suffix(".json")
    if not fn_path.is_file():
        print('Unable to find: ', fn_path)
    paths_ok, parameters = get_parameters(fn_path)
    if not paths_ok:
        return
    res = display_parameters(parameters)
    print('\n'.join(res))
    print()

    colors = vtkNamedColors()

    light = vtkLight()
    light.SetPosition(2.0, 0.0, 2.0)
    light.SetFocalPoint(0.0, 0.0, 0.0)

    ren = vtkOpenGLRenderer(background=colors.GetColor3d('Black'), automatic_light_creation=False)
    ren.AddLight(light)
    ren_win = vtkRenderWindow(size=(600, 600), window_name='PBR_Anisotropy')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win
    style = vtkInteractorStyleTrackballCamera()
    iren.interactor_style = style

    skybox = vtkSkybox()

    irradiance = ren.GetEnvMapIrradiance()
    irradiance.SetIrradianceStep(0.3)

    # Choose how to generate the skybox.
    is_hdr = False
    has_skybox = False
    gamma_correct = False

    if use_cubemap and 'cubemap' in parameters.keys():
        print('Using the cubemap files to generate the environment texture.')
        env_texture = read_cubemap(parameters['cubemap'])
        if parameters['skybox']:
            skybox.texture = env_texture
            has_skybox = True
    elif 'equirectangular' in parameters.keys():
        print('Using the equirectangular file to generate the environment texture.')
        env_texture = read_equirectangular_file(parameters['equirectangular'])
        if parameters['equirectangular'].suffix.lower() in '.hdr .pic':
            gamma_correct = True
            is_hdr = True
        if parameters['skybox']:
            # Generate a skybox.
            skybox.floor_right = (0, 0, 1)
            skybox.projection = vtkSkybox.Sphere
            skybox.texture = env_texture
            has_skybox = True
    else:
        print('An environment texture is required,\n'
              'please add the necessary equirectangular'
              ' or cubemap file paths to the json file.')
        return

    # Turn off the default lighting and use image based lighting.
    # ren.automatic_light_creation = False
    ren.use_image_based_lighting = True
    if is_hdr:
        ren.use_spherical_harmonics = True
        ren.SetEnvironmentTexture(env_texture, False)
    else:
        ren.use_spherical_harmonics = False
        ren.SetEnvironmentTexture(env_texture, True)

    cube = vtkCubeSource()

    triangulation = vtkTriangleFilter()

    tangents = vtkPolyDataTangents()

    mapper = vtkPolyDataMapper()
    cube >> triangulation >> tangents >> mapper

    material_reader = vtkPNGReader(file_name=parameters['material'])
    material = vtkTexture(interpolate=True)
    material_reader >> material

    albedo_reader = vtkPNGReader(file_name=parameters['albedo'])
    albedo = vtkTexture(use_srgb_color_space=True, interpolate=True)
    albedo_reader >> albedo

    normal_reader = vtkPNGReader(file_name=parameters['normal'])
    normal = vtkTexture(interpolate=True)
    normal_reader >> normal

    coat_normal = vtkTexture(interpolate=True)
    normal_reader >> coat_normal
    # Uncomment this if you want a similar image to the VTK test image.
    # flip = vtkImageFlip(filtered_axes=0)
    # normal_reader >> flip >> coat_normal

    actor = vtkActor(mapper=mapper, orientation=(0.0, 25.0, 0.0))
    actor.property.interpolation = Property.Interpolation.VTK_PBR

    # Set metallic, roughness and coat strength to 1.0 as they act as multipliers
    # with texture value.
    actor.property.metallic = 1.0
    actor.property.roughness = 1.0
    actor.property.coat_strength = 1.0
    actor.property.color = colors.GetColor3d('Red')

    actor.property.base_color_texture = albedo
    actor.property.orm_texture = material
    actor.property.normal_texture = normal
    actor.property.coat_normal_texture = coat_normal

    ren.AddActor(actor)

    if has_skybox:
        if gamma_correct:
            skybox.gamma_correct = True
        else:
            skybox.gamma_correct = False
        ren.AddActor(skybox)

    ren_win.Render()
    ren.active_camera.Zoom(1.5)
    # ren_win.Render()

    iren.Start()


def get_parameters(fn_path):
    """
    Read the parameters from a JSON file and check that the file paths exist.

    :param fn_path: The path to the JSON file.
    :return: True if the paths correspond to files and the parameters.
    """
    with open(fn_path) as data_file:
        json_data = json.load(data_file)
    parameters = dict()

    # Extract the values.
    keys_no_paths = {'title', 'object', 'objcolor', 'bkgcolor', 'skybox'}
    keys_with_paths = {'cubemap', 'equirectangular', 'albedo', 'normal', 'material', 'coat', 'anisotropy', 'emissive'}
    paths_ok = True
    for k, v in json_data.items():
        if k in keys_no_paths:
            parameters[k] = v
            continue
        if k in keys_with_paths:
            if k == 'cubemap':
                if ('root' in v) and ('files' in v):
                    root = fn_path.parent / Path(v['root'])
                    if not root.exists():
                        print(f'Bad cubemap path: {root}')
                        paths_ok = False
                    elif len(v['files']) != 6:
                        print(f'Expect six cubemap file names.')
                        paths_ok = False
                    else:
                        cm = list(map(lambda p: root / p, v['files']))
                        for fn in cm:
                            if not fn.is_file():
                                paths_ok = False
                                print(f'Not a file {fn}')
                        if paths_ok:
                            parameters['cubemap'] = cm
                else:
                    paths_ok = False
                    print('Missing the key "root" and/or the key "fíles" for the cubemap.')
            else:
                fn = fn_path.parent / Path(v)
                if not fn.exists():
                    print(f'Bad {k} path: {fn}')
                    paths_ok = False
                else:
                    parameters[k] = fn

    # Set Boy as the default surface.
    if ('object' in parameters.keys() and not parameters['object']) or 'object' not in parameters.keys():
        parameters['object'] = 'Boy'

    return paths_ok, parameters


def display_parameters(parameters):
    res = list()
    parameter_keys = ['title', 'object', 'objcolor', 'bkgcolor', 'skybox', 'cubemap', 'equirectangular', 'albedo',
                      'normal', 'material', 'coat', 'anisotropy', 'emissive']
    for k in parameter_keys:
        if k != 'cubemap':
            if k in parameters:
                res.append(f'{k:15}: {parameters[k]}')
        else:
            if k in parameters:
                for idx in range(len(parameters[k])):
                    if idx == 0:
                        res.append(f'{k:15}: {parameters[k][idx]}')
                    else:
                        res.append(f'{" " * 17}{parameters[k][idx]}')
    return res


def read_cubemap(cubemap):
    """
    Read six images forming a cubemap.

    :param cubemap: The paths to the six cubemap files.
    :return: The cubemap texture.
    """
    cube_map = vtkTexture(mipmap=True, interpolate=True, cube_map=True)

    i = 0
    for fn in cubemap:
        # Read the images.
        img_reader = vtkImageReader2Factory().CreateImageReader2(str(fn))
        img_reader.file_name = str(fn)

        # Each image must be flipped in Y due to canvas
        #  versus vtk ordering.
        flip = vtkImageFlip(filtered_axis=1)
        img_reader >> flip
        flip >> select_ports(i, cube_map)
        i += 1

    return cube_map


def read_equirectangular_file(fn_path):
    """
    Read an equirectangular environment file and convert to a texture.

    :param fn_path: The equirectangular file path.
    :return: The texture.
    """
    texture = vtkTexture(mipmap=True, interpolate=True)

    suffix = fn_path.suffix.lower()
    if suffix in ['.jpeg', '.jpg', '.png']:
        img_reader = vtkImageReader2Factory().CreateImageReader2(str(fn_path))
        img_reader.file_name = str(fn_path)
        select_ports(img_reader, 0) >> texture

    else:
        reader = vtkHDRReader()
        extensions = reader.GetFileExtensions()
        # Check the image can be read.
        if not reader.CanReadFile(str(fn_path)):
            print('CanReadFile failed for ', fn_path)
            return None
        if suffix not in extensions:
            print('Unable to read this file extension: ', suffix)
            return None
        reader.file_name = str(fn_path)

        texture.color_mode = Texture.ColorMode.VTK_COLOR_MODE_DIRECT_SCALARS
        reader >> texture

    return texture


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


@dataclass(frozen=True)
class Texture:
    @dataclass(frozen=True)
    class Quality:
        VTK_TEXTURE_QUALITY_DEFAULT: int = 0
        VTK_TEXTURE_QUALITY_16BIT: int = 16
        VTK_TEXTURE_QUALITY: int = 32

    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_MODE_DEFAULT: int = 0
        VTK_COLOR_MODE_MAP_SCALARS: int = 1
        VTK_COLOR_MODE_DIRECT_SCALARS: int = 2


if __name__ == '__main__':
    main()
