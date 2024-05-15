#!/usr/bin/env python3

# Translated from TenEllip.tcl

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import (
    vtkColorSeries,
    vtkNamedColors
)
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkFiltersCore import (
    vtkPolyDataNormals,
    vtkTensorGlyph
)
from vtkmodules.vtkFiltersGeometry import vtkImageDataGeometryFilter
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkFiltersSources import (
    vtkConeSource,
    vtkSphereSource
)
from vtkmodules.vtkImagingHybrid import vtkPointLoad
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Create the RenderWindow, Renderer and interactive renderer.
    ren = vtkRenderer(background=colors.GetColor3d('WhiteSmoke'))
    ren_win = vtkRenderWindow(size=(512, 512), window_name='TensorEllipsoids')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Generate the tensors.
    pt_load = vtkPointLoad(load_value=100.0, sample_dimensions=(6, 6, 6),
                           compute_effective_stress=True,
                           model_bounds=(-10, 10, -10, 10, -10, 10))

    # Extract a plane of data.
    plane = vtkImageDataGeometryFilter()
    plane.SetExtent(2, 2, 0, 99, 0, 99)
    pt_load >> plane

    # Generate the ellipsoids.
    sphere = vtkSphereSource(theta_resolution=8, phi_resolution=8)
    tensor_ellipsoids = vtkTensorGlyph(source_data=sphere.update().output,
                                       scale_factor=10, clamp_scaling=True)

    ellip_normals = vtkPolyDataNormals()

    scalar_range = plane.update().output.scalar_range  # force update for scalar range
    tensor_ellipsoids_mapper = vtkPolyDataMapper(lookup_table=make_log_lut(), scalar_range=scalar_range)
    pt_load >> tensor_ellipsoids >> ellip_normals >> tensor_ellipsoids_mapper
    tensor_actor = vtkActor()
    tensor_actor.SetMapper(tensor_ellipsoids_mapper)

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
    camera.SetClippingRange(1, 100)

    ren.AddActor(tensor_actor)
    ren.AddActor(outline_actor)
    ren.AddActor(cone_actor)
    ren.active_camera = camera

    iren.Initialize()
    ren_win.Render()
    iren.Start()


def make_log_lut():
    # Make the lookup using a Brewer palette.
    color_series = vtkColorSeries(color_scheme=vtkColorSeries.BREWER_DIVERGING_SPECTRAL_8)

    lut = vtkLookupTable(scale=LookupTable.Scale.VTK_SCALE_LOG10)
    color_series.BuildLookupTable(lut, color_series.ORDINAL)
    lut.SetNanColor(1, 0, 0, 1)
    # Original
    # lut = vtkLookupTable(scale=LookupTable.Scale.VTK_SCALE_LOG10, hue_range=(0.6667, 0.0))
    # lut.Build()

    return lut


@dataclass(frozen=True)
class LookupTable:
    @dataclass(frozen=True)
    class Scale:
        VTK_SCALE_LINEAR: int = 0
        VTK_SCALE_LOG10: int = 1


if __name__ == '__main__':
    main()
