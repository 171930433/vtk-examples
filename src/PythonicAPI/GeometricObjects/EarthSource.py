#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkUnsignedCharArray
)
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.vtkFiltersHybrid import vtkEarthSource
from vtkmodules.vtkFiltersSources import (
    vtkCubeSource
)
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkInteractionWidgets import (
    vtkOrientationMarkerWidget
)
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
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Earth source
    earth_source = vtkEarthSource(outline=True)
    earth_source.update()
    r = earth_source.GetRadius()

    # Transform to geographic coordinates:
    # (x, y, z)->(λ, φ), +λ is East, +φ is North.
    # +x-axis -> 90°λ, +y-axis -> 90°φ, +z-axis -> 0°λ
    # This corresponds to RotateX(-90.0) followed by RotateZ(-90.0).
    # The homogenous matrix for the transform is:
    m = [[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]]
    transform = vtkTransform()
    # We need to flatten the matrix.
    transform.matrix = [x for ms in m for x in ms]

    earth_transform = vtkTransformPolyDataFilter(transform=transform)
    sphere_transform = vtkTransformPolyDataFilter(transform=transform)

    # Create a sphere
    sphere = vtkSphereSource(theta_resolution=100, phi_resolution=100, radius=r)

    # Create a mapper and actor
    mapper = vtkPolyDataMapper()
    earth_source >> earth_transform >> mapper
    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('Black')
    actor.property.line_width = 2.0

    sphere_mapper = vtkPolyDataMapper()
    sphere >> sphere_transform >> sphere_mapper
    sphere_actor = vtkActor(mapper=sphere_mapper)
    sphere_actor.property.color = colors.GetColor3d('PeachPuff')

    # Create a renderer, render window, and interactor
    renderer = vtkRenderer(background=colors.GetColor3d('LightCyan'))
    render_window = vtkRenderWindow(size=(640, 480), window_name='EarthSource')
    render_window.AddRenderer(renderer)
    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window
    style = vtkInteractorStyleTrackballCamera()
    render_window_interactor.interactor_style = style

    # Add the actor to the scene.
    renderer.AddActor(actor)
    renderer.AddActor(sphere_actor)

    # Render and interact.
    render_window.Render()

    renderer.active_camera.Zoom(1.5)
    renderer.ResetCameraClippingRange()
    render_window.Render()

    xyz_labels = ['90°E', '90°N', '0°E']
    scale = [2.0, 2.0, 2.0]
    total_length = [2.0, 2.0, 2.0]
    axes = make_axes_actor(scale, total_length, xyz_labels)
    om2 = vtkOrientationMarkerWidget(orientation_marker=axes, viewport=(0.8, 0, 1.0, 0.2),
                                     interactor=render_window_interactor, default_renderer=renderer, enabled=True,
                                     interactive=True
                                     )

    # Set up the Orientation Marker Widget.
    prop_assembly = make_annotated_cube_actor()
    om1 = vtkOrientationMarkerWidget(orientation_marker=prop_assembly,
                                     interactor=render_window_interactor, default_renderer=renderer, enabled=True,
                                     interactive=True
                                     )

    # Begin interaction.
    render_window_interactor.Start()


def make_annotated_cube_actor():
    colors = vtkNamedColors()

    annotated_cube = vtkAnnotatedCubeActor(face_text_scale=1.0 / 4.0,
                                           x_plus_face_text='90°E', x_minus_face_text='90°W',
                                           y_plus_face_text='90°N', y_minus_face_text='90°S',
                                           z_plus_face_text='0°E', z_minus_face_text='180°E'
                                           )

    # Change the vector text colors.
    annotated_cube.text_edges_property.color = colors.GetColor3d('Black')
    annotated_cube.text_edges_property.line_width = 1

    annotated_cube.x_plus_face_property.color = colors.GetColor3d('Mint')
    annotated_cube.x_minus_face_property.color = colors.GetColor3d('Mint')
    annotated_cube.y_plus_face_property.color = colors.GetColor3d('Tomato')
    annotated_cube.y_minus_face_property.color = colors.GetColor3d('Tomato')
    annotated_cube.z_plus_face_property.color = colors.GetColor3d('Turquoise')
    annotated_cube.z_minus_face_property.color = colors.GetColor3d('Turquoise')

    annotated_cube.x_face_text_rotation = -90
    annotated_cube.y_face_text_rotation = 180
    annotated_cube.z_face_text_rotation = 90
    # Make the annotated cube transparent.
    annotated_cube.cube_property.opacity = 0

    # Colored faces for the cube.
    face_colors = vtkUnsignedCharArray()
    face_colors.SetNumberOfComponents(3)
    face_x_plus = colors.GetColor3ub('DarkGreen')
    face_x_minus = colors.GetColor3ub('DarkGreen')
    face_y_plus = colors.GetColor3ub('DarkBlue')
    face_y_minus = colors.GetColor3ub('DarkBlue')
    face_z_plus = colors.GetColor3ub('FireBrick')
    face_z_minus = colors.GetColor3ub('FireBrick')
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
    colors = vtkNamedColors()

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

    # Now color the axes.
    axes.x_axis_tip_property.color = colors.GetColor3d('LimeGreen')
    axes.x_axis_shaft_property.color = colors.GetColor3d('LimeGreen')
    axes.y_axis_tip_property.color = colors.GetColor3d('Blue')
    axes.y_axis_shaft_property.color = colors.GetColor3d('Blue')
    axes.z_axis_tip_property.color = colors.GetColor3d('Red')
    axes.z_axis_shaft_property.color = colors.GetColor3d('Red')

    # Now color the labels.
    colors = vtkNamedColors()
    axes.x_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('DarkGreen')
    axes.y_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('DarkBlue')
    axes.z_axis_caption_actor2d.caption_text_property.color = colors.GetColor3d('FireBrick')

    return axes


if __name__ == '__main__':
    main()
