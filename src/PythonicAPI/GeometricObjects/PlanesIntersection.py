#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPlanesIntersection
from vtkmodules.vtkFiltersSources import vtkSphereSource


def main():
    sphere_source = vtkSphereSource()
    sphere_source.update()

    bounds = sphere_source.output.bounds

    box = vtkPoints(number_of_points=8)

    x_min = bounds[0]
    x_max = bounds[1]
    y_min = bounds[2]
    y_max = bounds[3]
    z_min = bounds[4]
    z_max = bounds[5]

    box.SetPoint(0, x_max, y_min, z_max)
    box.SetPoint(1, x_max, y_min, z_min)
    box.SetPoint(2, x_max, y_max, z_min)
    box.SetPoint(3, x_max, y_max, z_max)
    box.SetPoint(4, x_min, y_min, z_max)
    box.SetPoint(5, x_min, y_min, z_min)
    box.SetPoint(6, x_min, y_max, z_min)
    box.SetPoint(7, x_min, y_max, z_max)

    planes_intersection = vtkPlanesIntersection(bounds=bounds)

    intersects = planes_intersection.IntersectsRegion(box)
    if intersects == 1:
        res = 'Yes'
    else:
        res = 'No'
    print(f'Intersects? {res}')


if __name__ == '__main__':
    main()
