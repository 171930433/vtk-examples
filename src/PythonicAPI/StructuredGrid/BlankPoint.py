#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkStructuredGrid
from vtkmodules.vtkFiltersGeometry import vtkStructuredGridGeometryFilter
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    points = vtkPoints()
    grid_size = 8
    counter = 0
    pt_idx = 0
    # Create a 5x5 grid of points
    for j in range(0, grid_size):
        for i in range(0, grid_size):
            if i == 3 and j == 3:  # Make one point higher than the rest.
                points.InsertNextPoint(i, j, 2)
                print(f'The different point is number {counter}.')
                pt_idx = counter
            else:
                # Make most of the points the same height.
                points.InsertNextPoint(i, j, 0)
            counter += 1

    # Specify the dimensions of the grid.
    structured_grid = vtkStructuredGrid(dimensions=(grid_size, grid_size, 1), points=points)
    structured_grid.BlankPoint(pt_idx)

    # Check.
    def is_visible(pt_num):
        if structured_grid.IsPointVisible(pt_num):
            return f'Point {pt_num:2d} is visible.'
        else:
            return f'Point {pt_num:2d} is not visible.'

    # Should not be visible.
    print(f'{is_visible(pt_idx)}')
    # Should be visible.
    print(f'{is_visible(7)}')

    # We need the geometry filter to ensure that the
    # blanked point and surrounding faces is missing.
    geometry_filter = vtkStructuredGridGeometryFilter()

    # Create a mapper and actor.
    grid_mapper = vtkDataSetMapper()
    structured_grid >> geometry_filter >> grid_mapper

    grid_actor = vtkActor(mapper=grid_mapper)
    grid_actor.property.edge_visibility = True
    grid_actor.property.edge_color = colors.GetColor3d('Blue')

    # Visualize
    renderer = vtkRenderer(background=colors.GetColor3d('ForestGreen'))
    ren_win = vtkRenderWindow(window_name='BlankPoint')
    ren_win.AddRenderer(renderer)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    renderer.AddActor(grid_actor)

    ren_win.Render()
    iren.Start()


if __name__ == '__main__':
    main()
