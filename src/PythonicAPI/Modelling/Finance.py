#!/usr/bin/env python3

from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkFloatArray,
    vtkPoints
)
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid
from vtkmodules.vtkFiltersCore import (
    vtkContourFilter,
    vtkTubeFilter
)
from vtkmodules.vtkFiltersGeneral import vtkAxes
from vtkmodules.vtkImagingHybrid import vtkGaussianSplatter
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    colors.SetColor('PopColor', 230, 230, 230, 255)

    file_name = get_program_parameters()
    path = Path(file_name)
    if not path.is_file():
        print(f'Nonexistent file: {path}')
        return

    keys = ['NUMBER_POINTS', 'MONTHLY_PAYMENT', 'INTEREST_RATE', 'LOAN_AMOUNT', 'TIME_LATE']

    # Read in the data and make an unstructured data set.
    data_set = make_dataset(path, keys)

    # Construct the pipeline for the original population.
    pop_splatter = vtkGaussianSplatter(sample_dimensions=(100, 100, 100), radius=0.05, scalar_warping=False)

    pop_surface = vtkContourFilter()
    pop_surface.SetValue(0, 0.01)

    pop_mapper = vtkPolyDataMapper(scalar_visibility=False)
    data_set >> pop_splatter >> pop_surface >> pop_mapper

    pop_actor = vtkActor(mapper=pop_mapper)
    pop_actor.property.opacity = 0.3
    pop_actor.property.color = colors.GetColor3d('PopColor')

    # Construct the pipeline for the delinquent population.
    late_splatter = vtkGaussianSplatter(sample_dimensions=(50, 50, 50), radius=0.05, scale_factor=0.005)

    late_surface = vtkContourFilter()
    late_surface.SetValue(0, 0.01)

    late_mapper = vtkPolyDataMapper(scalar_visibility=False)
    data_set >> late_splatter >> late_surface >> late_mapper

    late_actor = vtkActor(mapper=late_mapper)
    late_actor.SetMapper(late_mapper)
    late_actor.property.color = colors.GetColor3d('Red')

    # Create axes.
    bounds = pop_splatter.update().output.bounds
    scale_factor = pop_splatter.output.length / 5
    axes = vtkAxes(origin=(bounds[0], bounds[2], bounds[4]), scale_factor=scale_factor)

    axes_tubes = vtkTubeFilter(radius=axes.scale_factor / 25, number_of_sides=6)

    axes_mapper = vtkPolyDataMapper()
    axes >> axes_tubes >> axes_mapper

    axes_actor = vtkActor(mapper=axes_mapper)

    # Graphics stuff.
    renderer = vtkRenderer(background=colors.GetColor3d('Wheat'))

    ren_win = vtkRenderWindow(size=(640, 480), window_name='Finance')
    ren_win.AddRenderer(renderer)

    interactor = vtkRenderWindowInteractor()
    interactor.render_window = ren_win

    # Set up the renderer.
    renderer.AddActor(late_actor)
    renderer.AddActor(axes_actor)
    renderer.AddActor(pop_actor)

    renderer.ResetCamera()
    renderer.active_camera.Dolly(1.3)
    renderer.ResetCameraClippingRange()

    # Interact with the data.
    ren_win.Render()
    interactor.Start()


def get_program_parameters():
    import argparse
    description = 'Visualization of multidimensional financial data.'
    epilogue = '''
    The gray/wireframe surface represents the total data population.
    The red surface represents data points delinquent on loan payment.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='financial.txt.')
    args = parser.parse_args()
    return args.filename


def normalise(maximum, minimum, x):
    return minimum + x / (maximum - minimum)


def read_file(path):
    """
    Read in the data set.
    :param path: The file.
    :return:
    """
    res = dict()

    content = path.read_text(encoding="utf-8")
    has_key = False
    for line in content.split('\n'):
        cl = ' '.join(line.split()).split()  # Clean the line.
        if cl:
            if len(cl) == 2 and cl[0] == 'NUMBER_POINTS':
                k = cl[0]
                v = [int(cl[1])]
                has_key = True
                continue
            if len(cl) == 1 and not has_key:
                has_key = True
                k = cl[0]
                v = list()
            else:
                v += map(float, cl)
        else:
            if has_key:
                # Normalise the data.
                minimum = min(v)
                maximum = max(v)
                # Emulate the bug in the C++ code.
                for i in v:
                    if i > minimum:
                        maximum = i
                if maximum != minimum:
                    res[k] = list(map(lambda x: minimum + x / (maximum - minimum), v))
                else:
                    res[k] = v
                has_key = False
    return res


def make_dataset(path, keys):
    res = read_file(path)
    if res:
        new_pts = vtkPoints()
        new_scalars = vtkFloatArray()
        xyz = list(zip(res[keys[1]], res[keys[2]], res[keys[3]]))
        for i in range(0, res[keys[0]][0]):
            new_pts.InsertPoint(i, xyz[i])
            new_scalars.InsertValue(i, res[keys[4]][i])

        dataset = vtkUnstructuredGrid(points=new_pts)
        dataset.GetPointData().SetScalars(new_scalars)
        return dataset


if __name__ == '__main__':
    main()
