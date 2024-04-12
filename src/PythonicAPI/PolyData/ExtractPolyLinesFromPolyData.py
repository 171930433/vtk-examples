#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkIdList
from vtkmodules.vtkCommonDataModel import vtkPlane
from vtkmodules.vtkFiltersCore import (
    vtkCutter,
    vtkStripper
)
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()
    line_color = colors.GetColor3d('peacock')
    model_color = colors.GetColor3d('silver')
    background_color = colors.GetColor3d('wheat')

    model_source = vtkSphereSource()

    plane = vtkPlane()

    cutter = vtkCutter(cut_function=plane)
    cutter.GenerateValues(10, -0.5, 0.5)

    model_mapper = vtkPolyDataMapper()
    model_source >> model_mapper

    model = vtkActor(mapper=model_mapper)
    model.property.diffuse_color = model_color
    model.property.interpolation = Property.Interpolation.VTK_FLAT

    stripper = vtkStripper(join_contiguous_segments=True)
    stripper.JoinContiguousSegmentsOn()

    lines_mapper = vtkPolyDataMapper()
    model_source >> cutter >> stripper >> lines_mapper

    lines = vtkActor(mapper=lines_mapper)
    lines.property.diffuse_color = line_color
    lines.property.line_width = 3.0

    renderer = vtkRenderer(background=background_color)
    render_window = vtkRenderWindow(size=(640, 480), window_name='ExtractPolyLinesFromPolyData')
    render_window.AddRenderer(renderer)

    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window

    # Add the actors to the renderer.
    renderer.AddActor(model)
    renderer.AddActor(lines)
    renderer.active_camera.Azimuth(-45)
    renderer.active_camera.Elevation(-22.5)
    renderer.ResetCamera()

    # This starts the event loop and as a side effect causes an
    # initial render.
    render_window.Render()
    interactor.Start()

    # Extract the lines from the polydata.
    number_of_lines = cutter.GetOutput().GetNumberOfLines()

    print('-----------Lines without using vtkStripper')
    print(f'There are {number_of_lines} lines in the polydata.')

    number_of_lines = stripper.GetOutput().GetNumberOfLines()
    points = stripper.GetOutput().GetPoints()
    cells = stripper.GetOutput().GetLines()
    cells.InitTraversal()

    print('-----------Lines using vtkStripper')
    print(f'There are {number_of_lines} lines in the polydata.')

    indices = vtkIdList()
    line_count = 0

    while cells.GetNextCell(indices):
        print(f'Line {line_count}:')
        for i in range(indices.GetNumberOfIds()):
            point = points.GetPoint(indices.GetId(i))
            print(f'\t({point[0]:9.6f},{point[1]:9.6f}, {point[2]:9.6f})')
        line_count += 1


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
