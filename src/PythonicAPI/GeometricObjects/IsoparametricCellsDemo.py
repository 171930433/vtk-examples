#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import (
    vtkBiQuadraticQuad,
    vtkBiQuadraticQuadraticHexahedron,
    vtkBiQuadraticQuadraticWedge,
    vtkBiQuadraticTriangle,
    vtkCubicLine,
    vtkQuadraticEdge,
    vtkQuadraticHexahedron,
    vtkQuadraticLinearQuad,
    vtkQuadraticLinearWedge,
    vtkQuadraticPolygon,
    vtkQuadraticPyramid,
    vtkQuadraticQuad,
    vtkQuadraticTetra,
    vtkQuadraticTriangle,
    vtkQuadraticWedge,
    vtkTriQuadraticHexahedron,
    vtkUnstructuredGrid
)
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkInteractionWidgets import (
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkActor2D,
    vtkDataSetMapper,
    vtkGlyph3DMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty
)
from vtkmodules.vtkRenderingLabel import vtkLabeledDataMapper


def main():
    colors = vtkNamedColors()

    # Set up the viewports.
    x_grid_dimensions = 4
    y_grid_dimensions = 4
    renderer_size = 240
    size = (renderer_size * x_grid_dimensions, renderer_size * y_grid_dimensions)
    viewports = list()
    for row in range(0, y_grid_dimensions):
        for col in range(0, x_grid_dimensions):
            # (xmin, ymin, xmax, ymax)
            viewports.append([float(col) / x_grid_dimensions,
                              float(y_grid_dimensions - (row + 1)) / y_grid_dimensions,
                              float(col + 1) / x_grid_dimensions,
                              float(y_grid_dimensions - row) / y_grid_dimensions])

    ren_win = vtkRenderWindow(size=size, window_name='IsoparametricCellsDemo')

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    u_grids, titles = get_unstructured_grids()

    # Create one sphere for all.
    sphere = vtkSphereSource(phi_resolution=21, theta_resolution=21, radius=0.08)

    # Create one text property for all.
    text_property = vtkTextProperty(color=colors.GetColor3d('LightGoldenrodYellow'), bold=True, italic=True,
                                    shadow=True, font_family_as_string='Courier',
                                    font_size=16, justification=TextProperty.Justification.VTK_TEXT_CENTERED)

    # Position text according to its length and centered in the viewport.
    text_positions = get_text_positions(titles, justification=TextProperty.Justification.VTK_TEXT_CENTERED)

    text_representations = list()
    text_actors = list()
    text_widgets = list()
    renderers = list()

    # Create and link the mappers actors and renderers together.
    for i in range(0, len(u_grids)):
        name = titles[i]
        print('Creating:', titles[i])

        renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'), viewport=viewports[i])

        # Create the text actor and representation.
        text_actors.append(
            vtkTextActor(input=name,
                         text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_NONE,
                         text_property=text_property))

        # Create the text representation. Used for positioning the text actor.
        text_representations.append(vtkTextRepresentation(enforce_normalized_viewport_bounds=True))
        text_representations[i].GetPositionCoordinate().value = text_positions[name]['p']
        text_representations[i].GetPosition2Coordinate().value = text_positions[name]['p2']

        # Create the text widget, setting the default renderer and interactor.
        text_widgets.append(
            vtkTextWidget(representation=text_representations[i], text_actor=text_actors[i],
                          default_renderer=renderer, interactor=iren, selectable=False))

        mapper = vtkDataSetMapper()
        u_grids[i] >> mapper

        actor = vtkActor(mapper=mapper)
        actor.property.color = colors.GetColor3d('Tomato')
        actor.property.edge_visibility = True
        actor.property.line_width = 3
        actor.property.opacity = 0.5

        # Label the points.
        label_mapper = vtkLabeledDataMapper()
        label_mapper.SetInputData(u_grids[i])
        label_actor = vtkActor2D()
        label_actor.SetMapper(label_mapper)

        # Glyph the points
        point_mapper = vtkGlyph3DMapper(input_data=u_grids[i], source_data=sphere.update().output, scaling=False,
                                        scalar_visibility=False)

        point_actor = vtkActor(mapper=point_mapper)
        point_actor.property.diffuse_color = colors.GetColor3d('Banana')
        point_actor.property.specular = 0.6
        point_actor.property.specular_color = (1.0, 1.0, 1.0)
        point_actor.property.specular_power = 100

        renderer.AddViewProp(actor)
        renderer.AddViewProp(label_actor)
        renderer.AddViewProp(point_actor)

        renderers.append(renderer)

        ren_win.AddRenderer(renderers[i])

    for row in range(0, y_grid_dimensions):
        for col in range(0, x_grid_dimensions):
            index = row * x_grid_dimensions + col

            if index > (len(renderers) - 1):
                # Add a renderer even if there is no actor.
                # This makes the render window background all the same color.
                ren = vtkRenderer(background=colors.GetColor3d('SlateGray'), viewport=viewports[index])
                ren_win.AddRenderer(ren)

                continue

            renderers[index].ResetCamera()
            renderers[index].active_camera.Azimuth(30)
            renderers[index].active_camera.Elevation(-30)
            renderers[index].ResetCameraClippingRange()

    for i in range(0, len(titles)):
        text_widgets[i].On()

    iren.Initialize()
    ren_win.Render()
    iren.Start()


# These functions return a vtkUnstructured grid corresponding to the object.

def make_unstructured_grid(a_cell):
    pcoords = a_cell.GetParametricCoords()
    for i in range(0, a_cell.number_of_points):
        a_cell.point_ids.SetId(i, i)
        a_cell.points.SetPoint(i, (pcoords[3 * i]), (pcoords[3 * i + 1]), (pcoords[3 * i + 2]))

    ug = vtkUnstructuredGrid(points=a_cell.points)
    ug.InsertNextCell(a_cell.cell_type, a_cell.point_ids)
    return ug


def make_quadratic_polygon():
    quadratic_polygon = vtkQuadraticPolygon()

    quadratic_polygon.point_ids.SetNumberOfIds(8)
    quadratic_polygon.point_ids.SetId(0, 0)
    quadratic_polygon.point_ids.SetId(1, 1)
    quadratic_polygon.point_ids.SetId(2, 2)
    quadratic_polygon.point_ids.SetId(3, 3)
    quadratic_polygon.point_ids.SetId(4, 4)
    quadratic_polygon.point_ids.SetId(5, 5)
    quadratic_polygon.point_ids.SetId(6, 6)
    quadratic_polygon.point_ids.SetId(7, 7)

    quadratic_polygon.points.SetNumberOfPoints(8)
    quadratic_polygon.points.SetPoint(0, 0.0, 0.0, 0.0)
    quadratic_polygon.points.SetPoint(1, 2.0, 0.0, 0.0)
    quadratic_polygon.points.SetPoint(2, 2.0, 2.0, 0.0)
    quadratic_polygon.points.SetPoint(3, 0.0, 2.0, 0.0)
    quadratic_polygon.points.SetPoint(4, 1.0, 0.0, 0.0)
    quadratic_polygon.points.SetPoint(5, 2.0, 1.0, 0.0)
    quadratic_polygon.points.SetPoint(6, 1.0, 2.0, 0.0)
    quadratic_polygon.points.SetPoint(7, 0.0, 1.0, 0.0)
    quadratic_polygon.points.SetPoint(5, 3.0, 1.0, 0.0)

    ug = vtkUnstructuredGrid(points=quadratic_polygon.points)
    ug.InsertNextCell(quadratic_polygon.cell_type, quadratic_polygon.point_ids)
    return ug


def get_unstructured_grids():
    u_grids = list()
    titles = list()

    u_grids.append(make_unstructured_grid(
        vtkQuadraticEdge()))
    titles.append('VTK_QUADRATIC_EDGE (= 21)')

    u_grids.append(make_unstructured_grid(
        vtkQuadraticTriangle()))
    titles.append('VTK_QUADRATIC_TRIANGLE (= 22)')

    u_grids.append(make_unstructured_grid(
        vtkQuadraticQuad()))
    titles.append('VTK_QUADRATIC_QUAD (= 23)')

    u_grids.append(make_quadratic_polygon())
    titles.append('VTK_QUADRATIC_POLYGON (= 36)')

    u_grids.append(make_unstructured_grid(
        vtkQuadraticTetra()))
    titles.append('VTK_QUADRATIC_TETRA (= 24)')

    u_grids.append(make_unstructured_grid(
        vtkQuadraticHexahedron()))
    titles.append('VTK_QUADRATIC_HEXAHEDRON (= 25)')

    u_grids.append(make_unstructured_grid(
        vtkQuadraticWedge()))
    titles.append('VTK_QUADRATIC_WEDGE (= 26)')

    u_grids.append(make_unstructured_grid(
        vtkQuadraticPyramid()))
    titles.append('VTK_QUADRATIC_PYRAMID (= 27)')

    u_grids.append(make_unstructured_grid(
        vtkBiQuadraticQuad()))
    titles.append('VTK_BIQUADRATIC_QUAD (= 28)')

    u_grids.append(make_unstructured_grid(
        vtkTriQuadraticHexahedron()))
    titles.append('VTK_TRIQUADRATIC_HEXAHEDRON (= 29)')

    u_grids.append(make_unstructured_grid(
        vtkQuadraticLinearQuad()))
    titles.append('VTK_QUADRATIC_LINEAR_QUAD (= 30)')

    u_grids.append(make_unstructured_grid(
        vtkQuadraticLinearWedge()))
    titles.append('VTK_QUADRATIC_LINEAR_WEDGE (= 31)')

    u_grids.append(make_unstructured_grid(
        vtkBiQuadraticQuadraticWedge()))
    titles.append('VTK_BIQUADRATIC_QUADRATIC_WEDGE (= 32)')

    u_grids.append(make_unstructured_grid(
        vtkBiQuadraticQuadraticHexahedron()))
    titles.append('VTK_BIQUADRATIC_QUADRATIC_HEXAHEDRON (= 33)')

    u_grids.append(make_unstructured_grid(
        vtkBiQuadraticTriangle()))
    titles.append('VTK_BIQUADRATIC_TRIANGLE (= 34)')

    u_grids.append(make_unstructured_grid(
        vtkCubicLine()))
    titles.append('VTK_CUBIC_LINE (= 35)')

    return u_grids, titles


def get_text_positions(names, justification=0, vertical_justification=0, width=0.96, height=0.1):
    """
    Get viewport positioning information for a list of names.

    :param names: The list of names.
    :param justification: Horizontal justification of the text, default is left.
    :param vertical_justification: Vertical justification of the text, default is bottom.
    :param width: Width of the bounding_box of the text in screen coordinates.
    :param height: Height of the bounding_box of the text in screen coordinates.
    :return: A list of positioning information.
    """
    # The gap between the left or right edge of the screen and the text.
    dx = 0.02
    width = abs(width)
    if width > 0.96:
        width = 0.96

    y0 = 0.01
    height = abs(height)
    if height > 0.9:
        height = 0.9
    dy = height
    if vertical_justification == TextProperty.VerticalJustification.VTK_TEXT_TOP:
        y0 = 1.0 - (dy + y0)
        dy = height
    if vertical_justification == TextProperty.VerticalJustification.VTK_TEXT_CENTERED:
        y0 = 0.5 - (dy / 2.0 + y0)
        dy = height

    name_len_min = 0
    name_len_max = 0
    first = True
    for k in names:
        sz = len(k)
        if first:
            name_len_min = name_len_max = sz
            first = False
        else:
            name_len_min = min(name_len_min, sz)
            name_len_max = max(name_len_max, sz)
    text_positions = dict()
    for k in names:
        sz = len(k)
        delta_sz = width * sz / name_len_max
        if delta_sz > width:
            delta_sz = width

        if justification == TextProperty.Justification.VTK_TEXT_CENTERED:
            x0 = 0.5 - delta_sz / 2.0
        elif justification == TextProperty.Justification.VTK_TEXT_RIGHT:
            x0 = 1.0 - dx - delta_sz
        else:
            # Default is left justification.
            x0 = dx

        # For debugging!
        # print(
        #     f'{k:16s}: (x0, y0) = ({x0:3.2f}, {y0:3.2f}), (x1, y1) = ({x0 + delta_sz:3.2f}, {y0 + dy:3.2f})'
        #     f', width={delta_sz:3.2f}, height={dy:3.2f}')
        text_positions[k] = {'p': [x0, y0, 0], 'p2': [delta_sz, dy, 0]}

    return text_positions


@dataclass(frozen=True)
class TextProperty:
    @dataclass(frozen=True)
    class Justification:
        VTK_TEXT_LEFT: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_RIGHT: int = 2

    @dataclass(frozen=True)
    class VerticalJustification:
        VTK_TEXT_BOTTOM: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_TOP: int = 2


if __name__ == '__main__':
    main()
