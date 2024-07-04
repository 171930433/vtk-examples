#!/usr/bin/env python3

import numpy as np
# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkFloatArray,
    vtkPoints
)
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import vtkImplicitPolyDataDistance
from vtkmodules.vtkFiltersGeneral import vtkVertexGlyphFilter
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

    sphere_source = vtkSphereSource(center=(0.0, 0.0, 0.0), radius=1.0)

    sphere_mapper = vtkPolyDataMapper(scalar_visibility=False)
    sphere_source >> sphere_mapper

    sphere_actor = vtkActor(mapper=sphere_mapper)
    sphere_actor.property.opacity = 0.3
    sphere_actor.property.color = colors.GetColor3d('Red')

    implicit_poly_data_distance = vtkImplicitPolyDataDistance(input=sphere_source.update().output)

    # Setup a grid
    points = vtkPoints()
    step = 0.1
    for x in np.arange(-2, 2, step):
        for y in np.arange(-2, 2, step):
            for z in np.arange(-2, 2, step):
                points.InsertNextPoint(x, y, z)

    # Add distances to each point.
    signed_distances = vtkFloatArray(number_of_components=1, name='SignedDistances')

    # Evaluate the signed distance function at all the grid points.
    for pointId in range(points.GetNumberOfPoints()):
        p = points.GetPoint(pointId)
        signed_distance = implicit_poly_data_distance.EvaluateFunction(p)
        signed_distances.InsertNextValue(signed_distance)

    poly_data = vtkPolyData(points=points)
    poly_data.point_data.SetScalars(signed_distances)

    vertex_glyph_filter = vtkVertexGlyphFilter()

    signed_distance_mapper = vtkPolyDataMapper(scalar_visibility=True)
    poly_data >> vertex_glyph_filter >> signed_distance_mapper

    signed_distance_actor = vtkActor(mapper=signed_distance_mapper)

    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    renderer.AddViewProp(sphere_actor)
    renderer.AddViewProp(signed_distance_actor)

    render_window = vtkRenderWindow(window_name='ImplicitPolyDataDistance')
    render_window.AddRenderer(renderer)

    ren_win_interactor = vtkRenderWindowInteractor()
    ren_win_interactor.render_window = render_window

    render_window.Render()
    ren_win_interactor.Start()


if __name__ == '__main__':
    main()
