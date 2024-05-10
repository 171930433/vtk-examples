#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkQuadric
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

    # Create an ellipsoid using a implicit quadric.
    quadric = vtkQuadric(coefficients=(0.5, 1, 0.2, 0, 0.1, 0, 0, 0.2, 0, 0))

    # The sample function generates a distance function from the implicit
    # function. This is then contoured to get a polygonal surface.
    sample = vtkSampleFunction(implicit_function=quadric, model_bounds=(-0.5, 0.5, -0.5, 0.5, -0.5, 0.5),
                               sample_dimensions=(40, 40, 40), compute_normals=False)

    # Contour
    surface = vtkContourFilter()
    surface.SetValue(0, 0.0)

    # Mapper
    mapper = vtkPolyDataMapper(scalar_visibility=False)
    sample >> surface >> mapper

    # Actor
    actor = vtkActor(mapper=mapper)
    actor.property.edge_visibility = True
    actor.property.color = colors.GetColor3d('AliceBlue')
    actor.property.edge_color = colors.GetColor3d('SteelBlue')

    # A renderer and render window.
    renderer = vtkRenderer(background=colors.GetColor3d('Silver'))
    renwin = vtkRenderWindow(window_name='ImplicitQuadric')
    renwin.AddRenderer(renderer)

    # Add the actor.
    renderer.AddActor(actor)

    # An interactor.
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = renwin

    # Start
    interactor.Initialize()
    renwin.Render()
    interactor.Start()


if __name__ == '__main__':
    main()
