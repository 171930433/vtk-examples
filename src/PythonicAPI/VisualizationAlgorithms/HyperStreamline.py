#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersGeneral import vtkHyperStreamline
from vtkmodules.vtkFiltersGeometry import vtkImageDataGeometryFilter
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkImagingHybrid import vtkPointLoad
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkLogLookupTable,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Create the RenderWindow, Renderer and Interactor.
    ren = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='HyperStreamline')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Generate the tensors.
    pt_load = vtkPointLoad(load_value=100.0, sample_dimensions=(20, 20, 20),
                           compute_effective_stress=True,
                           model_bounds=(-10, 10, -10, 10, -10, 10))
    pt_load.update()

    lut = vtkLogLookupTable()
    lut.SetHueRange(0.6667, 0.0)

    # Make the hyperstreamlines.
    hyper_streamlines = list()
    hyper_streamlines.append(
        vtkHyperStreamline(input_data=pt_load.output, start_position=(9, 9, -9),
                           maximum_propagation_distance=18, integration_step_length=0.1,
                           step_length=0.01, radius=0.25, number_of_sides=18,
                           integration_eigenvector=
                           HyperStreamline.IntegrationEigenvector.VTK_INTEGRATE_MINOR_EIGENVECTOR,
                           integration_direction=
                           HyperStreamline.IntegrationDirection.VTK_INTEGRATE_BOTH_DIRECTIONS)
    )
    hyper_streamlines.append(
        vtkHyperStreamline(input_data=pt_load.output, start_position=(-9, -9, -9),
                           maximum_propagation_distance=18, integration_step_length=0.1,
                           step_length=0.01, radius=0.25, number_of_sides=18,
                           integration_eigenvector=
                           HyperStreamline.IntegrationEigenvector.VTK_INTEGRATE_MINOR_EIGENVECTOR,
                           integration_direction=
                           HyperStreamline.IntegrationDirection.VTK_INTEGRATE_BOTH_DIRECTIONS)
    )
    hyper_streamlines.append(
        vtkHyperStreamline(input_data=pt_load.output, start_position=(9, -9, -9),
                           maximum_propagation_distance=18, integration_step_length=0.1,
                           step_length=0.01, radius=0.25, number_of_sides=18,
                           integration_eigenvector=
                           HyperStreamline.IntegrationEigenvector.VTK_INTEGRATE_MINOR_EIGENVECTOR,
                           integration_direction=
                           HyperStreamline.IntegrationDirection.VTK_INTEGRATE_BOTH_DIRECTIONS)
    )
    hyper_streamlines.append(
        vtkHyperStreamline(input_data=pt_load.output, start_position=(-9, 9, -9),
                           maximum_propagation_distance=18, integration_step_length=0.1,
                           step_length=0.01, radius=0.25, number_of_sides=18,
                           integration_eigenvector=
                           HyperStreamline.IntegrationEigenvector.VTK_INTEGRATE_MINOR_EIGENVECTOR,
                           integration_direction=
                           HyperStreamline.IntegrationDirection.VTK_INTEGRATE_BOTH_DIRECTIONS)
    )

    actors = list()
    for hsl in hyper_streamlines:
        mapper = vtkPolyDataMapper(lookup_table=lut, scalar_range=pt_load.output.scalar_range)
        hsl >> mapper
        actors.append(vtkActor(mapper=mapper))

    # A plane for context.
    g = vtkImageDataGeometryFilter()
    g.SetExtent(0, 100, 0, 100, 0, 0)
    pt_load >> g
    g.update()  # for scalar range
    gm = vtkPolyDataMapper(scalar_range=g.output.scalar_range)
    g >> gm
    ga = vtkActor(mapper=gm)

    # Create an outline around the data.
    outline = vtkOutlineFilter()
    outline_mapper = vtkPolyDataMapper()
    pt_load >> outline >> outline_mapper
    outline_actor = vtkActor(mapper=outline_mapper)
    outline_actor.SetMapper(outline_mapper)
    outline_actor.property.color = colors.GetColor3d('Black')

    # Create a cone whose apex indicates the application of load.
    cone_src = vtkConeSource(radius=0.5, height=2)
    cone_map = vtkPolyDataMapper()
    cone_src >> cone_map
    cone_actor = vtkActor(mapper=cone_map, position=(0, 0, 11))
    cone_actor.RotateY(90)
    cone_actor.property.color = colors.GetColor3d('Tomato')

    camera = vtkCamera()
    camera.focal_point = (0.113766, -1.13665, -1.01919)
    camera.position = (-29.4886, -63.1488, 26.5807)
    camera.view_angle = 24.4617
    camera.view_up = (0.17138, 0.331163, 0.927879)
    camera.clipping_range = (1, 100)

    for actor in actors:
        ren.AddActor(actor)
    ren.AddActor(outline_actor)
    ren.AddActor(cone_actor)
    ren.AddActor(ga)
    ren.active_camera = camera

    ren_win.Render()
    iren.Start()


@dataclass(frozen=True)
class HyperStreamline:
    @dataclass(frozen=True)
    class IntegrationDirection:
        VTK_INTEGRATE_FORWARD: int = 0
        VTK_INTEGRATE_BACKWARD: int = 1
        VTK_INTEGRATE_BOTH_DIRECTIONS: int = 2

    @dataclass(frozen=True)
    class IntegrationEigenvector:
        VTK_INTEGRATE_MAJOR_EIGENVECTOR: int = 0
        VTK_INTEGRATE_MEDIUM_EIGENVECTOR: int = 1
        VTK_INTEGRATE_MINOR_EIGENVECTOR: int = 2


if __name__ == '__main__':
    main()
