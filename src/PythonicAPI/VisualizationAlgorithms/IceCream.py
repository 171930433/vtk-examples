#!/usr/bin/env python3


"""
This example demonstrates how to use boolean combinations of implicit
 functions to create a model of an ice cream cone.

"""
# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import (
    vtkCone,
    vtkImplicitBoolean,
    vtkPlane,
    vtkSphere
)
from vtkmodules.vtkFiltersCore import vtkContourFilter
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

    # Create implicit function primitives. These have been carefully placed to
    # give the effect that we want. We are going to use various combinations of
    # these functions to create the shape we want for example, we use planes
    # intersected with a cone (which is infinite in extent) to get a finite
    # cone.
    #
    cone = vtkCone(angle=20)
    vert_plane = vtkPlane(origin=(0.1, 0, 0), normal=(-1, 0, 0))
    base_plane = vtkPlane(origin=(1.2, 0, 0), normal=(1, 0, 0))
    ice_cream = vtkSphere(center=(1.333, 0, 0), radius=0.5)
    bite = vtkSphere(center=(1.5, 0, 0.5), radius=0.25)

    # Combine primitives to build ice-cream cone. Clip the cone with planes.
    the_cone = vtkImplicitBoolean(operation_type=vtkImplicitBoolean.VTK_INTERSECTION)
    the_cone.AddFunction(cone)
    the_cone.AddFunction(vert_plane)
    the_cone.AddFunction(base_plane)

    # Take a bite out of the ice cream.
    the_cream = vtkImplicitBoolean(operation_type=vtkImplicitBoolean.VTK_DIFFERENCE)
    the_cream.AddFunction(ice_cream)
    the_cream.AddFunction(bite)

    # The sample function generates a distance function from the
    # implicit function (which in this case is the cone). This is
    # then contoured to get a polygonal surface.
    #
    the_cone_sample = vtkSampleFunction(implicit_function=the_cone,
                                        model_bounds=(-1, 1.5, -1.25, 1.25, -1.25, 1.25),
                                        sample_dimensions=(128, 128, 128),
                                        compute_normals=False)

    the_cone_surface = vtkContourFilter(value=(0, 0.0))

    cone_mapper = vtkPolyDataMapper(scalar_visibility=False)
    the_cone_sample >> the_cone_surface >> cone_mapper

    cone_actor = vtkActor(mapper=cone_mapper)
    cone_actor.property.color = colors.GetColor3d('Chocolate')

    # The same here for the ice cream.
    #
    the_cream_sample = vtkSampleFunction(implicit_function=the_cream,
                                         model_bounds=(0, 2.5, -1.25, 1.25, -1.25, 1.25),
                                         sample_dimensions=(128, 128, 128),
                                         compute_normals=False)

    the_cream_surface = vtkContourFilter(value=(0, 0.0))

    cream_mapper = vtkPolyDataMapper(scalar_visibility=False)
    the_cream_sample >> the_cream_surface >> cream_mapper

    cream_actor = vtkActor(mapper=cream_mapper)
    cream_actor.property.diffuse_color = colors.GetColor3d('Mint')
    cream_actor.property.specular = 0.6
    cream_actor.property.specular_power = 50

    # Create the usual rendering stuff.
    #
    ren = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='IceCream')
    ren_win.AddRenderer(ren)

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Add the actors to the renderer, set the background and size.
    #
    ren.AddActor(cone_actor)
    ren.AddActor(cream_actor)

    ren.ResetCamera()
    ren.active_camera.Roll(90)
    ren.active_camera.Dolly(1.25)
    ren.ResetCameraClippingRange()
    iren.Initialize()

    # Render the image.
    #
    ren_win.Render()
    iren.Start()


if __name__ == '__main__':
    main()
