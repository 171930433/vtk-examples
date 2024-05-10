#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkPolyData
)
from vtkmodules.vtkFiltersCore import vtkElevationFilter
from vtkmodules.vtkFiltersGeneral import vtkDeformPointSet
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

    # Set the background color.
    # colors.SetColor('bkg', 0.2, 0.3, 0.4, 1.0)

    # Create a sphere to deform
    sphere = vtkSphereSource(theta_resolution=51, phi_resolution=17)

    # Create a filter to color the sphere.
    bounds = sphere.update().output.bounds
    low_point = [(bounds[1] + bounds[0]) / 2.0, (bounds[3] + bounds[2]) / 2.0, -bounds[5]]
    high_point = low_point[:2] + [bounds[5]]

    ele = vtkElevationFilter(low_point=low_point, high_point=high_point)

    # Create a mesh to deform the sphere
    pts = vtkPoints()
    pts.SetNumberOfPoints(6)
    pts.SetPoint(0,
                 bounds[0] - 0.1 * (bounds[1] - bounds[0]),
                 (bounds[3] + bounds[2]) / 2.0,
                 (bounds[5] + bounds[4]) / 2.0)
    pts.SetPoint(1,
                 bounds[1] + 0.1 * (bounds[1] - bounds[0]),
                 (bounds[3] + bounds[2]) / 2.0,
                 (bounds[5] + bounds[4]) / 2.0)
    pts.SetPoint(2,
                 (bounds[1] + bounds[0]) / 2.0,
                 bounds[2] - 0.1 * (bounds[3] - bounds[2]),
                 (bounds[5] + bounds[4]) / 2.0)
    pts.SetPoint(3,
                 (bounds[1] + bounds[0]) / 2.0,
                 bounds[3] + 0.1 * (bounds[3] - bounds[2]),
                 (bounds[5] + bounds[4]) / 2.0)
    pts.SetPoint(4,
                 (bounds[1] + bounds[0]) / 2.0,
                 (bounds[3] + bounds[2]) / 2.0,
                 bounds[4] - 0.1 * (bounds[5] - bounds[4]))
    pts.SetPoint(5,
                 (bounds[1] + bounds[0]) / 2.0,
                 (bounds[3] + bounds[2]) / 2.0,
                 bounds[5] + 0.1 * (bounds[5] - bounds[4]))
    tris = vtkCellArray()

    cells = [[2, 0, 4], [1, 2, 4], [3, 1, 4], [0, 3, 4], [0, 2, 5], [2, 1, 5], [1, 3, 5], [3, 0, 5]]

    for cell in cells:
        tris.InsertNextCell(3)
        for c in cell:
            tris.InsertCellPoint(c)

    pd = vtkPolyData(points=pts, polys=tris)

    mesh_mapper = vtkPolyDataMapper()
    pd >> mesh_mapper
    mesh_actor = vtkActor(mapper=mesh_mapper)
    mesh_actor.property.representation = Property.Representation.VTK_WIREFRAME
    mesh_actor.property.color = colors.GetColor3d('Black')

    deform = vtkDeformPointSet(control_mesh_data=pd)
    sphere >> ele >> deform
    deform.update()

    control_point = pts.GetPoint(5)
    pts.SetPoint(5, control_point[0],
                 control_point[1],
                 bounds[5] + .8 * (bounds[5] - bounds[4]))
    pts.Modified()

    poly_mapper = vtkPolyDataMapper()
    deform >> poly_mapper
    poly_mapper.SetInputConnection(deform.GetOutputPort())
    poly_actor = vtkActor(mapper=poly_mapper)

    renderer = vtkRenderer(background=colors.GetColor3d('DarkSlateGray'))
    ren_win = vtkRenderWindow(size=(300, 300), window_name='DeformPointSet')
    ren_win.AddRenderer(renderer)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    renderer.AddActor(poly_actor)
    renderer.AddActor(mesh_actor)

    renderer.active_camera.position = (1, 1, 1)
    renderer.ResetCamera()

    ren_win.Render()

    iren.Start()


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
