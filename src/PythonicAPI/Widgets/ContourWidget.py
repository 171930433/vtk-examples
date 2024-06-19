#!/usr/bin/python3

import math

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkCommand,
    vtkPoints
)
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkPolyData
)
from vtkmodules.vtkInteractionWidgets import (
    vtkContourWidget,
    vtkOrientedGlyphContourRepresentation,
    vtkWidgetEvent
)
from vtkmodules.vtkRenderingCore import (
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Contour widget.'
    epilogue = '''
    The options -Shift or -Scale demonstrate how to override the left button press event.
    If either of these are set, you cannot change the shape of the circle.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-Shift', action='store_true',
                       help='Pressing the left button on a point will shift the whole circle.')
    group.add_argument('-Scale', action='store_true',
                       help='Pressing the left button on a point will scale the whole circle.')
    return parser.parse_args()


def main():
    colors = vtkNamedColors()
    # colors.SetColor('bkg', [0.1, 0.2, 0.4, 1.0])

    args = get_program_parameters()

    # Create the RenderWindow, Renderer and both Actors
    renderer = vtkRenderer(background=colors.GetColor3d('MidnightBlue'))
    render_window = vtkRenderWindow(size=(600, 600), window_name='ContourWidget')
    render_window.AddRenderer(renderer)

    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window

    # Override the default representation for the contour widget to customize its look.
    contour_rep = vtkOrientedGlyphContourRepresentation()
    contour_rep.lines_property.color = colors.GetColor3d('Red')

    contour_widget = vtkContourWidget(interactor=interactor, representation=contour_rep)
    contour_widget.On()

    if args.Shift:
        contour_widget.event_translator.RemoveTranslation(
            vtkCommand.LeftButtonPressEvent)
        contour_widget.event_translator.SetTranslation(
            vtkCommand.LeftButtonPressEvent,
            vtkWidgetEvent.Translate)
    if args.Scale:
        contour_widget.event_translator.RemoveTranslation(
            vtkCommand.LeftButtonPressEvent)
        contour_widget.event_translator.SetTranslation(
            vtkCommand.LeftButtonPressEvent,
            vtkWidgetEvent.Scale)

    # Generate a set of points arranged in a circle.
    points = vtkPoints()

    num_pts = 21
    for i in range(0, num_pts):
        angle = 2.0 * math.pi * i / 20.0
        points.InsertPoint(i, 0.1 * math.cos(angle),
                           0.1 * math.sin(angle), 0.0)
        # lines.InsertNextCell(i)
    vertex_indices = list(range(0, num_pts))
    # Set the last vertex to 0; this means the last line segment will join the
    # 19th point (vertices[19]) with the first one (vertices[0]), thus closing
    # the circle.
    vertex_indices.append(0)
    lines = vtkCellArray()
    lines.InsertNextCell(num_pts + 1, vertex_indices)

    pd = vtkPolyData(points=points, lines=lines)

    contour_widget.Initialize(pd, 1)
    contour_widget.Render()
    renderer.ResetCamera()
    render_window.Render()

    interactor.Initialize()
    interactor.Start()


if __name__ == '__main__':
    main()
