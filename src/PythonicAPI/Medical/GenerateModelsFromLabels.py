#!/usr/bin/env python3

import os
import sys

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonDataModel import (
    vtkDataObject,
    vtkDataSetAttributes
)
from vtkmodules.vtkFiltersCore import (
    vtkMaskFields,
    vtkThreshold,
    vtkWindowedSincPolyDataFilter
)
from vtkmodules.vtkFiltersGeneral import (
    vtkDiscreteFlyingEdges3D,
    vtkDiscreteMarchingCubes
)
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkIOImage import vtkMetaImageReader
from vtkmodules.vtkIOXML import vtkXMLPolyDataWriter
from vtkmodules.vtkImagingStatistics import vtkImageAccumulate


def get_program_parameters():
    import argparse
    description = 'Creates vtkPolyData models from a 3D volume that contains discrete labels.'
    epilogue = '''
These volumes are normally the output of a segmentation algorithm.
The polydata for each label will be output into a separate file.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='Input volume e.g. Frog/frogtissue.mhd.')
    parser.add_argument('startlabel', type=int, help='The starting label in the input volume, e,g, 1.')
    parser.add_argument('endlabel', type=int, help='The ending label in the input volume e.g. 29')
    parser.add_argument('-m', '--marching_cubes', action='store_false',
                        help='Use Marching Cubes instead of Flying Edges.')
    args = parser.parse_args()
    return args.filename, args.startlabel, args.endlabel, args.marching_cubes


def main():
    """
    Generate models from labels.
    1) Read the meta file
    2) Generate a histogram of the labels
    3) Generate models from the labeled volume
    4) Smooth the models
    5) Output each model into a separate file

    :return:
    """

    file_name, start_label, end_label, use_flying_edges = get_program_parameters()

    if start_label > end_label:
        end_label, start_label = start_label, end_label

    reader = vtkMetaImageReader(file_name=file_name)

    if use_flying_edges:
        discrete_cubes = vtkDiscreteFlyingEdges3D()
    else:
        discrete_cubes = vtkDiscreteMarchingCubes()
    discrete_cubes.GenerateValues(end_label - start_label + 1, start_label, end_label)

    smoothing_iterations = 15
    pass_band = 0.001
    feature_angle = 120.0
    smoother = vtkWindowedSincPolyDataFilter(number_of_iterations=smoothing_iterations, boundary_smoothing=False,
                                             feature_edge_smoothing=False, feature_angle=feature_angle,
                                             pass_band=pass_band,
                                             non_manifold_smoothing=True, normalize_coordinates=True
                                             )

    selector = vtkThreshold()
    if use_flying_edges:
        selector.SetInputArrayToProcess(0, 0, 0, vtkDataObject.FIELD_ASSOCIATION_POINTS,
                                        vtkDataSetAttributes.SCALARS)
    else:
        selector.SetInputArrayToProcess(0, 0, 0, vtkDataObject.FIELD_ASSOCIATION_CELLS,
                                        vtkDataSetAttributes.SCALARS)

    # Strip the scalars from the output.
    scalars_off = vtkMaskFields()
    scalars_off.CopyAttributeOff(vtkMaskFields.POINT_DATA, vtkDataSetAttributes().SCALARS)
    scalars_off.CopyAttributeOff(vtkMaskFields.CELL_DATA, vtkDataSetAttributes().SCALARS)

    histogram = vtkImageAccumulate(component_extent=(0, end_label, 0, 0, 0, 0),
                                   component_origin=(0, 0, 0), component_spacing=(1, 1, 1))
    (reader >> histogram).update()

    geometry = vtkGeometryFilter()
    writer = vtkXMLPolyDataWriter()
    reader >> discrete_cubes >> smoother >> selector >> scalars_off >> geometry >> writer

    file_prefix = 'Label'
    for i in range(start_label, end_label + 1):
        # See if the label exists, if not skip it.
        frequency = histogram.output.point_data.scalars.GetTuple1(i)
        if frequency == 0.0:
            continue

        # Select the cells for a given label.
        selector.lower_threshold = i
        selector.upper_threshold = i

        # Output the polydata.
        output_fn = f'{file_prefix:s}{i:d}.vtp'
        print(f'{os.path.basename(sys.argv[0]):s} writing {output_fn:s}')

        writer.file_name = output_fn
        writer.Write()


if __name__ == '__main__':
    main()
