#!/usr/bin/env python3

import numpy as np
# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkFiltersCore import vtkResampleWithDataSet
from vtkmodules.vtkFiltersGeneral import vtkTableToPolyData
from vtkmodules.vtkFiltersPoints import (
    vtkGaussianKernel,
    vtkPointInterpolator
)
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkIOInfovis import vtkDelimitedTextReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPointGaussianMapper,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Plot the scalar field of points onto a PolyData surface.'
    epilogue = '''
This example uses vtkPointInterpolator with a Gaussian Kernel (or other kernel)
 to interpolate and extrapolate more smoothly the fields inside and outside the probed area.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('points_fn', help='sparsePoints.txt.')
    parser.add_argument('probe_fn', help='InterpolatingOnSTL_final.stl.')

    args = parser.parse_args()
    return args.points_fn, args.probe_fn


def main():
    points_fn, probe_fn = get_program_parameters()

    colors = vtkNamedColors()

    points_reader = vtkDelimitedTextReader(file_name=points_fn, detect_numeric_columns=True,
                                           field_delimiter_characters='\t', have_headers=True)

    table_points = vtkTableToPolyData(x_column='x', y_column='y', z_column='z')

    points = (points_reader >> table_points).update().output
    points.point_data.SetActiveScalars('val')
    range = points.point_data.scalars.range

    # Read a probe surface.
    stl_reader = vtkSTLReader(file_name=probe_fn)

    surface = stl_reader.update().output
    bounds = np.array(surface.bounds)

    dims = np.array([101, 101, 101])
    box = vtkImageData(dimensions=dims,
                       spacing=((bounds[1::2] - bounds[:-1:2]) / (dims - 1)),
                       origin=bounds[::2])

    # Gaussian kernel.
    gaussian_kernel = vtkGaussianKernel(sharpness=2, radius=12)

    interpolator = vtkPointInterpolator(input_data=box, source_data=points, kernel=gaussian_kernel)

    resample = vtkResampleWithDataSet(input_data=surface)
    resample.SetSourceConnection(interpolator.GetOutputPort())

    mapper = vtkPolyDataMapper(scalar_range=range)
    resample >> mapper

    actor = vtkActor(mapper=mapper)
    actor.SetMapper(mapper)

    splat_shader_code = """
        //VTK::Color::Impl\n
        float dist = dot(offsetVCVSOutput.xy,offsetVCVSOutput.xy);\n
        if (dist > 1.0) {\n
          discard;\n
        } else {\n
          float scale = (1.0 - dist);\n
          ambientColor *= scale;\n
          diffuseColor *= scale;\n
        }\n
    """
    point_mapper = vtkPointGaussianMapper(input_data=points, scalar_range=range, scale_factor=0.6, emissive=False)
    point_mapper.splat_shader_code = splat_shader_code

    point_actor = vtkActor(mapper=point_mapper)

    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='PointInterpolator')
    ren_win.AddRenderer(renderer)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    renderer.AddActor(actor)
    renderer.AddActor(point_actor)

    renderer.ResetCamera()
    renderer.active_camera.Elevation(-45)

    iren.Initialize()

    ren_win.Render()
    iren.Start()


if __name__ == '__main__':
    main()
