#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPerlinNoise
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

    perlin_noise = vtkPerlinNoise(frequency=(2, 1.25, 1.5), phase=(0, 0, 0))

    sample = vtkSampleFunction(implicit_function=perlin_noise, compute_normals=False, sample_dimensions=(65, 65, 20))

    surface = vtkContourFilter()
    surface.SetValue(0, 0.0)

    mapper = vtkPolyDataMapper(scalar_visibility=False)
    sample >> surface >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('SteelBlue')

    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    render_window = vtkRenderWindow(size=(300, 300), window_name='PerlinNoise')
    render_window.AddRenderer(renderer)
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window

    # Add the actors to the renderer, set the background and size.
    renderer.AddActor(actor)

    render_window.Render()
    interactor.Start()


if __name__ == '__main__':
    main()
