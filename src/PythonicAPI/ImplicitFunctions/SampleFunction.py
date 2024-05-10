#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkSuperquadric
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
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

    implicitFunction = vtkSuperquadric(phi_roundness=2.5, theta_roundness=0.5)

    # Get the model bounds.
    mb = list()
    for i in range(0, 6, 2):
        mb.append([-2.0, 2.0])
    # Flatten the list.
    model_bounds = [x for mbb in mb for x in mbb]

    # Sample the function
    sample = vtkSampleFunction(implicit_function=implicitFunction, sample_dimensions=(50, 50, 50),
                               model_bounds=model_bounds)

    # Create the 0 isosurface.
    contours = vtkContourFilter()
    contours.GenerateValues(1, 2.0, 2.0)

    # Map the contours to graphical primitives.
    contour_mapper = vtkPolyDataMapper(scalar_range=(0.0, 1.2))
    sample >> contours >> contour_mapper

    # Create an actor for the contours.
    contour_actor = vtkActor(mapper=contour_mapper)
    contour_actor.property.color = colors.GetColor3d('White')

    # Create a box around the function to indicate the sampling volume.

    # Create outline.
    outline = vtkOutlineFilter()

    # Map it to graphics primitives.
    outline_mapper = vtkPolyDataMapper()
    sample >> outline >> outline_mapper

    # Create an actor.
    outline_actor = vtkActor(mapper=outline_mapper)
    outline_actor.property.color = colors.GetColor3d("Black")

    # Visualize
    renderer = vtkRenderer(background=colors.GetColor3d("Tan"))
    render_window = vtkRenderWindow(window_name='SampleFunction')
    render_window.AddRenderer(renderer)

    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window

    renderer.AddActor(contour_actor)
    renderer.AddActor(outline_actor)

    # Enable user interface interactor.
    render_window.Render()
    interactor.Start()


if __name__ == '__main__':
    main()
