#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkSphere
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

    # Set the background color.
    colors.SetColor('BkgColor', [51, 77, 102, 255])

    sphere = vtkSphere()

    # get the model bounds.
    mb = list()
    for i in range(0, 6, 2):
        mb.append([-2.0, 2.0])
    # Flatten the list.
    model_bounds = [x for mbb in mb for x in mbb]

    # Sample the function
    sample = vtkSampleFunction(implicit_function=sphere, sample_dimensions=(50, 50, 50), model_bounds=model_bounds)

    # Create the 0 isosurface.
    contours = vtkContourFilter()
    contours.GenerateValues(1, 1, 1)

    # Map the contours to graphical primitives.
    contour_mapper = vtkPolyDataMapper(scalar_visibility=False)
    sample >> contours >> contour_mapper

    # Create an actor for the contours.
    contour_actor = vtkActor(mapper=contour_mapper)
    contour_actor.property.color = colors.GetColor3d('White')

    # Visualize
    renderer = vtkRenderer(background=colors.GetColor3d('BkgColor'))
    render_window = vtkRenderWindow(window_name='ImplicitSphere')
    render_window.AddRenderer(renderer)

    renderer.AddActor(contour_actor)

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    render_window.Render()
    interactor.Start()


if __name__ == '__main__':
    main()
