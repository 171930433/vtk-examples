#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkDoubleArray
from vtkmodules.vtkCommonDataModel import vtkRectilinearGrid
from vtkmodules.vtkFiltersGeneral import vtkShrinkFilter
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    x_array = vtkDoubleArray()
    x_array.InsertNextValue(0.0)
    x_array.InsertNextValue(2.0)

    y_array = vtkDoubleArray()
    y_array.InsertNextValue(0.0)
    y_array.InsertNextValue(1.0)
    y_array.InsertNextValue(2.0)

    z_array = vtkDoubleArray()
    z_array.InsertNextValue(0.0)
    z_array.InsertNextValue(5.0)

    # Create a grid.
    grid = vtkRectilinearGrid(dimensions=(2, 3, 2),
                              x_coordinates=x_array, y_coordinates=y_array, z_coordinates=z_array)

    shrink_filter = vtkShrinkFilter(shrink_factor=0.8)

    # Create a mapper and actor.
    mapper = vtkDataSetMapper()
    grid >> shrink_filter >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('PeachPuff')

    # Visualize
    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    render_window = vtkRenderWindow(window_name='VisualizeRectilinearGrid')
    render_window.AddRenderer(renderer)

    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    renderer.AddActor(actor)
    renderer.active_camera.Roll(10.0)
    renderer.active_camera.Elevation(60.0)
    renderer.active_camera.Azimuth(30.0)
    renderer.ResetCamera()

    render_window.Render()
    render_window_interactor.Start()


if __name__ == '__main__':
    main()
