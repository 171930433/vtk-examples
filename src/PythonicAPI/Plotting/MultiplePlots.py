#!/usr/bin/env python3

import math

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingContextOpenGL2
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkChartsCore import (
    vtkAxis,
    vtkChart,
    vtkChartXY,
    vtkPlotPoints
)
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkFloatArray
from vtkmodules.vtkCommonDataModel import vtkTable
from vtkmodules.vtkRenderingContext2D import (
    vtkContextActor,
    vtkContextScene
)
from vtkmodules.vtkRenderingCore import (
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Set up the viewports.
    grid_dimensions_x = 2
    grid_dimensions_y = 1
    renderer_sz_x = 320
    renderer_sz_y = 240
    size = (renderer_sz_x * grid_dimensions_x, renderer_sz_y * grid_dimensions_y)

    # The renderer window and interactor.
    renwin = vtkRenderWindow(size=size, window_name='MultiplePlots')
    iren = vtkRenderWindowInteractor()
    iren.render_window = renwin

    viewports = list()
    for row in range(0, grid_dimensions_y):
        for col in range(0, grid_dimensions_x):
            # index = row * grid_dimensions_x + col

            # (xmin, ymin, xmax, ymax)
            viewports.append([float(col) / grid_dimensions_x,
                              float(grid_dimensions_y - (row + 1)) / grid_dimensions_y,
                              float(col + 1) / grid_dimensions_x,
                              float(grid_dimensions_y - row) / grid_dimensions_y])

    # Link the renderers to the viewports.
    left_renderer = vtkRenderer(background=colors.GetColor3d('AliceBlue'), viewport=viewports[0])
    renwin.AddRenderer(left_renderer)

    right_renderer = vtkRenderer(background=colors.GetColor3d('Lavender'), viewport=viewports[1])
    renwin.AddRenderer(right_renderer)

    # Create the charts.
    left_chart = vtkChartXY(title='Cosine')
    left_chart.background_brush.color_f = colors.GetColor3d('MistyRose')
    left_chart.background_brush.opacity_f = 0.4

    x_axis = left_chart.GetAxis(vtkAxis.BOTTOM)
    x_axis.grid_pen.color = colors.GetColor4ub("LightGrey")
    x_axis.title = 'x'
    y_axis = left_chart.GetAxis(vtkAxis.LEFT)
    y_axis.grid_pen.color = colors.GetColor4ub("LightGrey")
    y_axis.title = 'cos(x)'

    left_chart_scene = vtkContextScene()
    left_chart_actor = vtkContextActor()

    left_chart_scene.AddItem(left_chart)
    left_chart_actor.scene = left_chart_scene

    left_renderer.AddActor(left_chart_actor)
    left_chart_scene.renderer = left_renderer

    right_chart = vtkChartXY(title='Sine')
    right_chart.background_brush.color_f = colors.GetColor3d('Thistle')
    right_chart.background_brush.opacity_f = 0.4

    x_axis = right_chart.GetAxis(vtkAxis.BOTTOM)
    x_axis.grid_pen.color = colors.GetColor4ub("LightCyan")
    x_axis.title = 'x'
    y_axis = right_chart.GetAxis(vtkAxis.LEFT)
    y_axis.grid_pen.color = colors.GetColor4ub("LightCyan")
    y_axis.title = 'sin(x)'

    right_chart_scene = vtkContextScene()
    right_chart_actor = vtkContextActor()

    right_chart_scene.AddItem(right_chart)
    right_chart_actor.scene = right_chart_scene

    right_renderer.AddActor(right_chart_actor)
    right_chart_scene.renderer = right_renderer

    # Create the data.
    table = vtkTable()
    array_x = vtkFloatArray(name='X Axis')
    table.AddColumn(array_x)

    array_cos = vtkFloatArray(name='Cosine')
    table.AddColumn(array_cos)

    array_sin = vtkFloatArray(name='Sine')
    table.AddColumn(array_sin)

    # Fill in the table with some example values.
    num_points = 40
    inc = 7.5 / (num_points - 1.0)
    table.number_of_rows = num_points
    for i in range(num_points):
        table.SetValue(i, 0, i * inc)
        table.SetValue(i, 1, math.cos(i * inc))
        table.SetValue(i, 2, math.sin(i * inc))

    points = left_chart.AddPlot(vtkChart.POINTS)
    points.input_data = (table, 0, 1)
    points.color = tuple(colors.GetColor4ub('Black'))
    points.width = 1.0
    points.marker_style = vtkPlotPoints.CROSS

    points = right_chart.AddPlot(vtkChart.POINTS)
    points.input_data = (table, 0, 2)
    points.color = tuple(colors.GetColor4ub('Black'))
    points.width = 1.0
    points.marker_style = vtkPlotPoints.PLUS

    renwin.Render()
    iren.Initialize()
    iren.Start()


if __name__ == '__main__':
    main()
