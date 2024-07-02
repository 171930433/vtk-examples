#!/usr/bin/env python3


# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersProgrammable import vtkProgrammableGlyphFilter
from vtkmodules.vtkFiltersSources import (
    vtkConeSource,
    vtkCubeSource,
    vtkSphereSource
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main(argv):
    colors = vtkNamedColors()

    # Create points.
    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(5, 0, 0)
    points.InsertNextPoint(10, 0, 0)

    # Combine into a polydata.
    polydata = vtkPolyData(points=points)

    # GlyphFilter needs a default glyph, but this should not be used.
    cone_source = vtkConeSource()
    glyph_filter = vtkProgrammableGlyphFilter(input_data=polydata, source_connection=cone_source.output_port)
    # Create the observer.
    observer = CalcGlyph(glyph_filter)
    glyph_filter.SetGlyphMethod(observer)

    # Create a mapper and actor.
    mapper = vtkPolyDataMapper()
    glyph_filter >> mapper
    actor = vtkActor(mapper=mapper)
    actor.property.color = colors.GetColor3d('Gold')

    # Create a renderer, render window, and interactor.
    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(window_name='ProgrammableGlyphFilter')
    ren_win.AddRenderer(renderer)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Add the actor to the scene.
    renderer.AddActor(actor)

    # Render and interact.
    ren_win.Render()
    renderer.active_camera.Zoom(0.9)
    iren.Start()


class CalcGlyph(object):
    def __init__(self, glyph_filter):
        self.glyph_filter = glyph_filter

    def __call__(self):
        point_coords = self.glyph_filter.point
        point_id = self.glyph_filter.point_id

        print(f'Calling CalcGlyph for point {point_id}')
        print(f'Point coordinates are: ({point_coords[0]}, {point_coords[1]}, {point_coords[2]})')
        if point_id == 0:
            cone_source = vtkConeSource(center=point_coords)
            self.glyph_filter.source_connection = cone_source.output_port
        elif point_id == 1:
            cube_source = vtkCubeSource(center=point_coords)
            self.glyph_filter.source_connection = cube_source.output_port
        elif point_id == 2:
            sphere_source = vtkSphereSource(center=point_coords)
            self.glyph_filter.source_connection = sphere_source.output_port


if __name__ == '__main__':
    import sys

    main(sys.argv)
