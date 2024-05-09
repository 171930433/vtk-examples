#!/usr/bin/env python3

import math
from dataclasses import dataclass
from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    VTK_DOUBLE_MAX,
    vtkPoints
)
from vtkmodules.vtkCommonDataModel import (
    vtkIterativeClosestPointTransform,
    vtkPolyData
)
from vtkmodules.vtkCommonTransforms import (
    vtkLandmarkTransform,
    vtkTransform
)
from vtkmodules.vtkFiltersGeneral import (
    vtkOBBTree,
    vtkTransformPolyDataFilter
)
from vtkmodules.vtkFiltersModeling import vtkHausdorffDistancePointSetFilter
from vtkmodules.vtkIOGeometry import (
    vtkBYUReader,
    vtkOBJReader,
    vtkSTLReader
)
from vtkmodules.vtkIOLegacy import (
    vtkPolyDataReader,
    vtkPolyDataWriter
)
from vtkmodules.vtkIOPLY import vtkPLYReader
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtkmodules.vtkInteractionWidgets import (
    vtkCameraOrientationWidget,
    vtkOrientationMarkerWidget
)
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'How to align two vtkPolyData\'s.'
    epilogue = '''

    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('src_fn', help='The polydata source file name,e.g. thingiverse/Grey_Nurse_Shark.stl.')
    parser.add_argument('tgt_fn', help='The polydata target file name, e.g. greatWhite.stl.')
    parser.add_argument('-w', action='store_true', help='Write out the aligned source and target as VTK files.')
    parser.add_argument('-omw', action='store_false',
                        help='Use an OrientationMarkerWidget instead of a CameraOrientationWidget.')
    args = parser.parse_args()
    return args.src_fn, args.tgt_fn, args.w, args.omw


def main():
    colors = vtkNamedColors()

    src_fn, tgt_fn, write_data, use_camera_omw = get_program_parameters()

    # Check that the files exist.
    src_fp = Path(src_fn)
    tgt_fp = Path(tgt_fn)
    if not src_fp.is_file():
        print(f'Nonexistent source: {src_fp}')
    if not tgt_fp.is_file():
        print(f'Nonexistent target: {tgt_fp}')
    if not src_fp.is_file() or not tgt_fp.is_file():
        return

    print('Loading source:', src_fp)
    source_polydata = read_poly_data(src_fp)
    # Save the source polydata in case the alignment process
    # does not improve segmentation.
    original_source_polydata = vtkPolyData()
    original_source_polydata.DeepCopy(source_polydata)

    print('Loading target:', tgt_fn)
    target_polydata = read_poly_data(tgt_fp)

    # If the target orientation is markedly different, you may need to apply a
    # transform to orient the target with the source.
    # For example, when using Grey_Nurse_Shark.stl as the source and
    # greatWhite.stl as the target, you need to transform the target.
    trnf = vtkTransform()
    if src_fp.name == 'Grey_Nurse_Shark.stl' and tgt_fp.name == 'greatWhite.stl':
        trnf.RotateY(90)

    tpd = vtkTransformPolyDataFilter(transform=trnf)
    p = (target_polydata >> tpd).update().output

    distance = vtkHausdorffDistancePointSetFilter()
    distance.SetInputData(0, p)
    distance.SetInputData(1, source_polydata)
    distance.update()

    distance_before_align = distance.GetOutput(0).field_data.GetArray('HausdorffDistance').GetComponent(0, 0)

    # Get initial alignment using oriented bounding boxes.
    align_bounding_boxes(source_polydata, tpd.output)

    distance.SetInputData(0, p)
    distance.SetInputData(1, source_polydata)
    distance.update()

    distance_after_align = distance.GetOutput(0).field_data.GetArray('HausdorffDistance').GetComponent(0, 0)

    best_distance = min(distance_before_align, distance_after_align)

    if distance_after_align > distance_before_align:
        source_polydata.DeepCopy(original_source_polydata)

    # Refine the alignment using IterativeClosestPoint.
    icp = vtkIterativeClosestPointTransform(source=source_polydata, target=p,
                                            maximum_number_of_landmarks=100, maximum_mean_distance=0.00001,
                                            maximum_number_of_iterations=500,
                                            check_mean_distance=True, start_by_matching_centroids=True)
    icp.landmark_transform.mode = LandmarkTransform.Mode.VTK_LANDMARK_RIGIDBODY
    icp.Update()
    icp_mean_distance = icp.GetMeanDistance()

    lm_transform = icp.landmark_transform
    # transform = vtkTransformPolyDataFilter(transform=icp.landmark_transform, input_data=source_polydata)
    transform = vtkTransformPolyDataFilter(transform=icp, input_data=source_polydata)

    distance.SetInputData(0, p)
    distance.SetInputData(1, transform.update().output)
    distance.update()

    # Note: If there is an error extracting eigenfunctions, then this will be zero.
    distance_after_icp = distance.GetOutput(0).field_data.GetArray('HausdorffDistance').GetComponent(0, 0)

    # Check if ICP worked.
    if not (math.isnan(icp_mean_distance) or math.isinf(icp_mean_distance)):
        if distance_after_icp < best_distance:
            best_distance = distance_after_icp

    print('Distances:')
    print('  Before aligning:                        {:0.5f}'.format(distance_before_align))
    print('  Aligning using oriented bounding boxes: {:0.5f}'.format(distance_before_align))
    print('  Aligning using IterativeClosestPoint:   {:0.5f}'.format(distance_after_icp))
    print('  Best distance:                          {:0.5f}'.format(best_distance))

    if write_data:
        writer = vtkPolyDataWriter()
        if best_distance == distance_before_align:
            writer.SetInputData(original_source_polydata)
        elif best_distance == distance_after_align:
            writer.SetInputData(source_polydata)
        else:
            writer.SetInputData(transform.GetOutput())
        writer.SetFileName('AlignedSource.vtk')
        writer.Write()
        writer.SetInputData(tpd.GetOutput())
        writer.SetFileName('Target.vtk')
        writer.Write()

    # Select the source to use.
    source_mapper = vtkDataSetMapper(scalar_visibility=False)
    if best_distance == distance_before_align:
        original_source_polydata >> source_mapper
        print('Using original alignment')
    elif best_distance == distance_after_align:
        source_polydata >> source_mapper
        print('Using alignment by OBB')
    else:
        transform >> source_mapper
        print('Using alignment by ICP')
    # source_mapper.ScalarVisibilityOff()

    source_actor = vtkActor(mapper=source_mapper)
    source_actor.property.opacity = 0.6
    source_actor.property.diffuse_color = colors.GetColor3d('White')

    target_mapper = vtkDataSetMapper(scalar_visibility=False)
    tpd >> target_mapper

    target_actor = vtkActor(mapper=target_mapper)
    target_actor.property.opacity = 1.0
    target_actor.property.diffuse_color = colors.GetColor3d('Tomato')

    renderer = vtkRenderer(use_hidden_line_removal=True, background=colors.GetColor3d('sea_green_light'))
    render_window = vtkRenderWindow(size=(640, 480), window_name='AlignTwoPolyDatas')
    render_window.AddRenderer(renderer)
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window

    renderer.AddActor(source_actor)
    renderer.AddActor(target_actor)

    render_window.Render()

    if use_camera_omw:
        cam_orient_manipulator = vtkCameraOrientationWidget(parent_renderer=renderer)
        # Enable the widget.
        cam_orient_manipulator.On()
    else:
        axes = vtkAxesActor()
        rgba = [0.0, 0.0, 0.0, 0.0]
        colors.GetColor('Carrot', rgba)
        widget = vtkOrientationMarkerWidget(orientation_marker=axes, outline_color=tuple(rgba[:3]),
                                            interactor=interactor, viewport=(0.0, 0.0, 0.2, 0.2),
                                            enabled=True, interactive=True)

    interactor.Start()


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


def align_bounding_boxes(source, target):
    # Use OBBTree to create an oriented bounding box for target and source
    source_obb_tree = vtkOBBTree(data_set=source, max_level=1)
    source_obb_tree.BuildLocator()

    target_obb_tree = vtkOBBTree(data_set=target, max_level=1)
    target_obb_tree.BuildLocator()

    source_landmarks = vtkPolyData()
    source_obb_tree.GenerateRepresentation(0, source_landmarks)

    target_landmarks = vtkPolyData()
    target_obb_tree.GenerateRepresentation(0, target_landmarks)

    lm_transform = vtkLandmarkTransform(target_landmarks=target_landmarks.points,
                                        mode=LandmarkTransform.Mode.VTK_LANDMARK_SIMILARITY)
    best_distance = VTK_DOUBLE_MAX
    best_points = vtkPoints()
    best_distance = best_bounding_box('X', target, source, target_landmarks, source_landmarks, best_distance,
                                      best_points)
    best_distance = best_bounding_box('Y', target, source, target_landmarks, source_landmarks, best_distance,
                                      best_points)
    best_distance = best_bounding_box('Z', target, source, target_landmarks, source_landmarks, best_distance,
                                      best_points)

    lm_transform.SetSourceLandmarks(best_points)
    lm_transform.Modified()

    lm_transform_pd = vtkTransformPolyDataFilter(transform=lm_transform)
    source >> lm_transform_pd
    source.DeepCopy(lm_transform_pd.update().output)

    return


def best_bounding_box(axis, target, source, target_landmarks, source_landmarks, best_distance, best_points):
    lm_transform = vtkLandmarkTransform(target_landmarks=target_landmarks.points,
                                        mode=LandmarkTransform.Mode.VTK_LANDMARK_SIMILARITY)
    lm_transform_pd = vtkTransformPolyDataFilter()

    source_center = source_landmarks.center

    distance = vtkHausdorffDistancePointSetFilter()
    test_transform = vtkTransform()
    test_transform_pd = vtkTransformPolyDataFilter()

    delta = 90.0
    for i in range(0, 4):
        angle = delta * i
        # Rotate about center
        test_transform.Identity()
        test_transform.Translate(source_center[0], source_center[1], source_center[2])
        if axis == 'X':
            test_transform.RotateX(angle)
        elif axis == 'Y':
            test_transform.RotateY(angle)
        else:
            test_transform.RotateZ(angle)
        test_transform.Translate(-source_center[0], -source_center[1], -source_center[2])

        test_transform_pd.transform = test_transform
        test_transform_pd.input_data = source_landmarks
        test_transform_pd.update()

        lm_transform.SetSourceLandmarks(test_transform_pd.output.points)
        lm_transform.Modified()

        lm_transform_pd.input_data = source
        lm_transform_pd.transform = lm_transform

        distance.SetInputData(0, target)
        distance.SetInputData(1, lm_transform_pd.update().output)
        distance.update()

        test_distance = distance.GetOutput(0).field_data.GetArray('HausdorffDistance').GetComponent(0, 0)
        if test_distance < best_distance:
            best_distance = test_distance
            best_points.DeepCopy(test_transform_pd.GetOutput().GetPoints())

    return best_distance


@dataclass(frozen=True)
class LandmarkTransform:
    @dataclass(frozen=True)
    class Mode:
        VTK_LANDMARK_RIGIDBODY: int = 6
        VTK_LANDMARK_SIMILARITY: int = 7
        VTK_LANDMARK_AFFINE: int = 12


if __name__ == '__main__':
    main()
