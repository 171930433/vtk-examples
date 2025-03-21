#!/usr/bin/env python3

import json
import sys
from dataclasses import dataclass
from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.util.execution_model import select_ports
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonComputationalGeometry import (
    vtkParametricBoy,
    vtkParametricMobius,
    vtkParametricRandomHills,
    vtkParametricTorus
)
from vtkmodules.vtkCommonCore import (
    vtkCommand,
    vtkFloatArray
)
from vtkmodules.vtkCommonDataModel import vtkPlane
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import (
    vtkCleanPolyData,
    vtkClipPolyData,
    vtkPolyDataNormals,
    vtkPolyDataTangents,
    vtkTriangleFilter
)
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.vtkFiltersModeling import vtkLinearSubdivisionFilter
from vtkmodules.vtkFiltersSources import (
    vtkCubeSource,
    vtkParametricFunctionSource,
    vtkTexturedSphereSource
)
from vtkmodules.vtkIOImage import (
    vtkHDRReader,
    vtkJPEGWriter,
    vtkImageReader2Factory,
    vtkPNGWriter
)
from vtkmodules.vtkImagingCore import vtkImageFlip
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkInteractionWidgets import (
    vtkCameraOrientationWidget,
    vtkOrientationMarkerWidget,
    vtkSliderRepresentation2D,
    vtkSliderWidget
)
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkSkybox,
    vtkTexture,
    vtkRenderer,
    vtkWindowToImageFilter
)
from vtkmodules.vtkRenderingOpenGL2 import (
    vtkCameraPass,
    vtkLightsPass,
    vtkOpaquePass,
    vtkOverlayPass,
    vtkRenderPassCollection,
    vtkSequencePass,
    vtkToneMappingPass
)


def get_program_parameters():
    import argparse
    description = 'Demonstrates physically based rendering, image based lighting, anisotropic texturing and a skybox.'
    epilogue = '''
Physically based rendering sets color, metallicity and roughness of the object.
Image based lighting uses a cubemap texture to specify the environment.
Texturing is used to generate lighting effects.
A Skybox is used to create the illusion of distant three-dimensional surroundings.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('file_name', help='The path to the JSON file e.g. PBR_Skybox_Anisotropy.json.')
    parser.add_argument('-s', '--surface', default='',
                        help='The name of the surface. Overrides the surface entry in the json file.')
    parser.add_argument('-c', '--use_cubemap', action='store_true',
                        help='Build the cubemap from the six cubemap files.'
                             ' Overrides the equirectangular entry in the json file.')
    parser.add_argument('-t', '--use_tonemapping', action='store_true',
                        help='Use tone mapping.')
    parser.add_argument('-omw', action='store_false',
                        help='Use an OrientationMarkerWidget instead of a CameraOrientationWidget.')
    args = parser.parse_args()
    return args.file_name, args.surface, args.use_cubemap, args.use_tonemapping, args.omw


def main():
    colors = vtkNamedColors()

    # Default background color.
    colors.color = ('BkgColor', (26, 51, 102, 255))

    fn, surface_name, use_cubemap, use_tonemapping, use_camera_omw = get_program_parameters()

    fn_path = Path(fn)
    if not fn_path.suffix:
        fn_path = fn_path.with_suffix('.json')
    if not fn_path.is_file():
        print('Unable to find: ', fn_path)
        return
    paths_ok, parameters = get_parameters(fn_path)
    if not paths_ok:
        return

    # Check for missing parameters.
    if 'bkgcolor' not in parameters.keys():
        parameters['bkgcolor'] = 'BkgColor'
    if 'objcolor' not in parameters.keys():
        parameters['objcolor'] = 'White'
    if 'skybox' not in parameters.keys():
        parameters['skybox'] = False
    if surface_name:
        parameters['object'] = surface_name

    res = display_parameters(parameters)
    print('\n'.join(res))
    print()

    if not check_for_missing_textures(parameters, ['albedo', 'normal', 'material', 'anisotropy']):
        return

    ren1 = vtkRenderer(background=colors.GetColor3d('Snow'), viewport=(0.0, 0.0, 0.2, 1.0))
    ren2 = vtkRenderer(background=colors.GetColor3d(parameters['bkgcolor']), viewport=(0.2, 0.0, 1, 1))

    name = Path(sys.argv[0]).stem
    render_window = vtkRenderWindow(size=(1000, 625), window_name=name)
    render_window.AddRenderer(ren1)
    render_window.AddRenderer(ren2)

    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window
    style = vtkInteractorStyleTrackballCamera()
    interactor.interactor_style = style

    # Set up tone mapping, so we can vary the exposure.
    # Custom Passes.
    camera_p = vtkCameraPass()
    seq = vtkSequencePass()
    opaque = vtkOpaquePass()
    lights = vtkLightsPass()
    overlay = vtkOverlayPass()

    passes = vtkRenderPassCollection()
    passes.AddItem(lights)
    passes.AddItem(opaque)
    passes.AddItem(overlay)
    seq.passes = passes
    camera_p.delegate_pass = seq

    tone_mapping_p = vtkToneMappingPass(delegate_pass=camera_p)

    if use_tonemapping:
        ren2.SetPass(tone_mapping_p)

    skybox = vtkSkybox()

    ren2.env_map_irradiance.irradiance_step = 0.3

    # Choose how to generate the skybox.
    is_hdr = False
    has_skybox = False
    gamma_correct = False

    if use_cubemap and 'cubemap' in parameters.keys():
        print('Using the cubemap files to generate the environment texture.')
        env_texture = read_cubemap(parameters['cubemap'])
        if parameters['skybox']:
            skybox.SetTexture(env_texture)
            has_skybox = True
    elif 'equirectangular' in parameters.keys():
        print('Using the equirectangular file to generate the environment texture.')
        env_texture = read_equirectangular_file(parameters['equirectangular'])
        if parameters['equirectangular'].suffix.lower() in '.hdr .pic':
            gamma_correct = True
            is_hdr = True
        if parameters['skybox']:
            # Generate a skybox.
            skybox.SetFloorRight(0, 0, 1)
            skybox.SetProjection(vtkSkybox.Sphere)
            skybox.SetTexture(env_texture)
            has_skybox = True
    else:
        print('An environment texture is required,\n'
              'please add the necessary equirectangular'
              ' or cubemap file paths to the json file.')
        return

    # Turn off the default lighting and use image based lighting.
    ren2.automatic_light_creation = False
    ren2.use_image_based_lighting = True
    if is_hdr:
        ren2.use_spherical_harmonics = True
        ren2.SetEnvironmentTexture(env_texture, False)
    else:
        ren2.use_spherical_harmonics = False
        ren2.SetEnvironmentTexture(env_texture, True)

    # Get the textures
    base_color = read_texture(parameters['albedo'])
    base_color.color_mode = Texture.ColorMode.VTK_COLOR_MODE_DIRECT_SCALARS
    base_color.use_srgb_color_space = True
    normal = read_texture(parameters['normal'])
    normal.color_mode = Texture.ColorMode.VTK_COLOR_MODE_DIRECT_SCALARS
    material = read_texture(parameters['material'])
    material.color_mode = Texture.ColorMode.VTK_COLOR_MODE_DIRECT_SCALARS
    anisotropy = read_texture(parameters['anisotropy'])
    anisotropy.color_mode = Texture.ColorMode.VTK_COLOR_MODE_DIRECT_SCALARS

    # Get the surface.
    surface = parameters['object'].lower()
    available_surfaces = {'boy', 'mobius', 'random hills', 'torus', 'sphere', 'clipped sphere', 'cube', 'clipped cube'}
    if surface not in available_surfaces:
        print(f'\nThe requested surface: {parameters["object"]} is not available.')
        print('Available surfaces are:')
        asl = sorted(list(available_surfaces))
        asl = [asl[i].title() for i in range(0, len(asl))]
        asl = [asl[i:i + 5] for i in range(0, len(asl), 5)]
        for i in range(0, len(asl)):
            s = ', '.join(asl[i])
            if i < len(asl) - 1:
                s += ','
            print(f'   {s}')
        return

    if surface == 'mobius':
        source = get_mobius()
    elif surface == 'random hills':
        source = get_random_hills()
    elif surface == 'torus':
        source = get_torus()
    elif surface == 'sphere':
        source = get_sphere()
    elif surface == 'clipped sphere':
        source = get_clipped_sphere()
    elif surface == 'cube':
        source = get_cube()
    elif surface == 'clipped cube':
        source = get_clipped_cube()
    else:
        source = get_boy()

    mapper = vtkPolyDataMapper()
    source >> mapper

    exposure_coefficient = 1.0
    # Let's use a nonmetallic surface
    diffuse_coefficient = 1.0
    roughness_coefficient = 0.3
    metallic_coefficient = 0.0
    # Other parameters.
    occlusion_strength = 1.0
    normal_scale = 1.0
    anisotropy_coefficient = 1.0
    anisotropy_rotation = 0.0

    actor = vtkActor(mapper=mapper)
    # Enable PBR on the model.
    actor.property.SetInterpolationToPBR()
    # Configure the basic properties.
    # Set the model colour.
    actor.property.color = colors.GetColor3d(parameters['objcolor'])
    actor.property.diffuse = diffuse_coefficient
    actor.property.roughness = roughness_coefficient
    actor.property.metallic = metallic_coefficient
    # Configure textures (needs tcoords on the mesh).
    actor.property.base_color_texture = base_color
    actor.property.o_r_m_texture = material
    actor.property.occlusion_strength = occlusion_strength
    # Needs tcoords, normals and tangents on the mesh.
    actor.property.normal_texture = normal
    actor.property.normal_scale = normal_scale
    actor.property.anisotropy_texture = anisotropy
    actor.property.anisotropy = anisotropy_coefficient
    actor.property.anisotropy_rotation = anisotropy_rotation
    ren2.AddActor(actor)

    if has_skybox:
        if gamma_correct:
            skybox.gamma_correct = True
        else:
            skybox.gamma_correct = False
        ren2.AddActor(skybox)

    # Create the slider callbacks to manipulate various parameters.
    step_size = 1.0 / 7
    y_val = 0.1
    # Setup a slider widget for each varying parameter.
    slider_properties = SliderProperties()

    slider_properties.title_text = 'Exposure'
    slider_properties.range['maximum_value'] = 5.0
    slider_properties.range['value'] = exposure_coefficient
    slider_properties.position = {'point1': (0.1, y_val), 'point2': (0.9, y_val)}
    sw_exposure = make_slider_widget(slider_properties, interactor)
    if use_tonemapping:
        sw_exposure.enable = True
    else:
        sw_exposure.enable = False
    sw_exposure_cb = SliderCallbackExposure(tone_mapping_p)
    sw_exposure.AddObserver(vtkCommand.InteractionEvent, sw_exposure_cb)

    slider_properties.title_text = 'Metallicity'
    slider_properties.range['maximum_value'] = 1.0
    slider_properties.range['value'] = metallic_coefficient
    y_val += step_size
    slider_properties.position = {'point1': (0.1, y_val), 'point2': (0.9, y_val)}
    sw_metallic = make_slider_widget(slider_properties, interactor)
    sw_metallic_cb = SliderCallbackMetallic(actor.GetProperty())
    sw_metallic.AddObserver(vtkCommand.InteractionEvent, sw_metallic_cb)

    slider_properties.title_text = 'Roughness'
    slider_properties.range['value'] = roughness_coefficient
    y_val += step_size
    slider_properties.position = {'point1': (0.1, y_val), 'point2': (0.9, y_val)}
    sw_roughness = make_slider_widget(slider_properties, interactor)
    sw_roughness_cb = SliderCallbackRoughness(actor.GetProperty())
    sw_roughness.AddObserver(vtkCommand.InteractionEvent, sw_roughness_cb)

    slider_properties.title_text = 'Occlusion'
    slider_properties.range['maximum_value'] = 1.0
    slider_properties.range['value'] = occlusion_strength
    y_val += step_size
    slider_properties.position = {'point1': (0.1, y_val), 'point2': (0.9, y_val)}
    sw_occlusion_strength = make_slider_widget(slider_properties, interactor)
    sw_occlusion_strength_cb = SliderCallbackOcclusionStrength(actor.GetProperty())
    sw_occlusion_strength.AddObserver(vtkCommand.InteractionEvent, sw_occlusion_strength_cb)

    slider_properties.title_text = 'Normal'
    slider_properties.range['maximum_value'] = 5.0
    slider_properties.range['value'] = normal_scale
    y_val += step_size
    slider_properties.position = {'point1': (0.1, y_val), 'point2': (0.9, y_val)}
    sw_normal = make_slider_widget(slider_properties, interactor)
    sw_normal_cb = SliderCallbackNormalScale(actor.GetProperty())
    sw_normal.AddObserver(vtkCommand.InteractionEvent, sw_normal_cb)

    slider_properties.title_text = 'Anisotropy'
    slider_properties.range['maximum_value'] = 1.0
    slider_properties.range['value'] = anisotropy_coefficient
    y_val += step_size
    slider_properties.position = {'point1': (0.1, y_val), 'point2': (0.9, y_val)}
    sw_anisotropy = make_slider_widget(slider_properties, interactor)
    sw_anisotropy_cb = SliderCallbackNormalScale(actor.GetProperty())
    sw_anisotropy.AddObserver(vtkCommand.InteractionEvent, sw_anisotropy_cb)

    slider_properties.title_text = 'Anisotropy Rotation'
    slider_properties.range['maximum_value'] = 1.0
    slider_properties.range['value'] = anisotropy_rotation
    y_val += step_size
    slider_properties.position = {'point1': (0.1, y_val), 'point2': (0.9, y_val)}
    sw_anisotropy_rotation = make_slider_widget(slider_properties, interactor)
    sw_anisotropy_rotation_cb = SliderCallbackNormalScale(actor.GetProperty())
    sw_anisotropy_rotation.AddObserver(vtkCommand.InteractionEvent, sw_anisotropy_rotation_cb)

    render_window.Render()

    if use_camera_omw:
        cam_orient_manipulator = vtkCameraOrientationWidget(parent_renderer=ren2)
        # Enable the widget.
        cam_orient_manipulator.On()
    else:
        rgb = [0.0] * 4
        colors.GetColor("Carrot", rgb)
        rgb = tuple(rgb[:3])
        widget = vtkOrientationMarkerWidget(orientation_marker=vtkAxesActor(),
                                            interactor=interactor, default_renderer=ren2,
                                            outline_color=rgb, viewport=(0.8, 0.8, 1.0, 1.0),
                                            enabled=True, interactive=True, zoom=1.5)

    print_callback = PrintCallback(interactor, name, 1, False)
    # print_callback = PrintCallback(interactor, name + '.jpg', 1, False)
    interactor.AddObserver('KeyPressEvent', print_callback)

    interactor.Start()


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

    This assumes that the files corresponding to the images
     are already ordered as:
      [right, left, top, bottom, front, back]
      or [+x, -x, +y, -y, +z, -z]

    :param cubemap: The paths to the six cubemap files.
    :return: The cubemap texture.
    """
    cube_map = vtkTexture(cube_map=True, mipmap=True, interpolate=True)

    flipped_images = list()
    for fn in cubemap:
        # Read the images.
        reader_factory = vtkImageReader2Factory()
        img_reader = reader_factory.CreateImageReader2(str(fn))
        img_reader.file_name = str(fn)

        # Each image must be flipped in Y due to canvas
        #  versus vtk ordering.
        flip = vtkImageFlip(filtered_axis=1)
        img_reader >> flip
        flipped_images.append(flip)

    for i in range(0, len(flipped_images)):
        flipped_images[i] >> select_ports(i, cube_map)

    return cube_map


def read_equirectangular_file(fn_path):
    """
    Read an equirectangular environment file and convert to a texture.

    :param fn_path: The equirectangular file path.
    :return: The texture.
    """
    texture = vtkTexture(cube_map=False, mipmap=True, interpolate=True)

    suffix = fn_path.suffix.lower()
    if suffix in ['.jpeg', '.jpg', '.png']:
        reader_factory = vtkImageReader2Factory()
        img_reader = reader_factory.CreateImageReader2(str(fn_path))
        img_reader.SetFileName(str(fn_path))

        img_reader >> texture

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
        reader.SetFileName(str(fn_path))

        texture.SetColorModeToDirectScalars()
        reader >> texture

    return texture


def read_texture(image_path):
    """
    Read an image and convert it to a texture
    :param image_path: The image path.
    :return: The texture.
    """

    suffix = image_path.suffix.lower()
    valid_extensions = ['.jpg', '.png', '.bmp', '.tiff', '.pnm', '.pgm', '.ppm']
    if suffix not in valid_extensions:
        print('Unable to read the texture file (wrong extension):', image_path)
        return None

    # Read the images
    reader_factory = vtkImageReader2Factory()
    img_reader = reader_factory.CreateImageReader2(str(image_path))
    img_reader.file_name = str(image_path)

    texture = vtkTexture(interpolate=True)
    img_reader >> texture

    return texture


def check_for_missing_textures(parameters, wanted_textures):
    """
    Check that the needed textures exist.

    :param parameters: The parameters.
    :param wanted_textures: The wanted textures.
    :return: True if all the wanted textures are present.
    """
    have_textures = True
    for texture_name in wanted_textures:
        if texture_name not in parameters:
            print('Missing texture:', texture_name)
            have_textures = False
        elif not parameters[texture_name]:
            print('No texture path for:', texture_name)
            have_textures = False

    return have_textures


def get_boy():
    surface = vtkParametricBoy()

    u_resolution = 51
    v_resolution = 51
    source = vtkParametricFunctionSource(parametric_function=surface,
                                         u_resolution=u_resolution, v_resolution=v_resolution,
                                         generate_texture_coordinates=True)

    tangents = vtkPolyDataTangents()

    return source >> tangents


def get_mobius():
    minimum_v = -0.25
    maximum_v = 0.25
    surface = vtkParametricMobius(minimum_v=minimum_v, maximum_v=maximum_v, )

    u_resolution = 51
    v_resolution = 51
    source = vtkParametricFunctionSource(parametric_function=surface,
                                         u_resolution=u_resolution, v_resolution=v_resolution,
                                         generate_texture_coordinates=True)

    # Build the tangents.
    tangents = vtkPolyDataTangents()

    transform = vtkTransform()
    transform.RotateX(-90.0)

    transform_filter = vtkTransformPolyDataFilter(transform=transform)

    return source >> tangents >> transform_filter


def get_random_hills():
    random_seed = 1
    number_of_hills = 30
    # If you want a plane
    # hill_amplitude=0
    surface = vtkParametricRandomHills(random_seed=random_seed, number_of_hills=number_of_hills)

    u_resolution = 51
    v_resolution = 51
    source = vtkParametricFunctionSource(parametric_function=surface,
                                         u_resolution=u_resolution, v_resolution=v_resolution,
                                         generate_texture_coordinates=True)

    # Build the tangents.
    tangents = vtkPolyDataTangents()

    transform = vtkTransform()
    transform.Translate(0.0, 5.0, 15.0)
    transform.RotateX(-90.0)

    transform_filter = vtkTransformPolyDataFilter(transform=transform)

    return source >> tangents >> transform_filter


def get_sphere():
    theta_resolution = 32
    phi_resolution = 32
    surface = vtkTexturedSphereSource(theta_resolution=theta_resolution, phi_resolution=phi_resolution)

    # Now the tangents.
    tangents = vtkPolyDataTangents()

    return surface >> tangents


def get_clipped_sphere():
    theta_resolution = 32
    phi_resolution = 32
    surface = vtkTexturedSphereSource(theta_resolution=theta_resolution, phi_resolution=phi_resolution)

    clip_plane = vtkPlane(origin=(0, 0.3, 0), normal=(0, -1, 0))

    clipper = vtkClipPolyData(clip_function=clip_plane)
    clipper.GenerateClippedOutputOn()

    # Now the tangents.
    tangents = vtkPolyDataTangents()

    return surface >> clipper >> tangents


def get_torus():
    surface = vtkParametricTorus()

    u_resolution = 51
    v_resolution = 51
    source = vtkParametricFunctionSource(parametric_function=surface,
                                         u_resolution=u_resolution, v_resolution=v_resolution,
                                         generate_texture_coordinates=True)

    # Build the tangents.
    tangents = vtkPolyDataTangents()

    transform = vtkTransform()
    transform.RotateX(-90.0)

    transform_filter = vtkTransformPolyDataFilter(transform=transform)

    return source >> tangents >> transform_filter


def get_cube():
    surface = vtkCubeSource()

    # Triangulate.
    triangulation = vtkTriangleFilter()
    # Subdivide the triangles.
    subdivide = vtkLinearSubdivisionFilter(number_of_subdivisions=3)
    # Build the tangents.
    tangents = vtkPolyDataTangents()

    return surface >> triangulation >> subdivide >> tangents


def get_clipped_cube():
    surface = vtkCubeSource()

    # Triangulate.
    triangulation = vtkTriangleFilter()

    # Subdivide the triangles
    subdivide = vtkLinearSubdivisionFilter(number_of_subdivisions=5)

    clip_plane = vtkPlane(origin=(0, 0.3, 0), normal=(0, -1, -1))

    clipper = vtkClipPolyData(clip_function=clip_plane)
    clipper.GenerateClippedOutputOn()

    cleaner = vtkCleanPolyData(tolerance=0.005)

    normals = vtkPolyDataNormals(feature_angle=60, flip_normals=True)

    # Now the tangents.
    tangents = vtkPolyDataTangents(compute_cell_tangents=True, compute_point_tangents=True)

    return surface >> triangulation >> subdivide >> clipper >> cleaner >> normals >> tangents


def uv_tcoords(u_resolution, v_resolution, pd):
    """
    Generate u, v texture coordinates on a parametric surface.
    :param u_resolution: u resolution
    :param v_resolution: v resolution
    :param pd: The polydata representing the surface.
    :return: The polydata with the texture coordinates added.
    """
    u0 = 1.0
    v0 = 0.0
    du = 1.0 / (u_resolution - 1)
    dv = 1.0 / (v_resolution - 1)
    num_pts = pd.GetNumberOfPoints()
    t_coords = vtkFloatArray(number_of_components=2, number_of_tuples=num_pts, name='Texture Coordinates')
    pt_id = 0
    u = u0
    for i in range(0, u_resolution):
        v = v0
        for j in range(0, v_resolution):
            tc = [u, v]
            t_coords.SetTuple(pt_id, tc)
            v += dv
            pt_id += 1
        u -= du
    pd.point_data.SetTCoords(t_coords)
    return pd


class SliderProperties:
    dimensions = {
        'tube_width': 0.008,
        'slider_length': 0.075, 'slider_width': 0.025,
        'end_cap_length': 0.025, 'end_cap_width': 0.025,
        'title_height': 0.025, 'label_height': 0.020,
    }
    colors = {
        'title_color': 'Black', 'label_color': 'Black', 'slider_color': 'BurlyWood',
        'selected_color': 'Lime', 'bar_color': 'Black', 'bar_ends_color': 'Indigo',
    }
    range = {'minimum_value': 0.0, 'maximum_value': 1.0, 'value': 1.0}
    title_text = '',
    position = {'point1': (0.1, 0.1), 'point2': (0.9, 0.1)}


def make_slider_widget(slider_properties, interactor):
    """
    Make a slider widget.
    :param slider_properties: range, title name, dimensions, colors, and position.
    :param interactor: The vtkInteractor.
    :return: The slider widget.
    """
    colors = vtkNamedColors()

    slider_rep = vtkSliderRepresentation2D(minimum_value=slider_properties.range['minimum_value'],
                                           maximum_value=slider_properties.range['maximum_value'],
                                           value=slider_properties.range['value'],
                                           title_text=slider_properties.title_text,
                                           tube_width=slider_properties.dimensions['tube_width'],
                                           slider_length=slider_properties.dimensions['slider_length'],
                                           slider_width=slider_properties.dimensions['slider_width'],
                                           end_cap_length=slider_properties.dimensions['end_cap_length'],
                                           end_cap_width=slider_properties.dimensions['end_cap_width'],
                                           title_height=slider_properties.dimensions['title_height'],
                                           label_height=slider_properties.dimensions['label_height'],
                                           )

    # Set the color properties.
    slider_rep.title_property.color = colors.GetColor3d(slider_properties.colors['title_color'])
    slider_rep.label_property.color = colors.GetColor3d(slider_properties.colors['label_color'])
    slider_rep.tube_property.color = colors.GetColor3d(slider_properties.colors['bar_color'])
    slider_rep.cap_property.color = colors.GetColor3d(slider_properties.colors['bar_ends_color'])
    slider_rep.slider_property.color = colors.GetColor3d(slider_properties.colors['slider_color'])
    slider_rep.selected_property.color = colors.GetColor3d(slider_properties.colors['selected_color'])

    # Set the position.
    slider_rep.point1_coordinate.coordinate_system = Coordinate.CoordinateSystem.VTK_NORMALIZED_VIEWPORT
    slider_rep.point1_coordinate.value = slider_properties.position['point1']
    slider_rep.point2_coordinate.coordinate_system = Coordinate.CoordinateSystem.VTK_NORMALIZED_VIEWPORT
    slider_rep.point2_coordinate.value = slider_properties.position['point2']

    widget = vtkSliderWidget(representation=slider_rep, interactor=interactor, enabled=True)
    widget.SetAnimationModeToAnimate()

    return widget


class SliderCallbackExposure:
    def __init__(self, tone_mapping_property):
        self.tone_mapping_property = tone_mapping_property

    def __call__(self, caller, ev):
        slider_widget = caller
        value = slider_widget.representation.value
        self.tone_mapping_property.exposure = value


class SliderCallbackMetallic:
    def __init__(self, actor_property):
        self.actor_property = actor_property

    def __call__(self, caller, ev):
        slider_widget = caller
        value = slider_widget.representation.value
        self.actor_property.metallic = value


class SliderCallbackRoughness:
    def __init__(self, actor_property):
        self.actor_property = actor_property

    def __call__(self, caller, ev):
        slider_widget = caller
        value = slider_widget.representation.value
        self.actor_property.roughness = value


class SliderCallbackOcclusionStrength:
    def __init__(self, actor_property):
        self.actor_property = actor_property

    def __call__(self, caller, ev):
        slider_widget = caller
        value = slider_widget.representation.value
        self.actor_property.occlusion_strength = value


class SliderCallbackNormalScale:
    def __init__(self, actor_property):
        self.actor_property = actor_property

    def __call__(self, caller, ev):
        slider_widget = caller
        value = slider_widget.representation.value
        self.actor_property.normal_scale = value


class SliderCallbackAnisotropy:
    def __init__(self, actor_property):
        self.actor_property = actor_property

    def __call__(self, caller, ev):
        slider_widget = caller
        value = slider_widget.representation.value
        self.actor_property.anisotropy = value


class SliderCallbackAnisotropyRotation:
    def __init__(self, actor_property):
        self.actor_property = actor_property

    def __call__(self, caller, ev):
        slider_widget = caller
        value = slider_widget.representation.value
        self.actor_property.anisotropy_rotation = value


class PrintCallback:
    def __init__(self, caller, file_name, image_quality=1, rgba=True):
        """
        Set the parameters for writing the
         render window view to an image file.

        :param caller: The caller for the callback.
        :param file_name: The image file name.
        :param image_quality: The image quality.
        :param rgba: The buffer type, (if true, there is no background in the screenshot).
        """
        self.caller = caller
        self.image_quality = image_quality
        self.rgba = rgba
        if not file_name:
            self.path = None
            print("A file name is required.")
            return
        pth = Path(file_name).absolute()
        valid_suffixes = ['.jpeg', '.jpg', '.png']
        if pth.suffix:
            ext = pth.suffix.lower()
        else:
            ext = '.png'
        if ext not in valid_suffixes:
            ext = '.png'
        self.suffix = ext
        self.path = Path(str(pth)).with_suffix(ext)

    def __call__(self, caller, ev):
        if not self.path:
            print('A file name is required.')
            return
        # Save the screenshot.
        if caller.GetKeyCode() == 'k':
            w2if = vtkWindowToImageFilter(input=caller.GetRenderWindow(),
                                          scale=(self.image_quality, self.image_quality),
                                          read_front_buffer=True)
            if self.rgba:
                w2if.SetInputBufferTypeToRGBA()
            else:
                w2if.SetInputBufferTypeToRGB()
            if self.suffix in ['.jpeg', '.jpg']:
                writer = vtkJPEGWriter(file_name=self.path)
            else:
                writer = vtkPNGWriter(file_name=self.path)
            w2if >> writer
            writer.Write()
            print('Screenshot saved to:', self.path)


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


@dataclass(frozen=True)
class Coordinate:
    @dataclass(frozen=True)
    class CoordinateSystem:
        VTK_DISPLAY: int = 0
        VTK_NORMALIZED_DISPLAY: int = 1
        VTK_VIEWPORT: int = 2
        VTK_NORMALIZED_VIEWPORT: int = 3
        VTK_VIEW: int = 4
        VTK_POSE: int = 5
        VTK_WORLD: int = 6
        VTK_USERDEFINED: int = 7


if __name__ == '__main__':
    main()
