#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.util.execution_model import select_ports
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import (
    vtkCylinder,
    vtkSphere
)
from vtkmodules.vtkFiltersCore import (
    vtkFlyingEdges3D,
    vtkMarchingCubes,
    vtkProbeFilter
)
from vtkmodules.vtkImagingHybrid import vtkSampleFunction
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    sample_resolution, use_flying_edges = get_program_parameters()

    radius = 1.0
    # Create a sampled sphere
    implicit_sphere = vtkSphere(radius=radius)

    x_min = -radius * 2.0
    x_max = radius * 2.0
    sampled_sphere = vtkSampleFunction(implicit_function=implicit_sphere,
                                       sample_dimensions=(sample_resolution, sample_resolution, sample_resolution),
                                       model_bounds=(x_min, x_max, x_min, x_max, x_min, x_max))

    if use_flying_edges:
        iso_sphere = vtkFlyingEdges3D()
    else:
        iso_sphere = vtkMarchingCubes()
    iso_sphere.SetValue(0, 1.0)
    sampled_sphere >> iso_sphere

    # Create a sampled cylinder
    implicit_cylinder = vtkCylinder(radius=radius / 2.0)
    sampled_cylinder = vtkSampleFunction(implicit_function=implicit_cylinder,
                                         sample_dimensions=(sample_resolution, sample_resolution, sample_resolution),
                                         model_bounds=(x_min, x_max, x_min, x_max, x_min, x_max))

    # Probe cylinder with the sphere isosurface.
    probe_cylinder = vtkProbeFilter()
    iso_sphere >> select_ports(0, probe_cylinder)
    sampled_cylinder >> select_ports(1, probe_cylinder)
    probe_cylinder.update()

    # Restore the original normals.
    probe_cylinder.output.point_data.SetNormals(iso_sphere.output.point_data.normals)

    sr = probe_cylinder.output.scalar_range
    print(f'Scalar range: {sr[0]:6.3f}, {sr[1]:6.3f}')

    # Create a mapper and actor
    map_sphere = vtkPolyDataMapper(scalar_range=sr)
    probe_cylinder >> map_sphere

    sphere = vtkActor(mapper=map_sphere)

    # Visualize
    renderer = vtkRenderer(background=colors.GetColor3d('AliceBlue'))
    render_window = vtkRenderWindow(window_name='IsosurfaceSampling')
    render_window.AddRenderer(renderer)

    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    renderer.AddActor(sphere)

    render_window.Render()
    render_window_interactor.Start()


def get_program_parameters():
    import argparse
    description = 'Create an isosurface and create point data on that isosurface that is sampled from another dataset.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-r', '--resolution', type=int, default=50,
                        help='The sample resolution of the sphere and cylinder')
    parser.add_argument('-m', '--marching_cubes', action='store_false',
                        help='Use Marching Cubes instead of Flying Edges.')
    args = parser.parse_args()
    return args.resolution, args.resolution


if __name__ == '__main__':
    main()
