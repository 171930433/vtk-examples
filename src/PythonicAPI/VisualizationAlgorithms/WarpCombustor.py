#!/usr/bin/env python3


# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import (
    vtkAppendPolyData,
    vtkPolyDataNormals,
    vtkStructuredGridOutlineFilter
)
from vtkmodules.vtkFiltersGeneral import vtkWarpScalar
from vtkmodules.vtkFiltersGeometry import vtkStructuredGridGeometryFilter
from vtkmodules.vtkIOParallel import vtkMultiBlockPLOT3DReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    xyz_fn, q_fn = get_program_parameters()

    # Here we read data from an annular combustor. A combustor burns fuel and air
    # in a gas turbine (e.g., a jet engine) and the hot gas eventually makes its
    # way to the turbine section.
    # Note that SetFileName is an alias for SetXYZFileName so you can use file_name instead of `x_y_z_file_name`.
    pl3d = vtkMultiBlockPLOT3DReader(file_name=xyz_fn, q_file_name=q_fn, scalar_function_number=100,
                                     vector_function_number=202)
    # Update and get the block that we want.
    pl3d.update()
    pl3d_output = pl3d.output.GetBlock(0)

    # Planes are specified using an imin,imax, jmin,jmax, kmin,kmax coordinate
    # specification. Min and max i,j,k values are clamped to 0 and maximum value.
    planes = ((pl3d_output >> vtkStructuredGridGeometryFilter(extent=[10, 10, 1, 100, 1, 100])).update().output,
              (pl3d_output >> vtkStructuredGridGeometryFilter(extent=[30, 30, 1, 100, 1, 100])).update().output,
              (pl3d_output >> vtkStructuredGridGeometryFilter(extent=[45, 45, 1, 100, 1, 100])).update().output)

    # We will then use an append filter because, in that way, we can do the warping, etc.
    # by just using a single pipeline and actor.
    p = (
            planes
            >> vtkAppendPolyData()
            >> vtkWarpScalar(use_normal=True, normal=[1.0, 0.0, 0.0], scale_factor=2.5)
            >> vtkPolyDataNormals(feature_angle=60)
    ).update().output

    plane_mapper = vtkPolyDataMapper(input_data=p, scalar_range=pl3d_output.scalar_range)
    plane_actor = vtkActor(mapper=plane_mapper)

    # The outline provides context for the data and the planes.
    outline = (pl3d_output >> vtkStructuredGridOutlineFilter()).update().output
    outline_mapper = vtkPolyDataMapper(input_data=outline)
    outline_actor = vtkActor(mapper=outline_mapper)
    outline_actor.property.color = colors.GetColor3d('Black')

    # Create the usual graphics stuff.
    ren = vtkRenderer(background=colors.GetColor3d('Silver'))
    ren.AddActor(outline_actor)
    ren.AddActor(plane_actor)

    ren_win = vtkRenderWindow(size=[640, 640], window_name='WarpCombustor')
    ren_win.AddRenderer(ren)

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Create an initial view.
    ren.active_camera.clipping_range = (3.95297, 50)
    ren.active_camera.focal_point = (8.88908, 0.595038, 29.3342)
    ren.active_camera.position = (-12.3332, 31.7479, 41.2387)
    ren.active_camera.view_up = (0.060772, -0.319905, 0.945498)
    iren.Initialize()

    # Render the image.
    ren_win.Render()

    # Start the event loop.
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'Extract "computational planes" from a structured dataset. '
    epilogue = '''

   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('xyz_file_name', help='combxyz.bin.')
    parser.add_argument('q_file_name', help='combq.bin.')
    args = parser.parse_args()
    return args.xyz_file_name, args.q_file_name


if __name__ == '__main__':
    main()
