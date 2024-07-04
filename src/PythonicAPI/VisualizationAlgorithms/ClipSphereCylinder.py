#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import (
    vtkCylinder,
    vtkImplicitBoolean,
    vtkSphere
)
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import vtkClipPolyData
from vtkmodules.vtkFiltersSources import vtkPlaneSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Demonstrate the use of clipping on polygonal data.

    # Create the pipeline.
    plane = vtkPlaneSource(x_resolution=25, y_resolution=25,
                           origin=(-1, -1, 0), point1=(1, -1, 0), point2=(-1, 1, 0))
    plane.update()

    transform_sphere = vtkTransform()
    transform_sphere.Identity()
    transform_sphere.Translate(0.4, -0.4, 0)
    transform_sphere.Inverse()

    sphere = vtkSphere(transform=transform_sphere, radius=0.5)

    transform_cylinder = vtkTransform()
    transform_cylinder.Identity()
    transform_cylinder.Translate(-0.4, 0.4, 0)
    transform_cylinder.RotateZ(30)
    transform_cylinder.RotateY(60)
    transform_cylinder.RotateX(90)
    transform_cylinder.Inverse()

    cylinder = vtkCylinder(radius=0.3, transform=transform_cylinder)

    boolean = vtkImplicitBoolean()
    boolean.AddFunction(cylinder)
    boolean.AddFunction(sphere)

    clipper = vtkClipPolyData(input_connection=plane.output_port, clip_function=boolean,
                              generate_clipped_output=True, generate_clip_scalars=True, value=0)
    clipper.update()

    clip_mapper = vtkPolyDataMapper(scalar_visibility=False)
    clipper >> clip_mapper

    clip_actor = vtkActor(mapper=clip_mapper)
    clip_actor.property.diffuse_color = colors.GetColor3d('MidnightBlue')
    clip_actor.property.representation = Property.Representation.VTK_WIREFRAME

    clip_inside_mapper = vtkPolyDataMapper(input_data=clipper.clipped_output, scalar_visibility=False)

    clip_inside_actor = vtkActor(mapper=clip_inside_mapper)
    clip_inside_actor.property.diffuse_color = colors.GetColor3d('LightBlue')

    # Create the graphics stuff.
    ren = vtkRenderer(background=colors.GetColor3d('Wheat'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='ClipSphereCylinder')
    ren_win.AddRenderer(ren)

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Add the actors to the renderer.
    ren.AddActor(clip_actor)

    ren.AddActor(clip_inside_actor)
    ren.ResetCamera()
    ren.active_camera.Dolly(1.4)
    ren.ResetCameraClippingRange()

    # Render the image.
    ren_win.Render()
    iren.Start()


@dataclass(frozen=True)
class Property:
    @dataclass(frozen=True)
    class Interpolation:
        VTK_FLAT: int = 0
        VTK_GOURAUD: int = 1
        VTK_PHONG: int = 2
        VTK_PBR: int = 3

    @dataclass(frozen=True)
    class Representation:
        VTK_POINTS: int = 0
        VTK_WIREFRAME: int = 1
        VTK_SURFACE: int = 2


if __name__ == '__main__':
    main()
