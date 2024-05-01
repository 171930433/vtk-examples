#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import (
    vtkBox,
    vtkImplicitBoolean,
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

    # Create a sphere.
    sphere = vtkSphere(radius=1.0, center=(1, 0, 0))

    # Create a box.
    box = vtkBox(bounds=(-1, 1, -1, 1, -1, 1))

    # Combine the two implicit functions.
    # You can also experiment with operation types of VTK_UNION or VTK_INTERSECTION.
    boolean = vtkImplicitBoolean(operation_type=vtkImplicitBoolean().VTK_DIFFERENCE)
    boolean.AddFunction(box)
    boolean.AddFunction(sphere)

    # The sample function generates a distance function from the implicit
    # function. This is then contoured to get a polygonal surface.
    sample = vtkSampleFunction(implicit_function=boolean, model_bounds=(-1, 2, -1, 1, -1, 1),
                               sample_dimensions=(40, 40, 40), compute_normals=False)

    # Contour
    surface = vtkContourFilter(value=(0, 0.0))

    # Mapper
    mapper = vtkPolyDataMapper(scalar_visibility=False)
    sample >> surface >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.edge_visibility = True
    actor.property.color = colors.GetColor3d('AliceBlue')
    actor.property.edge_color = colors.GetColor3d('SteelBlue')

    # A renderer and render window.
    renderer = vtkRenderer(background=colors.GetColor3d('Silver'))
    renwin = vtkRenderWindow(window_name='BooleanOperationImplicitFunctions')
    renwin.AddRenderer(renderer)

    # Add the actor.
    renderer.AddActor(actor)

    # An interactor.
    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renwin)

    # Start
    interactor.Initialize()
    renwin.Render()

    renderer.GetActiveCamera().SetPosition(5.0, -4.0, 1.6)
    renderer.GetActiveCamera().SetViewUp(0.1, 0.5, 0.9)
    renderer.GetActiveCamera().SetDistance(6.7)
    renwin.Render()
    interactor.Start()


if __name__ == '__main__':
    main()
