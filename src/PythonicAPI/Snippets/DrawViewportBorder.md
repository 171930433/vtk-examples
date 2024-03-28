### Description

Draw a border around a renderer's viewport.

To use the snippet, click the *Copy to clipboard* at the upper right of the code blocks.

### Implementation

``` Python
# from dataclasses import dataclass
# 
# from vtkmodules.vtkCommonCore import vtkPoints
# from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkPolyData, vtkPolyLine
# from vtkmodules.vtkFiltersCore import vtkAppendPolyData
# from vtkmodules.vtkRenderingCore import vtkActor2D, vtkPolyDataMapper2D, vtkRenderer
# from vtkmodules.vtkRenderingCore import vtkCoordinate


def draw_viewport_border(renderer, border, color=(0, 0, 0), line_width=2):
    """
    Draw a border around the viewport of a renderer.

    :param renderer: The renderer.
    :param border: The border to draw, it must be one of the constants in ViewPortBorder.
    :param color: The color.
    :param line_width: The line width of the border.
    :return:
    """

    def generate_border_lines(border_type):
        """
        Generate the lines for the border.

        :param border_type:  The border type to draw, it must be one of the constants in ViewPortBorder
        :return: The points and lines.
        """
        if border_type >= ViewPortBorder().NUMBER_OF_BORDER_TYPES:
            print('Not a valid border type.')
            return None

        # Points start at upper right and proceed anti-clockwise.
        pts = (
            (1, 1, 0),
            (0, 1, 0),
            (0, 0, 0),
            (1, 0, 0),
            (1, 1, 0),
        )
        vpb = ViewPortBorder()
        pt_orders = {
            vpb.TOP: (0, 1),
            vpb.LEFT: (1, 2),
            vpb.BOTTOM: (2, 3),
            vpb.RIGHT: (3, 4),
            vpb.LEFT_BOTTOM: (1, 2, 3),
            vpb.BOTTOM_RIGHT: (2, 3, 4),
            vpb.RIGHT_TOP: (3, 4, 1),
            vpb.RIGHT_TOP_LEFT: (3, 4, 1, 2),
            vpb.TOP_LEFT: (0, 1, 2),
            vpb.TOP_LEFT_BOTTOM: (0, 1, 2, 3),
            vpb.TOP_LEFT_BOTTOM_RIGHT: (0, 1, 2, 3, 4)
        }
        pt_order = pt_orders[border_type]
        number_of_points = len(pt_order)
        points = vtkPoints(number_of_points=number_of_points)
        i = 0
        for pt_id in pt_order:
            points.InsertPoint(i, *pts[pt_id])
            i += 1

        lines = vtkPolyLine()
        lines.point_ids.number_of_ids = number_of_points
        for i in range(0, number_of_points):
            lines.point_ids.id = (i, i)

        cells = vtkCellArray()
        cells.InsertNextCell(lines)

        # Make the polydata and return.
        return vtkPolyData(points=points, lines=cells)

    # Use normalized viewport coordinates since
    # they are independent of window size.
    coordinate = vtkCoordinate()
    coordinate.SetCoordinateSystemToNormalizedViewport()
    poly = vtkAppendPolyData()
    if border == ViewPortBorder().TOP_BOTTOM:
        (
            generate_border_lines(ViewPortBorder().TOP),
            generate_border_lines(ViewPortBorder().BOTTOM)
        ) >> poly
    elif border == ViewPortBorder().LEFT_RIGHT:
        (
            generate_border_lines(ViewPortBorder().LEFT),
            generate_border_lines(ViewPortBorder().RIGHT)
        ) >> poly
    else:
        generate_border_lines(border) >> poly

    mapper = vtkPolyDataMapper2D(transform_coordinate=coordinate)
    poly >> mapper
    actor = vtkActor2D(mapper=mapper)
    actor.property.color = color
    # Line width should be at least 2 to be visible at the extremes.
    actor.property.line_width = line_width

    renderer.AddViewProp(actor)


@dataclass(frozen=True)
class ViewPortBorder:
    TOP: int = 0
    LEFT: int = 1
    BOTTOM: int = 2
    RIGHT: int = 3
    LEFT_BOTTOM: int = 4
    BOTTOM_RIGHT: int = 5
    RIGHT_TOP: int = 6
    RIGHT_TOP_LEFT: int = 7
    TOP_LEFT: int = 8
    TOP_LEFT_BOTTOM: int = 9
    TOP_LEFT_BOTTOM_RIGHT: int = 10
    TOP_BOTTOM: int = 11
    LEFT_RIGHT: int = 12
    NUMBER_OF_BORDER_TYPES: int = 13

```

### Usage

``` Python

    draw_viewport_border(renderer, border=border, color=colors.GetColor3d('Yellow'), line_width=4)

```
