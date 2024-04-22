#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkLookupTable
)
from vtkmodules.vtkFiltersCore import (
    vtkPolyDataNormals,
    vtkWindowedSincPolyDataFilter
)
from vtkmodules.vtkFiltersGeneral import (
    vtkDiscreteFlyingEdges3D,
    vtkDiscreteMarchingCubes
)
from vtkmodules.vtkIOImage import vtkMetaImageReader
from vtkmodules.vtkImagingCore import vtkExtractVOI
from vtkmodules.vtkRenderingCore import (
    vtkColorTransferFunction,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkRenderingLOD import vtkLODActor


def get_program_parameters():
    import argparse
    description = 'MeshLabelImageColor.'
    epilogue = '''
        Takes a label image in Meta format and meshes a single label of it.
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)
    parser.add_argument('filename', help='labels.mhd')
    parser.add_argument('label', nargs='?', const=1, type=int, default=31, help='The label to use e.g 31')
    parser.add_argument('-m', '--marching_cubes', action='store_false',
                        help='Use Marching Cubes instead of Flying Edges.')
    args = parser.parse_args()
    return args.filename, args.label, args.marching_cubes


def main():
    colors = vtkNamedColors()
    ifn, index, use_flying_edges = get_program_parameters()

    print('Doing label', index)

    # Prepare to read the file.
    reader_volume = vtkMetaImageReader(file_name=ifn)

    # Extract the region of interest.
    voi = vtkExtractVOI(voi=(0, 517, 0, 228, 0, 392), sample_rate=(1, 1, 1))

    # Prepare surface generation.
    # For label images.
    if use_flying_edges:
        contour = vtkDiscreteFlyingEdges3D(value=(0, index))
    else:
        contour = vtkDiscreteMarchingCubes()

    # number_of_iterations=30 has little effect on the error.
    smoother = vtkWindowedSincPolyDataFilter(number_of_iterations=30, non_manifold_smoothing=True,
                                             normalize_coordinates=True, generate_error_scalars=True)
    # Try, smoother.SetPassBand(0.001) increases the error a lot!
    # smoother = vtkWindowedSincPolyDataFilter(number_of_iterations=30, non_manifold_smoothing=True,
    #                                          normalize_coordinates=True, generate_error_scalars=True,
    #                                          boundary_smoothing=False, feature_edge_smoothing=False,
    #                                          feature_angle=120, pass_band=0.001)

    # Calculate cell normals.
    normals = vtkPolyDataNormals(compute_cell_normals=True, compute_point_normals=False, consistency=True,
                                 auto_orient_normals=True, feature_angle=60.0)

    # Create the pipeline and then update smoother which will also update voi
    # so that we can use se_range in the mapper.
    p = reader_volume >> voi >> contour >> smoother >> normals
    smoother.update()

    srange = voi.output.GetScalarRange()
    print('Scalar range', srange)

    # Find min and max of the smoother error.
    se_range = smoother.GetOutput().GetPointData().GetScalars().GetRange()
    print('Smoother error range:', se_range)
    if se_range[1] > 1:
        print('Big smoother error: min/max:', se_range[0], se_range[1])

    lut = get_diverging_lut(4)

    mapper = vtkPolyDataMapper(scalar_visibility=True, scalar_range=se_range, lookup_table=lut)
    p >> mapper
    # mapper.SetScalarModeToUseCellData() # Contains the label eg. 31
    mapper.SetScalarModeToUsePointData()  # The smoother error relates to the verts.

    # Take the isosurface data and create the geometry.
    actor = vtkLODActor(mapper=mapper, number_of_cloud_points=100000)

    # Create the renderer.
    ren = vtkRenderer(background=colors.GetColor3d('DimGray'))
    ren.AddActor(actor)

    # Create a window for the renderer of size 600X600
    ren_win = vtkRenderWindow(size=(600, 600), window_name='MeshLabelImageColor')
    ren_win.AddRenderer(ren)
    ren_win.Render()

    # Set a user interface interactor for the render window.
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    # Start the initialization and rendering.
    iren.Initialize()
    iren.Start()


def get_diverging_lut(ct=0):
    """
    See: [Diverging Color Maps for Scientific Visualization](https://www.kennethmoreland.com/color-maps/)

    :param ct: The index of the color map to use.
    :return: The lookup table.
    """

    cm = dict()
    # Start point = 0.0, mid point = 0.5 and end point = 1.0.
    # Each value is a list with three sublists corresponding to the start point,
    # mid point and end point along with the rgb color values for the respective point.
    # cool to warm
    cm[0] = [[0.0, 0.230, 0.299, 0.754], [0.5, 0.865, 0.865, 0.865], [1.0, 0.706, 0.016, 0.150]]
    # purple to orange
    cm[1] = [[0.0, 0.436, 0.308, 0.631], [0.5, 0.865, 0.865, 0.865], [1.0, 0.759, 0.334, 0.046]]
    # green to purple
    cm[2] = [[0.0, 0.085, 0.532, 0.201], [0.5, 0.865, 0.865, 0.865], [1.0, 0.436, 0.308, 0.631]]
    # blue to brown
    cm[3] = [[0.0, 0.217, 0.525, 0.910], [0.5, 0.865, 0.865, 0.865], [1.0, 0.677, 0.492, 0.093]]
    # green to red
    cm[4] = [[0.0, 0.085, 0.532, 0.201], [0.5, 0.865, 0.865, 0.865], [1.0, 0.758, 0.214, 0.233]]

    ct = abs(ct)
    if ct > len(cm) - 1:
        ct = 0
        print('The selected diverging color map is unavailable. Using the default cool to warm one.')

    ctf = vtkColorTransferFunction(color_space=ColorTransferFunction.ColorSpace.VTK_CTF_DIVERGING)
    for scheme in cm[ct]:
        ctf.AddRGBPoint(*scheme)

    table_size = 256
    lut = vtkLookupTable()
    lut.SetNumberOfTableValues(table_size)
    lut.Build()

    for i in range(0, table_size):
        rgba = list(ctf.GetColor(float(i) / table_size))
        rgba.append(1)
        lut.table_value = (i, rgba)

    return lut


@dataclass(frozen=True)
class ColorTransferFunction:
    @dataclass(frozen=True)
    class ColorSpace:
        VTK_CTF_RGB: int = 0
        VTK_CTF_HSV: int = 1
        VTK_CTF_LAB: int = 2
        VTK_CTF_DIVERGING: int = 3
        VTK_CTF_LAB_CIEDE2000: int = 4
        VTK_CTF_STEP: int = 5

    @dataclass(frozen=True)
    class Scale:
        VTK_CTF_LINEAR: int = 0
        VTK_CTF_LOG10: int = 1


if __name__ == '__main__':
    main()
