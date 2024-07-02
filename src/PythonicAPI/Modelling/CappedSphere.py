#!/usr/bin/env python3

import math

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkLine,
    vtkPolyData
)
from vtkmodules.vtkFiltersModeling import vtkRotationalExtrusionFilter
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Display a capped sphere.'
    epilogue = '''
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('angle', default=90, type=float, nargs='?',
                        help='The length of the arc in degrees from +z to -z in the +x direction in the x-z plane.')
    parser.add_argument('step', default=1, type=float, nargs='?', help='Step size in degrees.')
    parser.add_argument('radius', default=1, type=float, nargs='?', help='Radius of the arc.')
    parser.add_argument('-u', '--uncapped', action='store_true', help='Uncap the sphere.')
    parser.add_argument('-s', '--show_line', action='store_true',
                        help='Show the line that is rotationally extruded to make the surface.')
    args = parser.parse_args()
    return args.angle, args.step, args.radius, args.uncapped, args.show_line


def main():
    angle, step, radius, uncapped, show_line = get_program_parameters()
    angle = math.radians(abs(angle))
    step = math.radians(abs(step))
    radius = abs(radius)
    # With the default settings, if you set this to 45°,
    # you get a bowl with a flat bottom.
    start = math.radians(90)

    pts = get_line_points(angle, step, radius, uncapped, start)

    # Setup points and lines
    points = vtkPoints()
    lines = vtkCellArray()
    for pt in pts:
        pt_id = points.InsertNextPoint(pt)
        if pt_id < len(pts) - 1:
            line = vtkLine()
            line.GetPointIds().SetId(0, pt_id)
            line.GetPointIds().SetId(1, pt_id + 1)
            lines.InsertNextCell(line)

    polydata = vtkPolyData(points=points, lines=lines)

    # Extrude the profile to make the capped sphere
    extrude = vtkRotationalExtrusionFilter(input_data=polydata, resolution=60)

    #  Visualize
    colors = vtkNamedColors()

    # To see the line.
    line_mapper = vtkPolyDataMapper(input_data=polydata)

    line_actor = vtkActor(mapper=line_mapper)
    line_actor.property.line_width = 4
    line_actor.property.color = colors.GetColor3d('Red')

    # To see the surface.
    surface_mapper = vtkPolyDataMapper()
    extrude >> surface_mapper

    surface_actor = vtkActor(mapper=surface_mapper)
    surface_actor.property.color = colors.GetColor3d('Khaki')

    ren = vtkRenderer(background=colors.GetColor3d('LightSlateGray'))
    ren_win = vtkRenderWindow(size=(600, 600), window_name='CappedSphere')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    ren.AddActor(surface_actor)
    if show_line:
        ren.AddActor(line_actor)

    ren.ResetCamera()
    if show_line:
        ren.active_camera.Roll(90)
    ren.active_camera.Elevation(60)

    ren.ResetCameraClippingRange()

    ren_win.Render()
    iren.Start()


def get_line_points(angle, step, radius, uncapped, start):
    """
    Get the points for a line.

    :param angle: Length of the arc in degrees.
    :param step: Step size in degrees.
    :param radius: Radius of the arc.
    :param uncapped: True if uncapped.
    :param start: Starting angle.
    :return: A vector of points.
    """
    precision = 1.0e-6
    pts = list()
    # Do the curved line
    theta = 0.0
    while theta <= angle:
        x = radius * math.cos(start - theta)
        z = radius * math.sin(theta - start)
        if x < 0:
            x = 0
            pts.append((x, 0, z))
            break
        if abs(x) < precision:
            x = 0
        if abs(z) < precision:
            z = 0
        pts.append((x, 0, z))
        theta += step

    if not uncapped:
        # Drop a perpendicular from the last point to the x-axis.
        if len(pts) > 1:
            if pts[-1][0] > 0:
                last_point = pts[-1]
                num_pts = 10
                interval = float(num_pts) / radius
                for i in range(1, num_pts):
                    x = last_point[0] - i / interval
                    z = last_point[2]
                    if x < 0:
                        x = 0
                        pts.append((x, 0, z))
                        break
                    if abs(x) < precision:
                        x = 0
                    if abs(z) < precision:
                        z = 0
                    pts.append((x, 0, z))
            if pts[-1][0] > precision:
                pts.append((0, 0, pts[-1][2]))
    return pts


if __name__ == '__main__':
    main()
