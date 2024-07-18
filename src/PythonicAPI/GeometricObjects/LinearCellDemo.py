# !/usr/bin/env python3

from collections import namedtuple
from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import (
    VTK_TETRA,
    vtkPolyData,
    vtkCellArray,
    vtkHexagonalPrism,
    vtkHexahedron,
    vtkLine,
    vtkPentagonalPrism,
    vtkPixel,
    vtkPolyLine,
    vtkPolyVertex,
    vtkPolygon,
    vtkPyramid,
    vtkQuad,
    vtkTetra,
    vtkTriangle,
    vtkTriangleStrip,
    vtkUnstructuredGrid,
    vtkVertex,
    vtkVoxel,
    vtkWedge
)
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
from vtkmodules.vtkFiltersSources import (
    vtkCubeSource,
    vtkSphereSource
)
from vtkmodules.vtkInteractionWidgets import (
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkActor2D,
    vtkCoordinate,
    vtkDataSetMapper,
    vtkGlyph3DMapper,
    vtkPolyDataMapper,
    vtkPolyDataMapper2D,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty,
)
from vtkmodules.vtkRenderingLabel import vtkLabeledDataMapper


def get_program_parameters():
    import argparse
    description = 'Demonstrate the linear cell types found in VTK.'
    epilogue = '''
     The numbers define the ordering of the points making the cell.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('-w', '--wireframe', action='store_true',
                        help='Render a wireframe.')
    group1.add_argument('-b', '--backface', action='store_true',
                        help='Display the back face in a different colour.')
    args = parser.parse_args()
    return args.wireframe, args.backface


def main():
    wireframe_on, backface_on = get_program_parameters()

    colors = vtkNamedColors()

    # Create one sphere for all.
    sphere = vtkSphereSource(phi_resolution=21, theta_resolution=21, radius=0.04)

    cells = get_cell_orientation()
    # needs_a_tile = ('VTK_TETRA (=10)',
    #                 'VTK_VOXEL (=11)',
    #                 'VTK_HEXAHEDRON (=12)',
    #                 'VTK_WEDGE (=13)',
    #                 'VTK_PYRAMID (=14)',
    #                 'VTK_PENTAGONAL_PRISM (=15)',
    #                 'VTK_HEXAGONAL_PRISM (=16)',
    #                 )

    # Set up the viewports.
    grid_column_dimensions = 4
    grid_row_dimensions = 4
    renderer_size = 300
    size = (grid_column_dimensions * renderer_size, grid_row_dimensions * renderer_size)

    keys = list(cells.keys())

    viewports = dict()
    VP_Params = namedtuple('VP_Params', ['viewport', 'border'])
    last_col = False
    last_row = False
    blank = len(cells)

    for row in range(0, grid_row_dimensions):
        if row == grid_row_dimensions - 1:
            last_row = True
        for col in range(0, grid_column_dimensions):
            if col == grid_column_dimensions - 1:
                last_col = True
            index = row * grid_column_dimensions + col
            # Set the renderer's viewport dimensions (xmin, ymin, xmax, ymax) within the render window.
            # Note that for the Y values, we need to subtract the row index from grid_rows
            #  because the viewport Y axis points upwards, and we want to draw the grid from top to down.
            viewport = (float(col) / grid_column_dimensions,
                        float(grid_row_dimensions - (row + 1)) / grid_row_dimensions,
                        float(col + 1) / grid_column_dimensions,
                        float(grid_row_dimensions - row) / grid_row_dimensions)

            if last_row and last_col:
                border = ViewPort.Border.TOP_LEFT_BOTTOM_RIGHT
                last_row = False
                last_col = False
            elif last_col:
                border = ViewPort.Border.RIGHT_TOP_LEFT
                last_col = False
            elif last_row:
                border = ViewPort.Border.TOP_LEFT_BOTTOM
            else:
                border = ViewPort.Border.TOP_LEFT
            vp_params = VP_Params(viewport, border)
            if index < blank:
                viewports[keys[index]] = vp_params
            else:
                viewports[index] = vp_params

    # Create one text property for all.
    text_property = vtkTextProperty(color=colors.GetColor3d('Black'),
                                    bold=True, italic=False, shadow=False,
                                    font_family_as_string='Courier',
                                    font_size=int(renderer_size / 18),
                                    justification=TextProperty.Justification.VTK_TEXT_CENTERED)

    label_property = vtkTextProperty(color=colors.GetColor3d('FireBrick'),
                                     bold=True, italic=False, shadow=False,
                                     font_family_as_string='Courier',
                                     font_size=int(renderer_size / 12),
                                     justification=TextProperty.Justification.VTK_TEXT_CENTERED)

    back_property = vtkProperty(color=colors.GetColor3d('Coral'))

    # Position text according to its length and centered in the viewport.
    text_positions = get_text_positions(keys,
                                        justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                        vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_BOTTOM,
                                        width=0.85, height=0.1)

    ren_win = vtkRenderWindow(size=size, window_name='LinearCellDemo')
    ren_win.SetWindowName('LinearCellDemo')
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win
    iren.interactor_style.SetCurrentStyleToTrackballCamera()

    renderers = dict()
    text_representations = list()
    text_actors = list()
    text_widgets = list()

    # Create and link the mappers, actors and renderers together.
    for key in keys:
        print('Creating:', key)

        mapper = vtkDataSetMapper()
        cells[key][0] >> mapper
        actor = vtkActor(mapper=mapper)
        if wireframe_on:
            actor.property.representation = Property.Representation.VTK_WIREFRAME
            actor.property.line_width = 2
            actor.property.opacity = 1
            actor.property.color = colors.GetColor3d('Black')
        else:
            actor.property.EdgeVisibilityOn()
            actor.property.line_width = 3
            actor.property.color = colors.GetColor3d('Snow')
            if backface_on:
                actor.property.opacity = 0.4
                actor.SetBackfaceProperty(back_property)
                back_property.opacity = 0.6
            else:
                actor.property.opacity = 0.8

        # Label the points.
        label_mapper = vtkLabeledDataMapper()
        cells[key][0] >> label_mapper
        label_mapper.label_text_property = label_property
        label_actor = vtkActor2D(mapper=label_mapper)

        # Glyph the points.
        point_mapper = vtkGlyph3DMapper(scaling=True, scalar_visibility=False,
                                        source_connection=sphere.output_port)
        cells[key][0] >> point_mapper
        point_actor = vtkActor(mapper=point_mapper)
        point_actor.property.color = colors.GetColor3d('Yellow')
        point_actor.property.specular = 1.0
        point_actor.property.specular_color = colors.GetColor3d('White')
        point_actor.property.specular_power = 100

        viewport = viewports[key].viewport
        border = viewports[key].border
        renderer = vtkRenderer(background=colors.GetColor3d('CornflowerBlue'), viewport=viewport)
        draw_viewport_border(renderer, border=border, color=colors.GetColor3d('Yellow'), line_width=4)

        renderer.AddActor(actor)
        renderer.AddActor(label_actor)
        renderer.AddActor(point_actor)
        # # Add a plane.
        # if key in needs_a_tile:
        #     tile_actor = make_tile(cells[key][0].GetBounds(), expansion_factor=0.1, thickness_ratio=0.05)
        #     tile_actor.GetProperty().SetColor(colors.GetColor3d('SpringGreen'))
        #     tile_actor.GetProperty().SetOpacity(0.3)
        #     renderer.AddActor(tile_actor)

        # Create the text actor and representation.
        text_actor = vtkTextActor(input=key,
                                  text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_NONE,
                                  text_property=text_property)

        # Create the text representation. Used for positioning the text actor.
        text_representation = vtkTextRepresentation(enforce_normalized_viewport_bounds=True)
        text_representation.GetPositionCoordinate().value = text_positions[key]['p']
        text_representation.GetPosition2Coordinate().value = text_positions[key]['p2']

        # Create the text widget, setting the default renderer and interactor.
        text_widget = vtkTextWidget(representation=text_representation, text_actor=text_actor,
                                    default_renderer=renderer, interactor=iren, selectable=False)

        text_actors.append(text_actor)
        text_representations.append(text_representation)
        text_widgets.append(text_widget)

        renderer.ResetCamera()
        renderer.active_camera.Dolly(cells[key][1].zoom)
        renderer.active_camera.Azimuth(cells[key][1].azimuth)
        renderer.active_camera.Elevation(cells[key][1].elevation)
        renderer.ResetCameraClippingRange()

        renderers[key] = renderer

        ren_win.AddRenderer(renderers[key])

    for i in range(blank, grid_column_dimensions * grid_row_dimensions):
        viewport = viewports[i].viewport
        border = viewports[i].border
        renderer = vtkRenderer(background=colors.GetColor3d('CornflowerBlue'), viewport=viewport)
        draw_viewport_border(renderer, border=border, color=colors.GetColor3d('Yellow'), line_width=4)
        ren_win.AddRenderer(renderer)

    for i in range(0, len(text_widgets)):
        text_widgets[i].On()

    ren_win.Render()
    iren.Initialize()
    iren.Start()


def get_cell_orientation():
    """
    Get the linear cell names, the cells and initial orientations.

    :return: The linear cell names, the cells and initial orientations
    """

    def make_orientation(azimuth: float = 0, elevation: float = 0, zoom: float = 1.0):
        return Orientation(azimuth, elevation, zoom)

    return {
        'VTK_VERTEX (=1)': (make_vertex(), make_orientation(30, -30, 0.1)),
        'VTK_POLY_VERTEX (=2)': (make_poly_vertex(), make_orientation(30, -30, 0.8)),
        'VTK_LINE (=3)': (make_line(), make_orientation(30, -30, 0.4)),
        'VTK_POLY_LINE (=4)': (make_polyline(), make_orientation(30, -30, 1.0)),
        'VTK_TRIANGLE (=5)': (make_polyline(), make_orientation(30, -30, 0.7)),
        'VTK_TRIANGLE_STRIP (=6)': (make_triangle_strip(), make_orientation(30, -30, 1.1)),
        'VTK_POLYGON (=7)': (make_polygon(), make_orientation(0, -45, 1.0)),
        'VTK_PIXEL (=8)': (make_pixel(), make_orientation(0, -45, 1.0)),
        'VTK_QUAD (=9)': (make_quad(), make_orientation(0, -45, 0)),
        'VTK_TETRA (=10)': (make_tetra(), make_orientation(0, -45, 0.95)),
        'VTK_VOXEL (=11)': (make_voxel(), make_orientation(-22.5, 15, 0.95)),
        'VTK_HEXAHEDRON (=12)': (make_hexahedron(), make_orientation(-22.5, 15, 0.95)),
        'VTK_WEDGE (=13)': (make_wedge(), make_orientation(-45, 15, 1.0)),
        'VTK_PYRAMID (=14)': (make_pyramid(), make_orientation(0, -30, 1.0)),
        # 'VTK_PENTAGONAL_PRISM (=15)': (make_pentagonal_prism(), make_orientation(-22.5, 15, 0.95)),
        'VTK_PENTAGONAL_PRISM (=15)': (make_pentagonal_prism(), make_orientation(-30, 15, 0.95)),
        'VTK_HEXAGONAL_PRISM (=16)': (make_hexagonal_prism(), make_orientation(-30, 15, 0.95)),
    }


@dataclass(frozen=True)
class Orientation:
    azimuth: float
    elevation: float
    zoom: float


# These functions return a vtkUnstructured grid corresponding to the object.

def make_vertex():
    # A vertex is a cell that represents a 3D point
    number_of_vertices = 1

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)

    vertex = vtkVertex()
    for i in range(0, number_of_vertices):
        vertex.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid(points=points)
    ug.InsertNextCell(vertex.GetCellType(), vertex.GetPointIds())

    return ug


def make_poly_vertex():
    # A polyvertex is a cell representing a set of 0D vertices
    number_of_vertices = 6

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, 0, 0)
    points.InsertNextPoint(0, 1, 0)
    points.InsertNextPoint(0, 0, 1)
    points.InsertNextPoint(1, 0, 0.4)
    points.InsertNextPoint(0, 1, 0.6)

    poly_vertex = vtkPolyVertex()
    poly_vertex.point_ids.SetNumberOfIds(number_of_vertices)

    for i in range(0, number_of_vertices):
        poly_vertex.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid(points=points)
    ug.InsertNextCell(poly_vertex.GetCellType(), poly_vertex.GetPointIds())

    return ug


def make_line():
    # A line is a cell that represents a 1D point
    number_of_vertices = 2

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(0.5, 0.5, 0)

    line = vtkLine()
    for i in range(0, number_of_vertices):
        line.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid(points=points)
    ug.InsertNextCell(line.GetCellType(), line.GetPointIds())

    return ug


def make_polyline():
    # A polyline is a cell that represents a set of 1D lines
    number_of_vertices = 5

    points = vtkPoints()
    points.InsertNextPoint(0, 0.5, 0)
    points.InsertNextPoint(0.5, 0, 0)
    points.InsertNextPoint(1, 0.3, 0)
    points.InsertNextPoint(1.5, 0.4, 0)
    points.InsertNextPoint(2.0, 0.4, 0)

    polyline = vtkPolyLine()
    polyline.point_ids.SetNumberOfIds(number_of_vertices)

    for i in range(0, number_of_vertices):
        polyline.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid(points=points)
    ug.InsertNextCell(polyline.GetCellType(), polyline.GetPointIds())

    return ug


def make_triangle():
    # A triangle is a cell that represents a 1D point
    number_of_vertices = 3

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(0.5, 0.5, 0)
    points.InsertNextPoint(.2, 1, 0)

    triangle = vtkTriangle()
    for i in range(0, number_of_vertices):
        triangle.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid(points=points)
    ug.InsertNextCell(triangle.GetCellType(), triangle.GetPointIds())

    return ug


def make_triangle_strip():
    # A triangle is a cell that represents a triangle strip
    number_of_vertices = 10

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, -.1, 0)
    points.InsertNextPoint(0.5, 1, 0)
    points.InsertNextPoint(2.0, -0.1, 0)
    points.InsertNextPoint(1.5, 0.8, 0)
    points.InsertNextPoint(3.0, 0, 0)
    points.InsertNextPoint(2.5, 0.9, 0)
    points.InsertNextPoint(4.0, -0.2, 0)
    points.InsertNextPoint(3.5, 0.8, 0)
    points.InsertNextPoint(4.5, 1.1, 0)

    trianglestrip = vtkTriangleStrip()
    trianglestrip.point_ids.SetNumberOfIds(number_of_vertices)
    for i in range(0, number_of_vertices):
        trianglestrip.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid(points=points)
    ug.InsertNextCell(trianglestrip.GetCellType(), trianglestrip.GetPointIds())

    return ug


def make_polygon():
    # A polygon is a cell that represents a polygon
    number_of_vertices = 6

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, -0.1, 0)
    points.InsertNextPoint(0.8, 0.5, 0)
    points.InsertNextPoint(1, 1, 0)
    points.InsertNextPoint(0.6, 1.2, 0)
    points.InsertNextPoint(0, 0.8, 0)

    polygon = vtkPolygon()
    polygon.point_ids.SetNumberOfIds(number_of_vertices)
    for i in range(0, number_of_vertices):
        polygon.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid(points=points)
    ug.InsertNextCell(polygon.GetCellType(), polygon.GetPointIds())

    return ug


def make_pixel():
    # A pixel is a cell that represents a pixel
    pixel = vtkPixel()
    pixel.points.SetPoint(0, 0, 0, 0)
    pixel.points.SetPoint(1, 1, 0, 0)
    pixel.points.SetPoint(2, 0, 1, 0)
    pixel.points.SetPoint(3, 1, 1, 0)

    pixel.point_ids.SetId(0, 0)
    pixel.point_ids.SetId(1, 1)
    pixel.point_ids.SetId(2, 2)
    pixel.point_ids.SetId(3, 3)

    ug = vtkUnstructuredGrid(points=pixel.points)
    ug.InsertNextCell(pixel.GetCellType(), pixel.GetPointIds())

    return ug


def make_quad():
    # A quad is a cell that represents a quad
    quad = vtkQuad()
    quad.points.SetPoint(0, 0, 0, 0)
    quad.points.SetPoint(1, 1, 0, 0)
    quad.points.SetPoint(2, 1, 1, 0)
    quad.points.SetPoint(3, 0, 1, 0)

    quad.point_ids.SetId(0, 0)
    quad.point_ids.SetId(1, 1)
    quad.point_ids.SetId(2, 2)
    quad.point_ids.SetId(3, 3)

    ug = vtkUnstructuredGrid(points=quad.points)
    ug.InsertNextCell(quad.cell_type, quad.point_ids)

    return ug


def make_tetra():
    # Make a tetrahedron.
    number_of_vertices = 4

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, 0, 0)
    points.InsertNextPoint(1, 1, 0)
    points.InsertNextPoint(0, 1, 1)

    tetra = vtkTetra()
    for i in range(0, number_of_vertices):
        tetra.point_ids.SetId(i, i)

    cell_array = vtkCellArray()
    cell_array.InsertNextCell(tetra)

    ug = vtkUnstructuredGrid(points=points)
    ug.SetCells(VTK_TETRA, cell_array)

    return ug


def make_voxel():
    # A voxel is a representation of a regular grid in 3-D space.
    number_of_vertices = 8

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, 0, 0)
    points.InsertNextPoint(0, 1, 0)
    points.InsertNextPoint(1, 1, 0)
    points.InsertNextPoint(0, 0, 1)
    points.InsertNextPoint(1, 0, 1)
    points.InsertNextPoint(0, 1, 1)
    points.InsertNextPoint(1, 1, 1)

    voxel = vtkVoxel()
    for i in range(0, number_of_vertices):
        voxel.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid(points=points)
    ug.InsertNextCell(voxel.cell_type, voxel.point_ids)

    return ug


def make_hexahedron():
    # A regular hexagon (cube) with all faces square and three squares around
    # each vertex is created below.

    # Set up the coordinates of eight points
    # (the two faces must be in counter-clockwise
    # order as viewed from the outside).

    number_of_vertices = 8

    # Create the points
    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, 0, 0)
    points.InsertNextPoint(1, 1, 0)
    points.InsertNextPoint(0, 1, 0)
    points.InsertNextPoint(0, 0, 1)
    points.InsertNextPoint(1, 0, 1)
    points.InsertNextPoint(1, 1, 1)
    points.InsertNextPoint(0, 1, 1)

    # Create a hexahedron from the points
    hexhedr = vtkHexahedron()
    for i in range(0, number_of_vertices):
        hexhedr.point_ids.SetId(i, i)

    # Add the points and hexahedron to an unstructured grid
    ug = vtkUnstructuredGrid(points=points)
    ug.InsertNextCell(hexhedr.cell_type, hexhedr.point_ids)

    return ug


def make_wedge():
    # A wedge consists of two triangular ends and three rectangular faces.

    number_of_vertices = 6

    points = vtkPoints()

    # Original Points.
    points.InsertNextPoint(0, 1, 0)
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(0, 0.5, 0.5)
    points.InsertNextPoint(1, 1, 0)
    points.InsertNextPoint(1, 0.0, 0.0)
    points.InsertNextPoint(1, 0.5, 0.5)

    # RotateX(-90), Translate(0,-1,0).
    # points.InsertNextPoint(0.0, 0.0, 0.0)
    # points.InsertNextPoint(0.0,0 , 1.0)
    # points.InsertNextPoint(0.0, 0.5, 0.5)
    # points.InsertNextPoint(1.0, 0.0, 0.0)
    # points.InsertNextPoint(1.0, 0, 1.0)
    # points.InsertNextPoint(1.0, 0.5, 0.5)

    wedge = vtkWedge()
    for i in range(0, number_of_vertices):
        wedge.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid(points=points)
    ug.InsertNextCell(wedge.cell_type, wedge.point_ids)

    # pd = vtkPolyData(points=points)
    # t = vtkTransform()
    # # t.Translate(1,1,1)
    # t.RotateX(-90)
    # t.Translate(0,-1,0)
    # tf = vtkTransformFilter(transform=t)
    # (pd >> tf).update()
    # pts = tf.output.GetPoints()
    # for i in range(0, pts.number_of_points):
    #     print(f'points.InsertNextPoint{pts.GetPoint(i)}')

    return ug


def make_pyramid():
    # Make a regular square pyramid.
    number_of_vertices = 5

    points = vtkPoints()

    # Original points.
    p0 = [1.0, 1.0, 0.0]
    p1 = [-1.0, 1.0, 0.0]
    p2 = [-1.0, -1.0, 0.0]
    p3 = [1.0, -1.0, 0.0]
    p4 = [0.0, 0.0, 1.0]

    # # RotateX(-90)
    # p0 = (1.0, 0, -1.0)
    # p1 = (-1.0, 0, -1.0)
    # p2 = (-1.0, 0, 1.0)
    # p3 = (1.0, 0, 1.0)
    # p4 = (0.0, 2.0, 0)

    points.InsertNextPoint(p0)
    points.InsertNextPoint(p1)
    points.InsertNextPoint(p2)
    points.InsertNextPoint(p3)
    points.InsertNextPoint(p4)

    pyramid = vtkPyramid()
    for i in range(0, number_of_vertices):
        pyramid.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid(points=points)
    ug.InsertNextCell(pyramid.cell_type, pyramid.point_ids)

    # pd = vtkPolyData(points=points)
    # t = vtkTransform()
    # t.RotateX(-90)
    # t.Translate(0,0,0)
    # tf = vtkTransformFilter(transform=t)
    # (pd >> tf).update()
    # pts = tf.output.GetPoints()
    # for i in range(0, pts.number_of_points):
    #     print(f'p{i} = {pts.GetPoint(i)}')

    return ug


def make_pentagonal_prism():
    pentagonal_prism = vtkPentagonalPrism()

    pentagonal_prism.point_ids.SetId(0, 0)
    pentagonal_prism.point_ids.SetId(1, 1)
    pentagonal_prism.point_ids.SetId(2, 2)
    pentagonal_prism.point_ids.SetId(3, 3)
    pentagonal_prism.point_ids.SetId(4, 4)
    pentagonal_prism.point_ids.SetId(5, 5)
    pentagonal_prism.point_ids.SetId(6, 6)
    pentagonal_prism.point_ids.SetId(7, 7)
    pentagonal_prism.point_ids.SetId(8, 8)
    pentagonal_prism.point_ids.SetId(9, 9)

    scale = 2.0
    pentagonal_prism.points.SetPoint(0, 11 / scale, 10 / scale, 10 / scale)
    pentagonal_prism.points.SetPoint(1, 13 / scale, 10 / scale, 10 / scale)
    pentagonal_prism.points.SetPoint(2, 14 / scale, 12 / scale, 10 / scale)
    pentagonal_prism.points.SetPoint(3, 12 / scale, 14 / scale, 10 / scale)
    pentagonal_prism.points.SetPoint(4, 10 / scale, 12 / scale, 10 / scale)
    pentagonal_prism.points.SetPoint(5, 11 / scale, 10 / scale, 14 / scale)
    pentagonal_prism.points.SetPoint(6, 13 / scale, 10 / scale, 14 / scale)
    pentagonal_prism.points.SetPoint(7, 14 / scale, 12 / scale, 14 / scale)
    pentagonal_prism.points.SetPoint(8, 12 / scale, 14 / scale, 14 / scale)
    pentagonal_prism.points.SetPoint(9, 10 / scale, 12 / scale, 14 / scale)

    ug = vtkUnstructuredGrid(points=pentagonal_prism.points)
    ug.InsertNextCell(pentagonal_prism.cell_type, pentagonal_prism.point_ids)

    return ug


def make_hexagonal_prism():
    hexagonal_prism = vtkHexagonalPrism()
    hexagonal_prism.point_ids.SetId(0, 0)
    hexagonal_prism.point_ids.SetId(1, 1)
    hexagonal_prism.point_ids.SetId(2, 2)
    hexagonal_prism.point_ids.SetId(3, 3)
    hexagonal_prism.point_ids.SetId(4, 4)
    hexagonal_prism.point_ids.SetId(5, 5)
    hexagonal_prism.point_ids.SetId(6, 6)
    hexagonal_prism.point_ids.SetId(7, 7)
    hexagonal_prism.point_ids.SetId(8, 8)
    hexagonal_prism.point_ids.SetId(9, 9)
    hexagonal_prism.point_ids.SetId(10, 10)
    hexagonal_prism.point_ids.SetId(11, 11)

    scale = 2.0
    hexagonal_prism.points.SetPoint(0, 11 / scale, 10 / scale, 10 / scale)
    hexagonal_prism.points.SetPoint(1, 13 / scale, 10 / scale, 10 / scale)
    hexagonal_prism.points.SetPoint(2, 14 / scale, 12 / scale, 10 / scale)
    hexagonal_prism.points.SetPoint(3, 13 / scale, 14 / scale, 10 / scale)
    hexagonal_prism.points.SetPoint(4, 11 / scale, 14 / scale, 10 / scale)
    hexagonal_prism.points.SetPoint(5, 10 / scale, 12 / scale, 10 / scale)
    hexagonal_prism.points.SetPoint(6, 11 / scale, 10 / scale, 14 / scale)
    hexagonal_prism.points.SetPoint(7, 13 / scale, 10 / scale, 14 / scale)
    hexagonal_prism.points.SetPoint(8, 14 / scale, 12 / scale, 14 / scale)
    hexagonal_prism.points.SetPoint(9, 13 / scale, 14 / scale, 14 / scale)
    hexagonal_prism.points.SetPoint(10, 11 / scale, 14 / scale, 14 / scale)
    hexagonal_prism.points.SetPoint(11, 10 / scale, 12 / scale, 14 / scale)

    ug = vtkUnstructuredGrid(points=hexagonal_prism.points)
    ug.InsertNextCell(hexagonal_prism.cell_type, hexagonal_prism.point_ids)

    return ug


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


def draw_viewport_border(renderer, border, color=(0, 0, 0), line_width=2):
    """
    Draw a border around the viewport of a renderer.

    :param renderer: The renderer.
    :param border: The border to draw, it must be one of the constants in ViewPort.Border.
    :param color: The color.
    :param line_width: The line width of the border.
    :return:
    """

    def generate_border_lines(border_type):
        """
        Generate the lines for the border.

        :param border_type:  The border type to draw, it must be one of the constants in ViewPort.Border
        :return: The points and lines.
        """
        if border_type >= ViewPort.Border.NUMBER_OF_BORDER_TYPES:
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
        pt_orders = {
            ViewPort.Border.TOP: (0, 1),
            ViewPort.Border.LEFT: (1, 2),
            ViewPort.Border.BOTTOM: (2, 3),
            ViewPort.Border.RIGHT: (3, 4),
            ViewPort.Border.LEFT_BOTTOM: (1, 2, 3),
            ViewPort.Border.BOTTOM_RIGHT: (2, 3, 4),
            ViewPort.Border.RIGHT_TOP: (3, 4, 1),
            ViewPort.Border.RIGHT_TOP_LEFT: (3, 4, 1, 2),
            ViewPort.Border.TOP_LEFT: (0, 1, 2),
            ViewPort.Border.TOP_LEFT_BOTTOM: (0, 1, 2, 3),
            ViewPort.Border.TOP_LEFT_BOTTOM_RIGHT: (0, 1, 2, 3, 4)
        }
        pt_order = pt_orders[border_type]
        number_of_points = len(pt_order)
        points = vtkPoints(number_of_points=number_of_points)
        i = 0
        for pt_id in pt_order:
            points.InsertPoint(i, *pts[pt_id])
            i += 1

        lines = vtkPolyLine()
        lines.point_ids.SetNumberOfIds(number_of_points)
        for i in range(0, number_of_points):
            lines.point_ids.id = (i, i)

        cells = vtkCellArray()
        cells.InsertNextCell(lines)

        # Make the polydata and return.
        return vtkPolyData(points=points, lines=cells)

    # Use normalized viewport coordinates since
    # they are independent of window size.
    coordinate = vtkCoordinate(coordinate_system=Coordinate.CoordinateSystem.VTK_NORMALIZED_VIEWPORT)
    poly = vtkAppendPolyData()
    if border == ViewPort.Border.TOP_BOTTOM:
        (
            generate_border_lines(ViewPort.Border.TOP),
            generate_border_lines(ViewPort.Border.BOTTOM)
        ) >> poly
    elif border == ViewPort.Border.LEFT_RIGHT:
        (
            generate_border_lines(ViewPort.Border.LEFT),
            generate_border_lines(ViewPort.Border.RIGHT)
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


def make_tile(bounds, expansion_factor=0.1, thickness_ratio=0.05):
    """
    Make a tile slightly larger or smaller than the bounds in the
      X and Z directions and thinner or thicker in the Y direction.

    A thickness_ratio of zero reduces the tile to an XZ plane.

    :param bounds: The bounds for the tile.
    :param expansion_factor: The expansion factor in the XZ plane.
    :param thickness_ratio: The thickness ratio in the Y direction, >= 0.
    :return: An actor corresponding to the tile.
    """

    d_xyz = (
        bounds[1] - bounds[0],
        bounds[3] - bounds[2],
        bounds[5] - bounds[4]
    )
    thickness = d_xyz[2] * thickness_ratio
    center = ((bounds[1] + bounds[0]) / 2.0,
              bounds[2] - thickness / 2.0,
              (bounds[5] + bounds[4]) / 2.0)
    x_length = bounds[1] - bounds[0] + (d_xyz[0] * expansion_factor)
    z_length = bounds[5] - bounds[4] + (d_xyz[2] * expansion_factor)

    plane = vtkCubeSource(center=center, x_length=x_length, y_length=thickness, z_length=z_length)
    plane_mapper = vtkPolyDataMapper()
    plane >> plane_mapper
    tile_actor = vtkActor(mapper=plane_mapper)

    return tile_actor


@dataclass(frozen=True)
class Coordinate:
    @dataclass(frozen=True)
    class CoordinateSystem:
        VTK_DISPLAY: int = 0
        VTK_NORMALIZED_DISPLAY: int = 1
        VTK_VIEWPORT: int = 2
        VTK_NORMALIZED_VIEWPORT: int = 3
        VTK_VIEW: int = 4
        VTK_POSE: int = 5
        VTK_WORLD: int = 6
        VTK_USERDEFINED: int = 7


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


@dataclass(frozen=True)
class TextProperty:
    @dataclass(frozen=True)
    class FontFamily:
        VTK_ARIAL: int = 0
        VTK_COURIER: int = 1
        VTK_TIMES: int = 2
        VTK_UNKNOWN_FONT: int = 3

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


@dataclass(frozen=True)
class ViewPort:
    @dataclass(frozen=True)
    class Border:
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


if __name__ == '__main__':
    main()
