#!/usr/bin/env python3

from dataclasses import dataclass

"""
The scene consists of:
1) four actors: a rectangle, a box, a cone and a sphere.
   The box, the cone and the sphere are above the rectangle.
2) Two spotlights, one in the direction of the box, another one in the
   direction of the sphere.
   Both lights are above the box, the cone and  the sphere.
3) A headlight has been added to fill in some of the dark shadows.
"""

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkPolyDataNormals
from vtkmodules.vtkFiltersSources import (
    vtkConeSource,
    vtkCubeSource,
    vtkPlaneSource,
    vtkSphereSource
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkLight,
    vtkLightActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor
)
from vtkmodules.vtkRenderingOpenGL2 import (
    vtkCameraPass,
    vtkOpaquePass,
    vtkOpenGLRenderer,
    vtkRenderPassCollection,
    vtkSequencePass,
    vtkShadowMapPass
)


def main():
    colors = vtkNamedColors()

    renderer = vtkOpenGLRenderer(background=colors.GetColor3d('Silver'), background2=colors.GetColor3d('Black'),
                                 gradient_background=True, automatic_light_creation=False)
    ren_win = vtkRenderWindow(size=(640, 480), window_name='ShadowsLightsDemo', multi_samples=0, alpha_bit_planes=1)
    ren_win.AddRenderer(renderer)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Set up a render pass pipeline.
    shadows = vtkShadowMapPass()
    passes = vtkRenderPassCollection()
    passes.AddItem(shadows.shadow_map_baker_pass)
    passes.AddItem(shadows)

    opaque = vtkOpaquePass()
    passes.AddItem(opaque)

    seq = vtkSequencePass()
    seq.SetPasses(passes)

    camera_p = vtkCameraPass()
    camera_p.delegate_pass = seq

    # Tell the renderer to use our render pass pipeline.
    renderer.SetPass(camera_p)

    box_color = colors.GetColor3d('Tomato')
    rectangle_color = colors.GetColor3d('Beige')
    cone_color = colors.GetColor3d('Peacock')
    sphere_color = colors.GetColor3d('Banana')

    rectangle_source = vtkPlaneSource(origin=(-5.0, 0.0, 5.0), point1=(5.0, 0.0, 5.0), point2=(-5.0, 0.0, -5.0),
                                      resolution=(100, 100))

    rectangle_mapper = vtkPolyDataMapper(scalar_visibility=False)
    rectangle_source >> rectangle_mapper

    rectangle_actor = vtkActor(mapper=rectangle_mapper, visibility=True)
    rectangle_actor.property.color = rectangle_color

    box_source = vtkCubeSource(x_length=2.0, y_length=1.0, z_length=1.0)

    box_normals = vtkPolyDataNormals(compute_point_normals=False, compute_cell_normals=True)

    box_mapper = vtkPolyDataMapper(scalar_visibility=False)
    box_source >> box_normals >> box_mapper

    box_actor = vtkActor(mapper=box_mapper, visibility=True, position=(-2.0, 2.0, 0.0))
    box_actor.property.color = box_color

    cone_source = vtkConeSource(resolution=24, direction=(1.0, 1.0, 1.0))

    cone_mapper = vtkPolyDataMapper(scalar_visibility=False)
    cone_source >> cone_mapper

    cone_actor = vtkActor(mapper=cone_mapper, visibility=True, position=(0.0, 1.0, 1.0))
    cone_actor.property.color = cone_color

    sphere_source = vtkSphereSource(theta_resolution=32, phi_resolution=32)

    sphere_mapper = vtkPolyDataMapper(scalar_visibility=False)
    sphere_source >> sphere_mapper

    sphere_actor = vtkActor(mapper=sphere_mapper, visibility=True, position=(2.0, 2.0, -1.0))
    sphere_actor.property.color = sphere_color

    renderer.AddViewProp(rectangle_actor)
    renderer.AddViewProp(box_actor)
    renderer.AddViewProp(cone_actor)
    renderer.AddViewProp(sphere_actor)

    # Spotlights.

    # Lighting the box.
    l1 = vtkLight(position=(-4.0, 4.0, -1.0), focal_point=box_actor.position, color=colors.GetColor3d('White'),
                  positional=True, switch=True)
    renderer.AddLight(l1)

    # Lighting the sphere.
    l2 = vtkLight(position=(4.0, 5.0, 1.0), focal_point=sphere_actor.position, color=colors.GetColor3d('Magenta'),
                  positional=True, switch=True)
    renderer.AddLight(l2)

    # For each spotlight, add a light frustum wireframe representation and a cone
    # wireframe representation, colored with the light color.
    angle = l1.cone_angle
    if l1.LightTypeIsSceneLight() and l1.GetPositional() and angle < 180.0:  # spotlight
        la = vtkLightActor(light=l1)
        # la.SetLight(l1)
        renderer.AddViewProp(la)
    angle = l2.cone_angle
    if l2.LightTypeIsSceneLight() and l2.GetPositional() and angle < 180.0:  # spotlight
        la = vtkLightActor(light=l2)
        # la.SetLight(l2)
        renderer.AddViewProp(la)

    # Add in a headlight.
    light = vtkLight(light_type=Light.LightType.VTK_LIGHT_TYPE_HEADLIGHT, position=(0.0, 8.0, 0.0),
                     focal_point=(0.0, 0.0, 0.0), diffuse_color=colors.GetColor3d('LightGrey'))
    renderer.AddLight(light)

    ren_win.Render()
    ren_win.SetWindowName('ShadowsLightsDemo')

    renderer.ResetCamera()

    camera = renderer.active_camera
    camera.Azimuth(40.0)
    camera.Elevation(10.0)

    ren_win.Render()

    iren.Start()


@dataclass(frozen=True)
class Light:
    @dataclass(frozen=True)
    class LightType:
        VTK_LIGHT_TYPE_HEADLIGHT: int = 1
        VTK_LIGHT_TYPE_CAMERA_LIGHT: int = 2
        VTK_LIGHT_TYPE_SCENE_LIGHT: int = 3


if __name__ == '__main__':
    main()
