#!/usr/bin/env python3

import sys
from dataclasses import dataclass
from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from lxml import etree
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkElevationFilter
from vtkmodules.vtkFiltersSources import vtkConeSource, vtkSphereSource
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkRenderingCore import (
    vtkDiscretizableColorTransferFunction,
)


def get_program_parameters(argv):
    import argparse
    description = 'Take an XML description of a colormap and convert it to a VTK colormap.'
    epilogue = '''
    A color transfer function in C++, Python or for the new Pythonic API can be optionally generated.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('file_name', help='The path to the XML file e.g Fast.xml.')
    parser.add_argument('-d', action='store_true', dest='discretize', help='Discretize the colormap.')
    parser.add_argument('-s', dest='size', default=None, type=int,
                        help='Specify the size of the colormap.')
    parser.add_argument('-g', dest='generate_function', default=None,
                        help='Generate code for the color transfer function,'
                             ' specify the desired language one of: Cxx, Python, PythonicAPI.')

    args = parser.parse_args()
    return args.file_name, args.discretize, args.size, args.generate_function


def main(file_name, discretize, table_size, generate_function):
    use_sphere = False

    if file_name:
        fn_path = Path(file_name)
        if not fn_path.suffix:
            fn_path = fn_path.with_suffix(".xml")
        if not fn_path.is_file():
            print('Unable to find: ', fn_path)
            return
    else:
        print('Please enter a path to the XML file.')
        return
    parameters = parse_xml(fn_path)

    if generate_function is not None:
        generate_function = generate_function.lower()
        available_languages = {k.lower(): k for k in ['Cxx', 'Python', 'PythonicAPI']}
        available_languages.update({'cpp': 'Cxx', 'c++': 'Cxx', 'py': 'Python'})
        if generate_function not in available_languages:
            print(f'The language: {generate_function} is not available.')
            tmp = ', '.join(sorted([lang for lang in set(available_languages.values())]))
            print(f'Choose one of these: {tmp}.')
            return
        else:
            language = available_languages[generate_function]
    else:
        language = None

    # There is just one entry in the parameters dict.
    colormap_name = list(parameters.keys())[0]
    ctf = generate_ctf(parameters[colormap_name], discretize, table_size)

    if language is not None and language in ['Cxx', 'Python', 'PythonicAPI']:
        if language == 'Python':
            generate_ctf_python(parameters[colormap_name], discretize, table_size)
        if language == 'PythonicAPI':
            generate_ctf_pythonic_api(parameters[colormap_name], discretize, table_size)
        else:
            generate_ctf_cpp(parameters[colormap_name], discretize, table_size)

    colors = vtkNamedColors()
    colors.SetColor('ParaViewBkg', 82, 87, 110, 255)

    ren = vtkRenderer(background=colors.GetColor3d('ParaViewBkg'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='ColorMapToLUT_XML')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    style = vtkInteractorStyleTrackballCamera()
    iren.interactor_style = style

    if use_sphere:
        sphere = vtkSphereSource(theta_resolution=64, phi_resolution=32)
        bounds = sphere.update().output.GetBounds()
    else:
        cone = vtkConeSource(resolution=6, direction=(0, 1, 0), height=1)
        bounds = cone.update().output.GetBounds()

    elevation_filter = vtkElevationFilter(low_point=(0, bounds[2], 0), high_point=(0, bounds[3], 0))

    ctf = generate_ctf(parameters[colormap_name], discretize, table_size)

    mapper = vtkPolyDataMapper(lookup_table=ctf, color_mode=Mapper.ColorMode.VTK_COLOR_MODE_MAP_SCALARS)
    if use_sphere:
        sphere >> elevation_filter >> mapper
    else:
        cone >> elevation_filter >> mapper
    mapper.interpolate_scalars_before_mapping = True

    actor = vtkActor(mapper=mapper)

    ren.AddActor(actor)

    ren_win.Render()
    iren.Start()


def parse_xml(fn_path):
    """
    Parse the XML file of a colormap.

    Check out: https://sciviscolor.org/colormaps/ for some good XML files.
    :param fn_path: The path to the XML file.
    :return: The parameters for the color map.
    """
    with open(fn_path) as data_file:
        xml_doc = etree.parse(data_file)

    def extract(d):
        """
        Pull out the data we need.

        :param d: The parsed XML data.
        :return: The extracted data.
        """
        color_map_details = dict()
        data_values = list()
        color_values = list()
        opacity_values = list()
        nan = None
        above = None
        below = None
        if d is not None:
            color_map_details = dict(d.attrib)
            if 'space' in color_map_details:
                # Some XML files use space instead of interpolation space.
                if color_map_details['space'].lower() not in ['rgb', 'hsv']:
                    color_map_details['interpolationspace'] = color_map_details['space']
                    # Assume RGB
                    color_map_details['space'] = 'RGB'
        for pt in d.findall('.//Point'):
            # "o" is opacity it (along with "cms" and "isMoT") are ignored.
            # "x" is the scalar value associated with the color (specified by "r", "g", and "b").
            data_values.append(pt.attrib['x'])
            color_values.append((pt.attrib['r'], pt.attrib['g'], pt.attrib['b']))
            if pt.attrib['o']:
                opacity_values.append(pt.attrib['o'])
        val = d.find('.//NaN')
        if val is not None:
            nan = (val.attrib['r'], val.attrib['g'], val.attrib['b'])
        val = d.find('.//Above')
        if val is not None:
            above = (val.attrib['r'], val.attrib['g'], val.attrib['b'])
        val = d.find('.//Below')
        if val is not None:
            below = (val.attrib['r'], val.attrib['g'], val.attrib['b'])
        return {'color_map_details': color_map_details, 'data_values': data_values,
                'color_values': color_values, 'opacity_values': opacity_values, 'NaN': nan, 'Above': above,
                'Below': below}

    s = xml_doc.getroot().find('ColorMap')
    if s is None:
        sys.exit('The attribute "ColorMap" is not found.')
    res = dict()
    parameters = extract(s)
    parameters['path'] = fn_path.name
    cm_name = parameters['color_map_details']['name']
    # Do some checks.
    if cm_name is not None:
        if len(parameters['data_values']) != len(parameters['color_values']):
            sys.exit(f'{parameters["path"]}: The data values length must be the same as colors.')
        if len(parameters['opacity_values']) > 0:
            if len(parameters['opacity_values']) != len(parameters['color_values']):
                sys.exit(f'{parameters["path"]}: The opacity values length must be the same as colors.')
        res[cm_name] = parameters
    return res


def generate_ctf(parameters, discretize, table_size=None):
    """
    Generate the discretizable color transfer function
    :param parameters: The parameters.
    :param discretize: True if the values are to be mapped after discretization.
    :param table_size: The table size.
    :return: The discretizable color transfer function.
    """

    ctf = vtkDiscretizableColorTransferFunction()

    interp_space = parameters['color_map_details'].get('interpolationspace', None)
    if interp_space:
        interp_space = interp_space.lower()
        if interp_space == 'hsv':
            ctf.SetColorSpaceToHSV()
        elif interp_space == 'lab':
            ctf.SetColorSpaceToLab()
        elif interp_space == 'cielab':
            ctf.SetColorSpaceToLab()
        elif interp_space == 'ciede2000':
            ctf.SetColorSpaceToLabCIEDE2000()
        elif interp_space == 'diverging':
            ctf.SetColorSpaceToDiverging()
        elif interp_space == 'step':
            ctf.SetColorSpaceToStep()
        else:
            ctf.SetColorSpaceToRGB()
    else:
        ctf.SetColorSpaceToRGB()

    scale = parameters['color_map_details'].get('interpolationtype', None)
    if scale:
        scale = scale.lower()
        if scale == 'log10':
            ctf.SetScaleToLog10()
        else:
            ctf.SetScaleToLinear()
    else:
        ctf.SetScaleToLinear()

    if parameters['NaN'] is not None:
        color = list(map(float, parameters['NaN']))
        ctf.SetNanColor(*color)

    if parameters['Above'] is not None:
        color = list(map(float, parameters['Above']))
        ctf.SetAboveRangeColor(*color)
        ctf.UseAboveRangeColorOn()

    if parameters['Below'] is not None:
        color = list(map(float, parameters['Below']))
        ctf.SetBelowRangeColor(*color)
        ctf.UseBelowRangeColorOn()

    space = parameters['color_map_details'].get('space', None)
    if space:
        space = space.lower()
        for i in range(0, len(parameters['data_values'])):
            color = list(map(float, parameters['color_values'][i]))
            idx = float(parameters['data_values'][i])
            if space == 'hsv':
                ctf.AddHSVPoint(idx, *color)
            else:
                ctf.AddRGBPoint(idx, *color)

    if table_size is not None:
        ctf.SetNumberOfValues(table_size)
    else:
        ctf.SetNumberOfValues(len(parameters["data_values"]))

    if discretize:
        ctf.DiscretizeOn()
    else:
        ctf.DiscretizeOff()

    return ctf


def generate_ctf_python(parameters, discretize, table_size=None):
    """
    Generate a function for the ctf.

    :param parameters: The parameters.
    :param discretize: True if the values are to be mapped after discretization.
    :param table_size: The table size.
    :return: The discretizable color transfer function.
    """
    indent = ' ' * 4

    comment = f'{indent}#'
    if 'name' in parameters['color_map_details']:
        comment += f' name: {parameters["color_map_details"]["name"]},'
    if 'creator' in parameters['color_map_details']:
        comment += f' creator: {parameters["color_map_details"]["creator"]}'
    if 'interpolationspace' in parameters['color_map_details']:
        comment += f'\n{indent}# interpolationspace: {parameters["color_map_details"]["interpolationspace"]},'
    if 'interpolationtype' in parameters['color_map_details']:
        comment += f' interpolationtype: {parameters["color_map_details"]["interpolationtype"]},'
    if 'space' in parameters['color_map_details']:
        comment += f' space: {parameters["color_map_details"]["space"]}'
    comment += f'\n{indent}# file name: {parameters["path"]}\n'

    s = ['', f'def get_ctf():', comment, f'{indent}ctf = vtkDiscretizableColorTransferFunction()', '']

    interp_space = parameters['color_map_details'].get('interpolationspace', None)
    if interp_space:
        interp_space = interp_space.lower()
        if interp_space == 'hsv':
            s.append(f'{indent}ctf.SetColorSpaceToHSV()')
        elif interp_space == 'lab':
            s.append(f'{indent}ctf.SetColorSpaceToLab()')
        elif interp_space == 'cielab':
            s.append(f'{indent}ctf.SetColorSpaceToLab()')
        elif interp_space == 'ciede2000':
            s.append(f'{indent}ctf.SetColorSpaceToLabCIEDE2000()')
        elif interp_space == 'diverging':
            s.append(f'{indent}ctf.SetColorSpaceToDiverging()')
        elif interp_space == 'step':
            s.append(f'{indent}ctf.SetColorSpaceToStep()')
        else:
            s.append(f'{indent}ctf.SetColorSpaceToRGB()')
    else:
        s.append(f'{indent}ctf.SetColorSpaceToRGB()')

    scale = parameters['color_map_details'].get('interpolationtype', None)
    if scale:
        scale = scale.lower()
        if scale == 'log10':
            s.append(f'{indent}ctf.SetScaleToLog10()')
        else:
            s.append(f'{indent}ctf.SetScaleToLinear()')
    else:
        s.append(f'{indent}ctf.SetScaleToLinear()')
    s.append('')

    if parameters['NaN'] is not None:
        color = ', '.join(parameters['NaN'])
        s.append(f'{indent}ctf.SetNanColor({color})')

    if parameters['Above'] is not None:
        color = ', '.join(parameters['Above'])
        s.append(f'{indent}ctf.SetAboveRangeColor({color})')
        s.append(f'{indent}ctf.UseAboveRangeColorOn()')

    if parameters['Below'] is not None:
        color = ', '.join(parameters['Below'])
        s.append(f'{indent}ctf.SetBelowRangeColor({color})')
        s.append(f'{indent}ctf.UseBelowRangeColorOn()')
    s.append('')

    space = parameters['color_map_details'].get('space', None)
    if space:
        space = space.lower()
        for i in range(0, len(parameters['data_values'])):
            color = ', '.join(parameters['color_values'][i])
            idx = parameters['data_values'][i]
            if space == 'hsv':
                s.append(f'{indent}ctf.AddHSVPoint({idx}, {color})')
            else:
                s.append(f'{indent}ctf.AddRGBPoint({idx}, {color})')
        s.append('')

    if table_size is not None:
        s.append(f'{indent}ctf.SetNumberOfValues({table_size})')
    else:
        s.append(f'{indent}ctf.SetNumberOfValues({len(parameters["data_values"])})')

    if discretize:
        s.append(f'{indent}ctf.DiscretizeOn()')
    else:
        s.append(f'{indent}ctf.DiscretizeOff()')
    s.append('')

    s.append(f'{indent}return ctf')
    s.append('')

    print('\n'.join(s))


def generate_ctf_pythonic_api(parameters, discretize, table_size=None):
    """
    Generate a function for the ctf using the new Pythonic API.

    :param parameters: The parameters.
    :param discretize: True if the values are to be mapped after discretization.
    :param table_size: The table size.
    :return: The discretizable color transfer function.
    """
    indent = ' ' * 4

    comment = f'{indent}#'
    if 'name' in parameters['color_map_details']:
        comment += f' name: {parameters["color_map_details"]["name"]},'
    if 'creator' in parameters['color_map_details']:
        comment += f' creator: {parameters["color_map_details"]["creator"]}'
    if 'interpolationspace' in parameters['color_map_details']:
        comment += f'\n{indent}# interpolationspace: {parameters["color_map_details"]["interpolationspace"]},'
    if 'interpolationtype' in parameters['color_map_details']:
        comment += f' interpolationtype: {parameters["color_map_details"]["interpolationtype"]},'
    if 'space' in parameters['color_map_details']:
        comment += f' space: {parameters["color_map_details"]["space"]}'
    comment += f'\n{indent}# file name: {parameters["path"]}\n'

    s = ['', f'def get_ctf():', comment]
    ctf_fn = f'{indent}ctf = vtkDiscretizableColorTransferFunction('
    indent1 = ' ' * len(ctf_fn)
    interp_space = parameters['color_map_details'].get('interpolationspace', None)
    color_space = ctf_fn + 'color_space=ColorTransferFunction.ColorSpace.'
    scale = 'scale=ColorTransferFunction.Scale.'
    css = list()
    if interp_space:
        interp_space = interp_space.lower()
        if interp_space == 'hsv':
            s.append(f'{color_space}VTK_CTF_HSV')
        elif interp_space == 'lab':
            s.append(f'{color_space}VTK_CTF_LAB')
        elif interp_space == 'cielab':
            s.append(f'{color_space}VTK_CTF_LAB')
        elif interp_space == 'ciede2000':
            s.append(f'{color_space}VTK_CTF_LAB_CIEDE2000')
        elif interp_space == 'diverging':
            s.append(f'{color_space}VTK_CTF_DIVERGING')
        elif interp_space == 'step':
            s.append(f'{color_space}VTK_CTF_STEP')
        else:
            s.append(f'{color_space}VTK_CTF_RGB')
    else:
        s.append(f'{color_space}VTK_CTF_RGB')
    s[-1] = s[-1] + ','
    interp = parameters['color_map_details'].get('interpolationtype', None)
    if interp:
        interp = interp.lower()
        if interp == 'log10':
            s.append(f'{indent1}{scale}VTK_CTF_LOG10')
        else:
            s.append(f'{indent1}{scale}VTK_CTF_LINEAR')
    else:
        s.append(f'{indent1}{scale}VTK_CTF_LINEAR')

    if parameters['NaN'] is not None:
        color = ', '.join(list(map(str, parameters['NaN'])))
        s[-1] = s[-1] + ','
        s.append(f'{indent1}nan_color=({color})')

    if parameters['Above'] is not None:
        color = ', '.join(list(map(str, parameters['Above'])))
        s[-1] = s[-1] + ','
        s.append(f'{indent1}above_range_color=({color}), ctf.use_above_range_color=True')

    if parameters['Below'] is not None:
        color = ', '.join(list(map(str, parameters['Below'])))
        s[-1] = s[-1] + ','
        s.append(f'{indent1}below_range_color=({color}), ctf.use_below_range_color=True')

    ctf_sz = len(parameters["data_values"])
    td = list()
    if table_size is not None:
        td.append(f'{indent1}number_of_values={max(table_size, ctf_sz)}')
    else:
        td.append(f'{indent1}number_of_values={ctf_sz}')

    if discretize:
        td.append(f'discretize=True)')
    else:
        td.append(f'discretize=False)')
    if td:
        s[-1] = s[-1] + ','
        s.append(f'{", ".join(td)}')
    s.append('')

    space = parameters['color_map_details']['space'].lower()
    for i in range(0, ctf_sz):
        rgb = ', '.join(list(map(str, parameters['color_values'][i])))
        idx = parameters['data_values'][i]
        if space == 'hsv':
            s.append(f'{indent}ctf.AddHSVPoint({idx}, {rgb})')
        else:
            s.append(f'{indent}ctf.AddRGBPoint({idx}, {rgb})')
    s.append('')

    s.append(f'{indent}return ctf')
    s.append('')

    print('\n'.join(s))


def generate_ctf_cpp(parameters, discretize, table_size=None):
    """
    Generate a function for the ctf.

    :param parameters: The parameters.
    :param discretize: True if the values are to be mapped after discretization.
    :param table_size: The table size.
    :return: The discretizable color transfer function.
    """
    indent = ' ' * 2

    comment = f'{indent}//'
    if 'name' in parameters['color_map_details']:
        comment += f' name: {parameters["color_map_details"]["name"]},'
    if 'creator' in parameters['color_map_details']:
        comment += f' creator: {parameters["color_map_details"]["creator"]}'
    if 'interpolationspace' in parameters['color_map_details']:
        comment += f'\n{indent}// interpolationspace: {parameters["color_map_details"]["interpolationspace"]},'
    if 'interpolationtype' in parameters['color_map_details']:
        comment += f' interpolationtype: {parameters["color_map_details"]["interpolationtype"]},'
    if 'space' in parameters['color_map_details']:
        comment += f' space: {parameters["color_map_details"]["space"]}'
    comment += f'\n{indent}// file name: {parameters["path"]}\n'

    s = ['', f'vtkNew<vtkDiscretizableColorTransferFunction> GetCTF()', '{', comment,
         f'{indent}vtkNew<vtkDiscretizableColorTransferFunction> ctf;', '']

    interp_space = parameters['color_map_details'].get('interpolationspace', None)
    if interp_space:
        interp_space = interp_space.lower()
        if interp_space == 'hsv':
            s.append(f'{indent}ctf->SetColorSpaceToHSV();')
        elif interp_space == 'lab':
            s.append(f'{indent}ctf->SetColorSpaceToLab();')
        elif interp_space == 'cielab':
            s.append(f'{indent}ctf->SetColorSpaceToLab();')
        elif interp_space == 'ciede2000':
            s.append(f'{indent}ctf->SetColorSpaceToLabCIEDE2000();')
        elif interp_space == 'diverging':
            s.append(f'{indent}ctf->SetColorSpaceToDiverging();')
        elif interp_space == 'step':
            s.append(f'{indent}ctf->SetColorSpaceToStep();')
        else:
            s.append(f'{indent}ctf->SetColorSpaceToRGB();')
    else:
        s.append(f'{indent}ctf->SetColorSpaceToRGB();')

    scale = parameters['color_map_details'].get('interpolationtype', None)
    if scale:
        scale = scale.lower()
        if scale == 'log10':
            s.append(f'{indent}ctf->SetScaleToLog10();')
        else:
            s.append(f'{indent}ctf->SetScaleToLinear();')
    else:
        s.append(f'{indent}ctf->SetScaleToLinear();')
    s.append('')

    if parameters['NaN'] is not None:
        color = ', '.join(parameters['NaN'])
        s.append(f'{indent}ctf->SetNanColor({color});')

    if parameters['Above'] is not None:
        color = ', '.join(parameters['Above'])
        s.append(f'{indent}ctf->SetAboveRangeColor({color});')
        s.append(f'{indent}ctf->UseAboveRangeColorOn();')

    if parameters['Below'] is not None:
        color = ', '.join(parameters['Below'])
        s.append(f'{indent}ctf->SetBelowRangeColor({color});')
        s.append(f'{indent}ctf->UseBelowRangeColorOn();')
    s.append('')

    space = parameters['color_map_details'].get('space', None)
    if space:
        space = space.lower()
        for i in range(0, len(parameters['data_values'])):
            color = ', '.join(parameters['color_values'][i])
            idx = parameters['data_values'][i]
            if space == 'hsv':
                s.append(f'{indent}ctf->AddHSVPoint({idx}, {color});')
            else:
                s.append(f'{indent}ctf->AddRGBPoint({idx}, {color});')
        s.append('')

    if table_size is not None:
        s.append(f'{indent}ctf->SetNumberOfValues({table_size});')
    else:
        s.append(f'{indent}ctf->SetNumberOfValues({len(parameters["data_values"])});')

    if discretize:
        s.append(f'{indent}ctf->DiscretizeOn();')
    else:
        s.append(f'{indent}ctf->DiscretizeOff();')
    s.append('')

    s.append(f'{indent}return ctf;')
    s.append('}')
    s.append('')

    print('\n'.join(s))


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
    file, discretise, size, generate = get_program_parameters(sys.argv)
    main(file, discretise, size, generate)
