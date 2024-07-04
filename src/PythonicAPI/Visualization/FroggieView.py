#!/usr/bin/env python3

import json
from dataclasses import dataclass
from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkCommand,
    vtkLookupTable
)
from vtkmodules.vtkCommonMath import vtkMatrix4x4
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import vtkPolyDataNormals
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.vtkIOLegacy import vtkPolyDataReader
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkInteractionWidgets import (
    vtkCameraOrientationWidget,
    vtkOrientationMarkerWidget,
    vtkSliderRepresentation2D,
    vtkSliderWidget
)
from vtkmodules.vtkRenderingAnnotation import (
    vtkAxesActor,
    vtkAnnotatedCubeActor,
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkPropAssembly,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters(argv):
    import argparse
    description = 'View surfaces of a segmented frog dataset using preprocessed VTK tissue files.'
    epilogue = '''
Sliders are provided to control the opacity of the displayed tissues.
Up to fifteen different surfaces may be viewed.

Note:
   If you want to use brainbin (the brain with no gaussian smoothing),
    instead of brain, then request it with -t brainbin
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', action='store_const', dest='view', const='a',
                       help='The view corresponds to Fig 12-9a in the VTK Textbook')
    group.add_argument('-b', action='store_const', dest='view', const='b',
                       help='The view corresponds to Fig 12-9b in the VTK Textbook')
    group.add_argument('-c', action='store_const', dest='view', const='c',
                       help='The view corresponds to Fig 12-9c in the VTK Textbook')
    group.add_argument('-d', action='store_const', dest='view', const='d',
                       help='The view corresponds to Fig 12-9d in the VTK Textbook')
    group.add_argument('-l', action='store_const', dest='view', const='l',
                       help='The view corresponds to looking down on the anterior surface')
    group.add_argument('-p', action='store_const', dest='view', const='p',
                       help='The view corresponds to looking down on the posterior surface (the default)')
    parser.set_defaults(type=None)

    parser.add_argument('file_name', help='The path to the JSON file e.g. Frog_vtk.json.')
    parser.add_argument('-n', action='store_true', dest='omit_sliders', help='No sliders.')
    parser.add_argument('-t', nargs='+', dest='tissues', action='append', help='Select one or more tissues.')
    args = parser.parse_args()
    return args.file_name, args.view, args.omit_sliders, args.tissues


def main(fn, select_figure, no_sliders, chosen_tissues):
    if not select_figure:
        select_figure = 'p'

    fn_path = Path(fn)
    if not fn_path.suffix:
        fn_path = fn_path.with_suffix(".json")
    if not fn_path.is_file():
        print('Unable to find: ', fn_path)
        return
    parsed_ok, parameters = parse_json(fn_path)
    if not parsed_ok:
        print('Unable to parse the JSON file.')
        return

    color_lut = create_tissue_lut(parameters['indices'], parameters['colors'])

    tissues = parameters['names']
    if select_figure:
        if select_figure == 'b':
            # No skin.
            tissues = parameters['fig12-9b']
        if select_figure in ['c', 'd']:
            # No skin, blood and skeleton.
            tissues = parameters['fig12-9cd']

    if chosen_tissues:
        chosen_tissues = set(val for sublist in chosen_tissues for val in sublist)
        res = list()
        has_brainbin = False
        if 'brainbin' in chosen_tissues:
            print('Using brainbin instead of brain.')
            res.append('brainbin')
            parameters['indices'].pop('brain', None)
            parameters['indices']['brainbin'] = 2
            parameters['colors'].pop('brain', None)
            parameters['colors']['brainbin'] = 'beige'
            has_brainbin = True
        for ct in chosen_tissues:
            if has_brainbin and ct in ['brain', 'brainbin']:
                continue
            if ct in tissues:
                res.append(ct)
            else:
                print(f'Tissue: {ct} is not available.')
                print(f'Available tissues are: {", ".join(tissues)} and brainbin')
                return
        if len(res) == 1 and 'skin' in res:
            parameters['opacity']['skin'] = 1.0
        tissues = res

    colors = vtkNamedColors()
    colors.SetColor('ParaViewBkg', 82, 87, 110, 255)

    # Setup render window, renderers, and interactor.
    ren = vtkRenderer(background=colors.GetColor3d('ParaViewBkg'))
    ren_win = vtkRenderWindow(window_name='FroggieView')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win
    style = vtkInteractorStyleTrackballCamera()
    iren.interactor_style = style

    sliders = dict()
    left_step_size = 1.0 / 9
    left_pos_y = 0.275
    left_pos_x0 = 0.02
    left_pos_x1 = 0.18
    right_step_size = 1.0 / 9
    right_pos_y = 0.05
    right_pos_x0 = 0.8 + 0.02
    right_pos_x1 = 0.8 + 0.18

    slider_count = 0

    color_size = len(max(parameters['colors'].values(), key=len))
    name_size = len(max(parameters['names'], key=len))
    int_size = 2
    line = '-' * (7 + name_size + color_size)
    res = [line,
           f'{"Tissue":<{name_size}s} {"Label":{int_size + 3}s} {"Color":>{color_size}s}',
           line]

    for name in tissues:
        reader = vtkPolyDataReader(file_name=parameters['vtk_files'][name])

        trans = SliceOrder().get(parameters['orientation'][name])
        trans.Scale(1, -1, -1)

        tf = vtkTransformPolyDataFilter(transform=trans)

        normals = vtkPolyDataNormals(feature_angle=60.0)

        mapper = vtkPolyDataMapper()
        reader >> tf >> normals >> mapper

        actor = vtkActor(mapper=mapper)

        actor.property.opacity = parameters['opacity'][name]
        actor.property.diffuse_color = color_lut.GetTableValue(parameters['indices'][name])[:3]
        actor.property.specular = 0.5
        actor.property.specular_power = 10

        ren.AddActor(actor)

        if not no_sliders:
            slider_properties = SliderProperties()
            slider_properties.range['value'] = parameters['opacity'][name]
            slider_properties.title_text = name

            # Screen coordinates.
            if slider_count < 7:
                slider_properties.position['point1'] = (left_pos_x0, left_pos_y)
                slider_properties.position['point2'] = (left_pos_x1, left_pos_y)
                left_pos_y += left_step_size
            else:
                slider_properties.position['point1'] = (right_pos_x0, right_pos_y)
                slider_properties.position['point2'] = (right_pos_x1, right_pos_y)
                right_pos_y += right_step_size

            slider_widget = make_slider_widget(slider_properties, color_lut, parameters['indices'][name], iren)

            cb = SliderCallback(actor.GetProperty())
            slider_widget.AddObserver(vtkCommand.InteractionEvent, cb)
            sliders[name] = slider_widget
            slider_count += 1

        res.append(
            f'{name:<{name_size}s} {parameters["indices"][name]:{int_size + 3}d} {parameters["colors"][name]:>{color_size}s}')

    res.append(line)
    print('\n'.join(res))

    if no_sliders:
        ren_win.size = (1024, 1024)
    else:
        ren_win.size = (1024 + 400, 1024)

    #  Final view.
    camera = ren.active_camera
    # Superior Anterior Left
    labels = 'sal'
    if select_figure == 'a':
        # Fig 12-9a in the VTK Textbook
        camera.position = (742.731237, -441.329635, -877.192015)
        camera.focal_point = (247.637687, 120.680880, -253.487473)
        camera.view_up = (-0.323882, -0.816232, 0.478398)
        camera.distance = 974.669585
        camera.clipping_range = (311.646383, 1803.630763)
    elif select_figure == 'b':
        # Fig 12-9b in the VTK Textbook
        camera.position = (717.356065, -429.889054, -845.381584)
        camera.focal_point = (243.071719, 100.996487, -247.446340)
        camera.view_up = (-0.320495, -0.820148, 0.473962)
        camera.distance = 929.683631
        camera.clipping_range = (293.464446, 1732.794957)
    elif select_figure == 'c':
        # Fig 12-9c in the VTK Textbook
        camera.position = (447.560023, -136.611491, -454.753689)
        camera.focal_point = (253.142277, 91.949451, -238.583973)
        camera.view_up = (-0.425438, -0.786048, 0.448477)
        camera.distance = 369.821187
        camera.clipping_range = (0.829116, 829.115939)
    elif select_figure == 'd':
        # Fig 12-9d in the VTK Textbook
        camera.position = (347.826249, -469.633647, -236.234262)
        camera.focal_point = (296.893207, 89.307704, -225.156581)
        camera.view_up = (-0.687345, -0.076948, 0.722244)
        camera.distance = 561.366478
        camera.clipping_range = (347.962064, 839.649856)
    elif select_figure == 'l':
        # Orient so that we look down on the anterior surface and
        #   the superior surface faces the top of the screen.
        #  Left Superior Anterior
        labels = 'lsa'
        transform = vtkTransform()
        transform.matrix = camera.GetModelTransformMatrix()
        transform.RotateY(90)
        transform.RotateZ(90)
        camera.model_transform_matrix = transform.matrix
        ren.ResetCamera()
    else:
        # The default.
        # Orient so that we look down on the posterior surface and
        #   the superior surface faces the top of the screen.
        # Right Superior Posterior
        labels = 'rsp'
        transform = vtkTransform()
        transform.matrix = camera.GetModelTransformMatrix()
        transform.RotateY(-90)
        transform.RotateZ(90)
        camera.model_transform_matrix = transform.matrix
        ren.ResetCamera()

    cow = vtkCameraOrientationWidget(parent_renderer=ren, enabled=True)
    if no_sliders:
        # Turn off if you do not want it.
        cow.EnabledOn()
    else:
        cow.EnabledOff()

    axes = make_cube_actor(labels)
    # Position upper left in the viewport: (0.0, 0.8, 0.2, 1.0).
    # Position lower left in the viewport: (0, 0, 0.2, 0.2).
    om = vtkOrientationMarkerWidget(orientation_marker=axes, viewport=(0, 0, 0.2, 0.2), interactor=iren, enabled=True,
                                    interactive=True)

    ren_win.Render()

    slider_toggle = SliderToggleCallback(sliders)
    iren.AddObserver('KeyPressEvent', slider_toggle)

    iren.Start()


def parse_json(fn_path):
    """
    Parse the JSON file selecting the components that we want.

    We also check that the file paths are valid.

    :param fn_path: The path the JSON file.
    :return: A dictionary of the parameters that we require.
    """
    with open(fn_path) as data_file:
        json_data = json.load(data_file)
    paths_ok = True
    parameters = dict()
    for k, v in json_data.items():
        if k == 'files':
            if 'root' in v:
                root = fn_path.parent / Path(v['root'])
                if not root.exists():
                    print(f'Bad path: {root}')
                    paths_ok = False
                else:
                    if 'vtk_files' not in v:
                        print('Expected vtk files.')
                        paths_ok = False
                        continue
                    for kk in v:
                        if kk == 'vtk_files':
                            if len(v[kk]) != 17:
                                print(f'Expected seventeen file names.')
                                paths_ok = False
                            # The stem of the file path becomes the key.
                            path_map = dict()
                            for p in list(map(lambda pp: root / pp, v[kk])):
                                path_map[p.stem] = p
                                if not p.is_file():
                                    paths_ok = False
                                    print(f'Not a file {p}')
                            if paths_ok:
                                parameters[kk] = path_map
            else:
                paths_ok = False
                print('Missing the key "root" and/or the key "files" for the files.')
        else:
            if k in ['tissues', 'figures']:
                for kk, vv in v.items():
                    parameters[kk] = vv
    return paths_ok, parameters


class SliceOrder:
    """
    These transformations permute image and other geometric data to maintain proper
     orientation regardless of the acquisition order. After applying these transforms with
    vtkTransformFilter, a view up of 0, -1, 0 will result in the body part
    facing the viewer.
    NOTE: some transformations have a -1 scale factor for one of the components.
          To ensure proper polygon orientation and normal direction, you must
          apply the vtkPolyDataNormals filter.

    Naming (the nomenclature is medical):
    si - superior to inferior (top to bottom)
    is - inferior to superior (bottom to top)
    ap - anterior to posterior (front to back)
    pa - posterior to anterior (back to front)
    lr - left to right
    rl - right to left
    """

    def __init__(self):
        self.si_mat = vtkMatrix4x4()
        self.si_mat.Zero()
        self.si_mat.SetElement(0, 0, 1)
        self.si_mat.SetElement(1, 2, 1)
        self.si_mat.SetElement(2, 1, -1)
        self.si_mat.SetElement(3, 3, 1)

        self.is_mat = vtkMatrix4x4()
        self.is_mat.Zero()
        self.is_mat.SetElement(0, 0, 1)
        self.is_mat.SetElement(1, 2, -1)
        self.is_mat.SetElement(2, 1, -1)
        self.is_mat.SetElement(3, 3, 1)

        self.lr_mat = vtkMatrix4x4()
        self.lr_mat.Zero()
        self.lr_mat.SetElement(0, 2, -1)
        self.lr_mat.SetElement(1, 1, -1)
        self.lr_mat.SetElement(2, 0, 1)
        self.lr_mat.SetElement(3, 3, 1)

        self.rl_mat = vtkMatrix4x4()
        self.rl_mat.Zero()
        self.rl_mat.SetElement(0, 2, 1)
        self.rl_mat.SetElement(1, 1, -1)
        self.rl_mat.SetElement(2, 0, 1)
        self.rl_mat.SetElement(3, 3, 1)

        """
        The previous transforms assume radiological views of the slices
         (viewed from the feet).
        Other modalities such as physical sectioning may view from the head.
        The following transforms modify the original with a 180° rotation about y
        """

        self.hf_mat = vtkMatrix4x4()
        self.hf_mat.Zero()
        self.hf_mat.SetElement(0, 0, -1)
        self.hf_mat.SetElement(1, 1, 1)
        self.hf_mat.SetElement(2, 2, -1)
        self.hf_mat.SetElement(3, 3, 1)

        self.transform = dict()

        si_trans = vtkTransform()
        si_trans.SetMatrix(self.si_mat)
        self.transform['si'] = si_trans

        is_trans = vtkTransform()
        is_trans.SetMatrix(self.is_mat)
        self.transform['is'] = is_trans

        ap_trans = vtkTransform()
        ap_trans.Scale(1, -1, 1)
        self.transform['ap'] = ap_trans

        pa_trans = vtkTransform()
        pa_trans.Scale(1, -1, -1)
        self.transform['pa'] = pa_trans

        lr_trans = vtkTransform()
        lr_trans.SetMatrix(self.lr_mat)
        self.transform['lr'] = lr_trans

        rl_trans = vtkTransform()
        rl_trans.SetMatrix(self.rl_mat)
        self.transform['rl'] = rl_trans

        hf_trans = vtkTransform()
        hf_trans.SetMatrix(self.hf_mat)
        self.transform['hf'] = hf_trans

        hf_si_trans = vtkTransform()
        hf_si_trans.SetMatrix(self.hf_mat)
        hf_si_trans.Concatenate(self.si_mat)
        self.transform['hfsi'] = hf_si_trans

        hf_is_trans = vtkTransform()
        hf_is_trans.SetMatrix(self.hf_mat)
        hf_is_trans.Concatenate(self.is_mat)
        self.transform['hfis'] = hf_is_trans

        hf_ap_trans = vtkTransform()
        hf_ap_trans.SetMatrix(self.hf_mat)
        hf_ap_trans.Scale(1, -1, 1)
        self.transform['hfap'] = hf_ap_trans

        hf_pa_trans = vtkTransform()
        hf_pa_trans.SetMatrix(self.hf_mat)
        hf_pa_trans.Scale(1, -1, -1)
        self.transform['hfpa'] = hf_pa_trans

        hf_lr_trans = vtkTransform()
        hf_lr_trans.SetMatrix(self.hf_mat)
        hf_lr_trans.Concatenate(self.lr_mat)
        self.transform['hflr'] = hf_lr_trans

        hf_rl_trans = vtkTransform()
        hf_rl_trans.SetMatrix(self.hf_mat)
        hf_rl_trans.Concatenate(self.rl_mat)
        self.transform['hfrl'] = hf_rl_trans

        # Identity
        self.transform['I'] = vtkTransform()

        # Zero
        z_trans = vtkTransform()
        z_trans.Scale(0, 0, 0)
        self.transform['Z'] = z_trans

    def print_transform(self, order):
        """
        Print the homogenous matrix corresponding to the slice order.
        :param order: The slice order.
        :return:
        """
        print(order)
        m = self.transform[order].GetMatrix()
        for i in range(0, 4):
            row = list()
            for j in range(0, 4):
                row.append(f'{m.GetElement(i, j):6.2g}')
            print(' '.join(row))

    def print_all_transforms(self):
        """
        Print all the homogenous matrices corresponding to the slice orders.
        :return:
        """
        for k in self.transform.keys():
            self.print_transform(k)

    def get(self, order):
        """
        Returns the vtkTransform corresponding to the slice order.

        :param order: The slice order.
        :return: The vtkTransform to use.
        """
        if order in self.transform.keys():
            return self.transform[order]
        else:
            s = 'No such transform "{:s}" exists.'.format(order)
            raise Exception(s)


def create_tissue_lut(indices, colors):
    """
    Create the lookup table for the frog tissues.

    Each table value corresponds the color of one of the frog tissues.

    :param indices: The tissue name and index.
    :param colors: The tissue name and color.
    :return: The lookup table.
    """
    lut = vtkLookupTable(number_of_colors=len(colors), table_range=(0, len(colors) - 1))
    lut.Build()

    nc = vtkNamedColors()

    for k in indices.keys():
        lut.SetTableValue(indices[k], nc.GetColor4d(colors[k]))

    return lut


class SliderProperties:
    dimensions = {
        'tube_width': 0.004,
        'slider_length': 0.015, 'slider_width': 0.008,
        'end_cap_length': 0.008, 'end_cap_width': 0.02,
        'title_height': 0.02, 'label_height': 0.020,
    }
    colors = {
        'title_color': 'Black', 'label_color': 'Black', 'slider_color': 'BurlyWood',
        'selected_color': 'Lime', 'bar_color': 'Black', 'bar_ends_color': 'Indigo',
        'value_color': 'DarkSlateGray'
    }
    range = {'minimum_value': 0.0, 'maximum_value': 1.0, 'value': 1.0}
    title_text = '',
    position = {'point1': (0.2, 0.1), 'point2': (0.18, 0.1)}


def make_slider_widget(slider_properties, lut, idx, interactor):
    """
    Make a slider widget.
    :param slider_properties: range, title name, dimensions, colors, and position.
    :param lut: The color lookup table.
    :param idx: The tissue index.
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
    if idx in range(0, 16):
        slider_rep.title_property.color = lut.GetTableValue(idx)[:3]
        slider_rep.title_property.shadow = False
    else:
        slider_rep.title_property.color = colors.GetColor3d(slider_properties.colors['title_color'])

    # slider_rep.title_property.color = colors.GetColor3d(slider_properties.colors['title_color'])
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


class SliderCallback:
    def __init__(self, actor_property):
        self.actor_property = actor_property

    def __call__(self, caller, ev):
        slider_widget = caller
        value = slider_widget.representation.value
        self.actor_property.opacity = value


class SliderToggleCallback:
    def __init__(self, sliders):
        self.sliders = sliders

    def __call__(self, caller, ev):
        if caller.key_code == 'n':
            for k, v in self.sliders.items():
                if v.enabled:
                    v.Off()
                else:
                    v.On()


def make_axes_actor(scale, total_length, xyz_labels):
    """
    :param scale: Sets the scale and direction of the axes.
    :param total_length: The total length of each axis.
    :param xyz_labels: Labels for the axes.
    :return: The axes actor.
    """
    colors = vtkNamedColors()

    axes = vtkAxesActor(shaft_type=vtkAxesActor.CYLINDER_SHAFT, tip_type=vtkAxesActor.CONE_TIP,
                        x_axis_label_text=xyz_labels[0], y_axis_label_text=xyz_labels[1],
                        z_axis_label_text=xyz_labels[2],
                        scale=scale,
                        total_length=total_length)

    axes.SetCylinderRadius(0.5 * axes.GetCylinderRadius())
    axes.SetConeRadius(1.025 * axes.GetConeRadius())
    axes.SetSphereRadius(1.5 * axes.GetSphereRadius())

    # Set the font properties.
    tprop = axes.x_axis_caption_actor2d.caption_text_property
    tprop.italic = True
    tprop.shadow = True
    tprop.SetFontFamilyToTimes()

    # Use the same text properties on the other two axes.
    axes.y_axis_caption_actor2d.caption_text_property.ShallowCopy(tprop)
    axes.z_axis_caption_actor2d.caption_text_property.ShallowCopy(tprop)

    # Now color the axes.
    axes.x_axis_tip_property.color = colors.GetColor3d('Red')
    axes.x_axis_shaft_property.color = colors.GetColor3d('Red')
    axes.y_axis_tip_property.color = colors.GetColor3d('LimeGreen')
    axes.y_axis_shaft_property.color = colors.GetColor3d('LimeGreen')
    axes.z_axis_tip_property.color = colors.GetColor3d('Blue')
    axes.z_axis_shaft_property.color = colors.GetColor3d('Blue')

    # Now color the labels.
    axes.x_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('FireBrick')
    axes.y_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('DarkGreen')
    axes.z_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('DarkBlue')

    return axes


def make_annotated_cube_actor(labels, rotations, scale, opacity=1):
    """
    :param labels: The labels for the cube faces.
    :param rotations: A tuple for x, y, z text rotations.
    :param scale: Scaling for the text on the faces.
    :param opacity: Opacity of the cube.
    :return: The annotated cube actor.
    """
    colors = vtkNamedColors()

    # A cube with labeled faces.
    cube = vtkAnnotatedCubeActor(face_text_scale=scale,
                                 x_plus_face_text=labels[0], x_minus_face_text=labels[1],
                                 y_plus_face_text=labels[2], y_minus_face_text=labels[3],
                                 z_plus_face_text=labels[4], z_minus_face_text=labels[5],
                                 )

    cube.cube_property.color = colors.GetColor3d('Gainsboro')

    cube.text_edges_property.color = colors.GetColor3d('LightSlateGray')
    cube.text_edges_property.line_width = 1

    # Change the vector text colors.
    cube.x_plus_face_property.color = colors.GetColor3d('Tomato')
    cube.x_minus_face_property.color = colors.GetColor3d('Tomato')
    cube.y_plus_face_property.color = colors.GetColor3d('SeaGreen')
    cube.y_minus_face_property.color = colors.GetColor3d('SeaGreen')
    cube.z_plus_face_property.color = colors.GetColor3d('DeepSkyBlue')
    cube.z_minus_face_property.color = colors.GetColor3d('DeepSkyBlue')

    cube.x_face_text_rotation = rotations[0]
    cube.y_face_text_rotation = rotations[1]
    cube.z_face_text_rotation = rotations[2]

    # Set this to 0 if you are adding a cube whose
    # faces are individually colored.
    cube.cube_property.opacity = opacity

    return cube


def make_cube_actor(label_selector):
    """
    :param label_selector: The selector used to define labels for the axes and cube.
    :return: The combined axes and annotated cube prop.
    """
    if label_selector == 'sal':
        # xyz_labels = ('S', 'A', 'L')
        xyz_labels = ('+X', '+Y', '+Z')
        cube_labels = ('S', 'I', 'A', 'P', 'L', 'R')
        label_rotations = (-90, 180, 90)
        scale = (1.5, 1.5, 1.5)
    elif label_selector == 'rsp':
        # xyz_labels = ('R', 'S', 'P')
        xyz_labels = ('+X', '+Y', '+Z')
        cube_labels = ('R', 'L', 'S', 'I', 'P', 'A')
        label_rotations = (-90, -180, 90)
        scale = (1.5, 1.5, 1.5)
    elif label_selector == 'lsa':
        # xyz_labels = ('L', 'S', 'A')
        xyz_labels = ('+X', '+Y', '+Z')
        cube_labels = ('L', 'R', 'S', 'I', 'A', 'P')
        label_rotations = (-90, 180, 90)
        scale = (1.5, 1.5, 1.5)
    else:
        xyz_labels = ('+X', '+Y', '+Z')
        cube_labels = ('+X', '-X', '+Y', '-Y', '+Z', '-Z')
        label_rotations = (90, 180, -90)
        scale = (1.5, 1.5, 1.5)

    # We are combining a vtkAxesActor and a vtkAnnotatedCubeActor
    # into a vtkPropAssembly
    face_text_scale = 0.5
    cube = make_annotated_cube_actor(cube_labels, label_rotations, face_text_scale, opacity=1)
    total_length = (0.7, 0.7, 0.7)
    axes = make_axes_actor(scale, total_length, xyz_labels)

    # Combine orientation markers into one with an assembly.
    assembly = vtkPropAssembly()
    assembly.AddPart(axes)
    assembly.AddPart(cube)
    return assembly


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
    import sys

    data_folder, view, omit_sliders, selected_tissues = get_program_parameters(sys.argv)
    main(data_folder, view, omit_sliders, selected_tissues)
