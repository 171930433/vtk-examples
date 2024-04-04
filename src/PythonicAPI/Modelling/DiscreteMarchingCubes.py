#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkLookupTable,
    vtkMinimalStandardRandomSequence
)
from vtkmodules.vtkCommonDataModel import (
    vtkImageData,
    vtkSphere
)
from vtkmodules.vtkFiltersGeneral import (
    vtkDiscreteFlyingEdges3D,
    vtkDiscreteMarchingCubes
)
from vtkmodules.vtkImagingCore import vtkImageThreshold
from vtkmodules.vtkImagingHybrid import vtkSampleFunction
from vtkmodules.vtkImagingMath import vtkImageMathematics
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Create surfaces from labeled data.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-m', '--marching_cubes', action='store_false',
                        help='Use Marching Cubes instead of Flying Edges.')
    args = parser.parse_args()
    return args.marching_cubes


def main():
    use_flying_edges = get_program_parameters()

    colors = vtkNamedColors()

    # Create the RenderWindow, Renderer, Interactor
    ren = vtkRenderer(background=colors.GetColor3d('Burlywood'))
    ren_win = vtkRenderWindow(window_name='DiscreteMarchingCubes')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    n = 20
    radius = 8
    blob = make_blob(n, radius)

    if use_flying_edges:
        try:
            discrete = vtkDiscreteFlyingEdges3D()
        except AttributeError:
            discrete = vtkDiscreteMarchingCubes()
    else:
        discrete = vtkDiscreteMarchingCubes()
    discrete.GenerateValues(n, 1, n)

    lut = make_colors(n)

    mapper = vtkPolyDataMapper(lookup_table=lut, scalar_range=(0, lut.number_of_colors))
    blob >> discrete >> mapper
    actor = vtkActor(mapper=mapper)

    ren.AddActor(actor)

    ren_win.Render()

    iren.Start()


def make_blob(n, radius):
    blob_image = vtkImageData()

    max_r = 50 - 2.0 * radius
    random_sequence = vtkMinimalStandardRandomSequence(seed=5071)
    for i in range(0, n):

        x = random_sequence.GetRangeValue(-max_r, max_r)
        random_sequence.Next()
        y = random_sequence.GetRangeValue(-max_r, max_r)
        random_sequence.Next()
        z = random_sequence.GetRangeValue(-max_r, max_r)
        random_sequence.Next()

        sphere = vtkSphere(radius=radius, center=(int(x), int(y), int(z)))

        sampler = vtkSampleFunction(implicit_function=sphere, output_scalar_type=ImageCastOutputScalarType.VTK_FLOAT,
                                    sample_dimensions=(100, 100, 100), model_bounds=(-50, 50, -50, 50, -50, 50))

        thres = vtkImageThreshold(replace_in=True, replace_out=True, in_value=i + 1, out_value=0)
        thres.ThresholdByLower(radius * radius)
        (sampler >> thres).update()
        if i == 0:
            blob_image.DeepCopy(thres.output)

        max_value = vtkImageMathematics(operation=ImageMathematicsOperation.VTK_MAX)
        ((blob_image, thres) >> max_value).update()

        blob_image.DeepCopy(max_value.output)

    return blob_image


def make_colors(n):
    """
    Generate some random colors
    :param n: The number of colors.
    :return: The lookup table.
    """

    lut = vtkLookupTable(number_of_colors=n, table_range=(0, n - 1), scale=LookupTableScale.VTK_SCALE_LINEAR)
    lut.Build()
    lut.SetTableValue(0, 0.0, 0.0, 0.0, 1.0)

    random_sequence = vtkMinimalStandardRandomSequence()
    random_sequence.SetSeed(5071)
    for i in range(1, n):
        r = random_sequence.GetRangeValue(0.4, 1)
        random_sequence.Next()
        g = random_sequence.GetRangeValue(0.4, 1)
        random_sequence.Next()
        b = random_sequence.GetRangeValue(0.4, 1)
        random_sequence.Next()
        lut.SetTableValue(i, r, g, b, 1.0)

    return lut


@dataclass(frozen=True)
class ImageCastOutputScalarType:
    VTK_CHAR: int = 2
    VTK_UNSIGNED_CHAR: int = 3
    VTK_SHORT: int = 4
    VTK_UNSIGNED_SHORT: int = 5
    VTK_INT: int = 6
    VTK_UNSIGNED_INT: int = 7
    VTK_LONG: int = 8
    VTK_UNSIGNED_LONG: int = 9
    VTK_FLOAT: int = 10
    VTK_DOUBLE: int = 11


@dataclass(frozen=True)
class ImageMathematicsOperation:
    VTK_ADD: int = 0
    VTK_SUBTRACT: int = 1
    VTK_MULTIPLY: int = 2
    VTK_DIVIDE: int = 3
    VTK_INVERT: int = 4
    VTK_SIN: int = 5
    VTK_COS: int = 6
    VTK_EXP: int = 7
    VTK_LOG: int = 8
    VTK_ABS: int = 9
    VTK_SQR: int = 10
    VTK_SQRT: int = 11
    VTK_MIN: int = 12
    VTK_MAX: int = 13
    VTK_ATAN: int = 14
    VTK_ATAN2: int = 15
    VTK_MULTIPLYBYK: int = 16
    VTK_ADDC: int = 17
    VTK_CONJUGATE: int = 18
    VTK_COMPLEX_MULTIPLY: int = 19
    VTK_REPLACECBYK: int = 20


@dataclass(frozen=True)
class LookupTableScale:
    VTK_SCALE_LINEAR: int = 0
    VTK_SCALE_LOG10: int = 1


if __name__ == '__main__':
    main()
