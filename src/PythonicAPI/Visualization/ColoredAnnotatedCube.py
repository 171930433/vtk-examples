#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import (
    vtkColorSeries,
    vtkNamedColors
)
from vtkmodules.vtkCommonCore import (
    vtkLookupTable,
    vtkUnsignedCharArray
)
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import vtkElevationFilter
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.vtkFiltersModeling import vtkBandedPolyDataContourFilter
from vtkmodules.vtkFiltersSources import (
    vtkConeSource,
    vtkCubeSource
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import (
    vtkAnnotatedCubeActor,
    vtkAxesActor
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkPropAssembly,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkViewport
)


def main():
    colors = vtkNamedColors()

    # Basic stuff setup
    # Set up the renderer, window, and interactor

    # Try different gradient modes for the renderer.
    # Choose from:
    # vtkViewport.GradientModes.VTK_GRADIENT_RADIAL_VIEWPORT_FARTHEST_SIDE,
    # vtkViewport.GradientModes.VTK_GRADIENT_RADIAL_VIEWPORT_FARTHEST_CORNER,
    # vtkViewport.GradientModes.VTK_GRADIENT_VERTICAL,
    # vtkViewport.GradientModes.VTK_GRADIENT_HORIZONTAL,

    ren = vtkRenderer(gradient_background=True,
                      gradient_mode=vtkViewport.GradientModes.VTK_GRADIENT_RADIAL_VIEWPORT_FARTHEST_CORNER,
                      background=colors.GetColor3d('MistyRose'), background2=colors.GetColor3d('RoyalBlue'))
    ren_win = vtkRenderWindow(size=(600, 600), window_name='ColoredAnnotatedCube')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win
    style = vtkInteractorStyleTrackballCamera()
    iren.interactor_style = style

    # Create a cone with an elliptical base whose major axis is in th X-direction.
    cone_source = vtkConeSource(center=(0.0, 0.0, 0.0), radius=5.0, height=15.0, direction=(0, 1, 0), resolution=60)

    transform = vtkTransform()
    transform.Scale(1.0, 1.0, 0.75)

    trans_f = vtkTransformPolyDataFilter(transform=transform)
    cone_source >> trans_f
    bounds = trans_f.output.bounds

    elevation = vtkElevationFilter(low_point=(0, bounds[2], 0), high_point=(0, bounds[3], 0))

    banded_contours = vtkBandedPolyDataContourFilter(
        scalar_mode=BandedPolyDataContourFilter.ScalarMode.VTK_SCALAR_MODE_VALUE,
        generate_contour_edges=True
    )
    banded_contours.GenerateValues(11, elevation.GetScalarRange())

    # Make a lookup table using a color series.
    color_series = vtkColorSeries()
    color_series.SetColorScheme(vtkColorSeries.BREWER_DIVERGING_SPECTRAL_11)

    lut = vtkLookupTable()
    color_series.BuildLookupTable(lut, vtkColorSeries.ORDINAL)

    cone_mapper = vtkPolyDataMapper(lookup_table=lut, scalar_range=elevation.scalar_range)
    trans_f >> elevation >> banded_contours >> cone_mapper

    cone_actor = vtkActor(mapper=cone_mapper)

    # Contouring
    contour_line_mapper = vtkPolyDataMapper(
        scalar_range=elevation.scalar_range,
        resolve_coincident_topology=Mapper.ResolveCoincidentTopology.VTK_RESOLVE_POLYGON_OFFSET
    )
    contour_line_mapper.SetInputData(banded_contours.GetContourEdgesOutput())

    contour_line_actor = vtkActor(mapper=contour_line_mapper)
    contour_line_actor.property.color = colors.GetColor3d('DimGray')

    # Set up the Orientation Marker Widget.
    prop_assembly = make_annotated_cube_actor()
    om1 = vtkOrientationMarkerWidget(orientation_marker=prop_assembly,
                                     interactor=iren, default_renderer=ren, enabled=True, interactive=True
                                     )

    xyz_labels = ['X', 'Y', 'Z']
    scale = [1.0, 1.0, 1.0]
    total_length = [1.0, 1.0, 1.0]
    axes = make_axes_actor(scale, total_length, xyz_labels)
    om2 = vtkOrientationMarkerWidget(orientation_marker=axes, viewport=(0.8, 0, 1.0, 0.2),
                                     interactor=iren, default_renderer=ren, enabled=True, interactive=True
                                     )

    ren.AddActor(cone_actor)
    ren.AddActor(contour_line_actor)
    ren.active_camera.Azimuth(45)
    ren.active_camera.Pitch(-22.5)
    ren.ResetCamera()

    ren_win.Render()
    iren.Start()


def make_annotated_cube_actor():
    annotated_cube = vtkAnnotatedCubeActor(face_text_scale=1.0 / 3.0,
                                           x_plus_face_text='X+', x_minus_face_text='X-',
                                           y_plus_face_text='Y+', y_minus_face_text='Y-',
                                           z_plus_face_text='Z+', z_minus_face_text='Z-'
                                           )

    colors = vtkNamedColors()

    # Change the vector text colors.
    annotated_cube.text_edges_property.color = colors.GetColor3d('Black')
    annotated_cube.text_edges_property.line_width = 1

    annotated_cube.x_plus_face_property.color = colors.GetColor3d('Turquoise')
    annotated_cube.x_minus_face_property.color = colors.GetColor3d('Turquoise')
    annotated_cube.y_plus_face_property.color = colors.GetColor3d('Mint')
    annotated_cube.y_minus_face_property.color = colors.GetColor3d('Mint')
    annotated_cube.z_plus_face_property.color = colors.GetColor3d('Tomato')
    annotated_cube.z_minus_face_property.color = colors.GetColor3d('Tomato')

    annotated_cube.x_face_text_rotation = 90
    annotated_cube.y_face_text_rotation = 180
    annotated_cube.z_face_text_rotation = -90
    # Make the annotated cube transparent.
    annotated_cube.cube_property.opacity = 0

    # Colored faces for the cube.
    face_colors = vtkUnsignedCharArray()
    face_colors.SetNumberOfComponents(3)
    face_x_plus = colors.GetColor3ub('Red')
    face_x_minus = colors.GetColor3ub('Green')
    face_y_plus = colors.GetColor3ub('Blue')
    face_y_minus = colors.GetColor3ub('Yellow')
    face_z_plus = colors.GetColor3ub('Cyan')
    face_z_minus = colors.GetColor3ub('Magenta')
    face_colors.InsertNextTypedTuple(face_x_minus)
    face_colors.InsertNextTypedTuple(face_x_plus)
    face_colors.InsertNextTypedTuple(face_y_minus)
    face_colors.InsertNextTypedTuple(face_y_plus)
    face_colors.InsertNextTypedTuple(face_z_minus)
    face_colors.InsertNextTypedTuple(face_z_plus)

    cube_source = vtkCubeSource()
    cube_source.update()
    cube_source.output.cell_data.SetScalars(face_colors)

    cube_mapper = vtkPolyDataMapper()
    cube_source >> cube_mapper

    cube_actor = vtkActor(mapper=cube_mapper)

    # Assemble the colored cube and annotated cube texts into a composite prop.
    prop_assembly = vtkPropAssembly()
    prop_assembly.AddPart(annotated_cube)
    prop_assembly.AddPart(cube_actor)
    return prop_assembly


def make_axes_actor(scale, total_length, xyz_labels):
    axes = vtkAxesActor(shaft_type=vtkAxesActor.CYLINDER_SHAFT, tip_type=vtkAxesActor.CONE_TIP,
                        x_axis_label_text=xyz_labels[0], y_axis_label_text=xyz_labels[1],
                        z_axis_label_text=xyz_labels[2],
                        scale=scale,
                        total_length=total_length)
    axes.cylinder_radius = 0.5 * axes.cylinder_radius
    axes.cone_radius = 1.025 * axes.cone_radius
    axes.sphere_radius = 1.5 * axes.sphere_radius

    # Set the font properties.
    tprop = axes.x_axis_caption_actor2d.caption_text_property
    tprop.italic = True
    tprop.shadow = True
    tprop.SetFontFamilyToTimes()

    # Use the same text properties on the other two axes.
    axes.y_axis_caption_actor2d.caption_text_property.ShallowCopy(tprop)
    axes.z_axis_caption_actor2d.caption_text_property.ShallowCopy(tprop)

    # Now color the labels.
    colors = vtkNamedColors()
    axes.x_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('FireBrick')
    axes.y_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('DarkGreen')
    axes.z_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('DarkBlue')

    return axes


@dataclass(frozen=True)
class BandedPolyDataContourFilter:
    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_INDEX: int = 0
        VTK_SCALAR_MODE_VALUE: int = 1


@dataclass(frozen=True)
class Mapper:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_MODE_DEFAULT: int = 0
        VTK_COLOR_MODE_MAP_SCALARS: int = 1
        VTK_COLOR_MODE_DIRECT_SCALARS: int = 2

    @dataclass(frozen=True)
    class ResolveCoincidentTopology:
        VTK_RESOLVE_OFF: int = 0
        VTK_RESOLVE_POLYGON_OFFSET: int = 1
        VTK_RESOLVE_SHIFT_ZBUFFER: int = 2

    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_DEFAULT: int = 0
        VTK_SCALAR_MODE_USE_POINT_DATA: int = 1
        VTK_SCALAR_MODE_USE_CELL_DATA: int = 2
        VTK_SCALAR_MODE_USE_POINT_FIELD_DATA: int = 3
        VTK_SCALAR_MODE_USE_CELL_FIELD_DATA: int = 4
        VTK_SCALAR_MODE_USE_FIELD_DATA: int = 5


if __name__ == '__main__':
    main()
