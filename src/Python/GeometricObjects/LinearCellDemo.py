# !/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import (
    VTK_TETRA,
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
from vtkmodules.vtkFiltersSources import (
    vtkCubeSource,
    vtkSphereSource
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkActor2D,
    vtkDataSetMapper,
    vtkGlyph3DMapper,
    vtkPolyDataMapper,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextMapper,
    vtkTextProperty
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

    parser.add_argument('-n', '--no_plinth', action='store_true',
                        help='Remove the plinth.')
    args = parser.parse_args()
    return args.wireframe, args.backface, args.no_plinth


def main():
    wireframe_on, backface_on, plinth_off = get_program_parameters()

    colors = vtkNamedColors()

    # Create one sphere for all.
    sphere = vtkSphereSource()
    sphere.SetPhiResolution(21)
    sphere.SetThetaResolution(21)
    sphere.SetRadius(0.04)

    cells = get_unstructured_grids()
    keys = list(cells.keys())

    add_plinth = ('VTK_TETRA (=10)',
                  'VTK_VOXEL (=11)',
                  'VTK_HEXAHEDRON (=12)',
                  'VTK_WEDGE (=13)',
                  'VTK_PYRAMID (=14)',
                  'VTK_PENTAGONAL_PRISM (=15)',
                  'VTK_HEXAGONAL_PRISM (=16)',
                  )
    lines = ('VTK_LINE (=3)', 'VTK_POLY_LINE (=4)')

    # Set up the viewports.
    grid_column_dimensions = 4
    grid_row_dimensions = 4
    renderer_size = 300
    window_size = (grid_column_dimensions * renderer_size, grid_row_dimensions * renderer_size)

    viewports = dict()
    blank = len(cells)
    blank_viewports = list()

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

            if index < blank:
                viewports[keys[index]] = viewport
            else:
                s = f'vp_{col:d}_{row:d}'
                viewports[s] = viewport
                blank_viewports.append(s)

    # Create one text property for all.
    text_property = vtkTextProperty()
    text_property.SetFontSize(int(renderer_size / 18))
    text_property.BoldOn()
    text_property.SetJustificationToCentered()
    text_property.SetColor(colors.GetColor3d('Black'))

    label_property = vtkTextProperty()
    label_property.SetFontSize(int(renderer_size / 12))
    label_property.BoldOn()
    label_property.ShadowOn()
    label_property.SetJustificationToCentered()
    label_property.SetColor(colors.GetColor3d('DeepPink'))

    back_property = vtkProperty()
    back_property.SetColor(colors.GetColor3d('DodgerBlue'))

    ren_win = vtkRenderWindow()
    ren_win.SetSize(window_size)
    ren_win.SetWindowName('LinearCellDemo')

    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    renderers = dict()

    # Create and link the mappers, actors and renderers together.
    keys = cells.keys()
    for key in keys:
        print('Creating:', key)

        text_mapper = vtkTextMapper()
        text_mapper.SetTextProperty(text_property)
        text_mapper.SetInput(key)
        text_actor = vtkActor2D()
        text_actor.SetMapper(text_mapper)
        text_actor.SetPosition(renderer_size / 2.0, 8)

        mapper = vtkDataSetMapper()
        mapper.SetInputData(cells[key][0])
        actor = vtkActor()
        actor.SetMapper(mapper)
        if wireframe_on or key in lines:
            actor.GetProperty().SetRepresentationToWireframe()
            actor.GetProperty().SetLineWidth(2)
            actor.GetProperty().SetOpacity(1)
            actor.GetProperty().SetColor(colors.GetColor3d('Black'))
        else:
            actor.GetProperty().EdgeVisibilityOn()
            actor.GetProperty().SetLineWidth(3)
            actor.GetProperty().SetColor(colors.GetColor3d('Snow'))
            if backface_on:
                actor.GetProperty().SetOpacity(0.4)
                actor.SetBackfaceProperty(back_property)
                back_property.SetOpacity(0.6)
            else:
                actor.GetProperty().SetOpacity(0.8)

        # Label the points.
        label_mapper = vtkLabeledDataMapper()
        label_mapper.SetInputData(cells[key][0])
        label_mapper.SetLabelTextProperty(label_property)
        label_actor = vtkActor2D()
        label_actor.SetMapper(label_mapper)

        # Glyph the points.
        point_mapper = vtkGlyph3DMapper()
        point_mapper.SetInputData(cells[key][0])
        point_mapper.SetSourceConnection(sphere.GetOutputPort())
        point_mapper.ScalingOn()
        point_mapper.ScalarVisibilityOff()

        point_actor = vtkActor()
        point_actor.SetMapper(point_mapper)
        point_actor.GetProperty().SetColor(colors.GetColor3d('Gold'))

        renderer = vtkRenderer()
        renderer.SetBackground(colors.GetColor3d('LightSteelBlue'))
        renderer.SetViewport(viewports[key])

        renderer.AddActor(text_actor)
        renderer.AddActor(actor)
        renderer.AddActor(label_actor)
        renderer.AddActor(point_actor)
        if not plinth_off:
            # Add a plinth.
            if key in add_plinth:
                tile_actor = make_tile(cells[key][0].GetBounds(), expansion_factor=0.5, thickness_ratio=0.05)
                tile_actor.GetProperty().SetColor(colors.GetColor3d('Lavender'))
                tile_actor.GetProperty().SetOpacity(0.3)
                renderer.AddActor(tile_actor)

        renderer.ResetCamera()
        renderer.GetActiveCamera().Azimuth(cells[key][1])
        renderer.GetActiveCamera().Elevation(cells[key][2])
        renderer.GetActiveCamera().Dolly(cells[key][3])
        renderer.ResetCameraClippingRange()

        renderers[key] = renderer

        ren_win.AddRenderer(renderers[key])

    for name in blank_viewports:
        viewport = viewports[name]
        renderer = vtkRenderer()
        renderer.SetBackground = colors.GetColor3d('LightSteelBlue')
        renderer.SetViewport(viewport)
        ren_win.AddRenderer(renderer)

    ren_win.Render()
    iren.Initialize()
    iren.Start()


def get_unstructured_grids():
    """
    Get the unstructured grids along with their orientation.

    :return: A dictionary of unstructured grids.
    """
    cells = dict()
    # name, unstructured grid source, azimuth, elevation and dolly.
    cells['VTK_VERTEX (=1)'] = (make_vertex(), 30, -30, 0.1)
    cells['VTK_POLY_VERTEX (=2)'] = (make_poly_vertex(), 30, -30, 0.8)
    cells['VTK_LINE (=3)'] = (make_line(), 30, -30, 0.4)
    cells['VTK_POLY_LINE (=4)'] = (make_polyline(), 30, -30, 1.0)
    cells['VTK_TRIANGLE (=5)'] = (make_triangle(), 30, -30, 0.7)
    cells['VTK_TRIANGLE_STRIP (=6)'] = (make_triangle_strip(), 30, -30, 1.1)
    cells['VTK_POLYGON (=7)'] = (make_polygon(), 0, -45, 1.0)
    cells['VTK_PIXEL (=8)'] = (make_pixel(), 0, -45, 1.0)
    cells['VTK_QUAD (=9)'] = (make_quad(), 0, -45, 1.0)
    cells['VTK_TETRA (=10)'] = (make_tetra(), 20, 20, 1.0)
    cells['VTK_VOXEL (=11)'] = (make_voxel(), -22.5, 15, 0.95)
    cells['VTK_HEXAHEDRON (=12)'] = (make_hexahedron(), -22.5, 15, 0.95)
    cells['VTK_WEDGE (=13)'] = (make_wedge(), -30, 15, 1.0)
    cells['VTK_PYRAMID (=14)'] = (make_pyramid(), -60, 15, 1.0)
    cells['VTK_PENTAGONAL_PRISM (=15)'] = (make_pentagonal_prism(), -60, 10, 1.0)
    cells['VTK_HEXAGONAL_PRISM (=16)'] = (make_hexagonal_prism(), -60, 15, 1.0)

    return cells


# These functions return an vtkUnstructured grid corresponding to the object.

def make_vertex():
    # A vertex is a cell that represents a 3D point.
    number_of_vertices = 1

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)

    vertex = vtkVertex()
    for i in range(0, number_of_vertices):
        vertex.GetPointIds().SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(vertex.GetCellType(), vertex.GetPointIds())

    return ug


def make_poly_vertex():
    # A polyvertex is a cell that represents a set of 0D vertices.
    number_of_vertices = 6

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, 0, 0)
    points.InsertNextPoint(0, 1, 0)
    points.InsertNextPoint(0, 0, 1)
    points.InsertNextPoint(1, 0, 0.4)
    points.InsertNextPoint(0, 1, 0.6)

    poly_vertex = vtkPolyVertex()
    poly_vertex.GetPointIds().SetNumberOfIds(number_of_vertices)

    for i in range(0, number_of_vertices):
        poly_vertex.GetPointIds().SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(poly_vertex.GetCellType(), poly_vertex.GetPointIds())

    return ug


def make_line():
    # A line is a cell that represents a 1D point.
    number_of_vertices = 2

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(0.5, 0.5, 0)

    line = vtkLine()
    for i in range(0, number_of_vertices):
        line.GetPointIds().SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(line.GetCellType(), line.GetPointIds())

    return ug


def make_polyline():
    # A polyline is a cell that represents a set of 1D lines.
    number_of_vertices = 5

    points = vtkPoints()
    points.InsertNextPoint(0, 0.5, 0)
    points.InsertNextPoint(0.5, 0, 0)
    points.InsertNextPoint(1, 0.3, 0)
    points.InsertNextPoint(1.5, 0.4, 0)
    points.InsertNextPoint(2.0, 0.4, 0)

    polyline = vtkPolyLine()
    polyline.GetPointIds().SetNumberOfIds(number_of_vertices)

    for i in range(0, number_of_vertices):
        polyline.GetPointIds().SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(polyline.GetCellType(), polyline.GetPointIds())

    return ug


def make_triangle():
    # A triangle is a cell that represents a triangle.
    number_of_vertices = 3

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(0.5, 0.5, 0)
    points.InsertNextPoint(.2, 1, 0)

    triangle = vtkTriangle()
    for i in range(0, number_of_vertices):
        triangle.GetPointIds().SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(triangle.GetCellType(), triangle.GetPointIds())

    return ug


def make_triangle_strip():
    # A triangle strip is a cell that represents a triangle strip.
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

    triangle_strip = vtkTriangleStrip()
    triangle_strip.GetPointIds().SetNumberOfIds(number_of_vertices)
    for i in range(0, number_of_vertices):
        triangle_strip.GetPointIds().SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(triangle_strip.GetCellType(), triangle_strip.GetPointIds())

    return ug


def make_polygon():
    # A polygon is a cell that represents a polygon.
    number_of_vertices = 6

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, -0.1, 0)
    points.InsertNextPoint(0.8, 0.5, 0)
    points.InsertNextPoint(1, 1, 0)
    points.InsertNextPoint(0.6, 1.2, 0)
    points.InsertNextPoint(0, 0.8, 0)

    polygon = vtkPolygon()
    polygon.GetPointIds().SetNumberOfIds(number_of_vertices)
    for i in range(0, number_of_vertices):
        polygon.GetPointIds().SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(polygon.GetCellType(), polygon.GetPointIds())

    return ug


def make_pixel():
    # A pixel is a cell that represents a pixel
    number_of_vertices = 4

    pixel = vtkPixel()
    pixel.GetPoints().SetPoint(0, 0, 0, 0)
    pixel.GetPoints().SetPoint(1, 1, 0, 0)
    pixel.GetPoints().SetPoint(2, 0, 1, 0)
    pixel.GetPoints().SetPoint(3, 1, 1, 0)

    for i in range(0, number_of_vertices):
        pixel.GetPointIds().SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(pixel.GetPoints())
    ug.InsertNextCell(pixel.GetCellType(), pixel.GetPointIds())

    return ug


def make_quad():
    # A quad is a cell that represents a quad
    number_of_vertices = 4

    quad = vtkQuad()
    quad.GetPoints().SetPoint(0, 0, 0, 0)
    quad.GetPoints().SetPoint(1, 1, 0, 0)
    quad.GetPoints().SetPoint(2, 1, 1, 0)
    quad.GetPoints().SetPoint(3, 0, 1, 0)

    for i in range(0, number_of_vertices):
        quad.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(quad.GetPoints())
    ug.InsertNextCell(quad.GetCellType(), quad.GetPointIds())

    return ug


def make_tetra():
    # Make a tetrahedron.
    number_of_vertices = 4

    points = vtkPoints()
    # points.InsertNextPoint(0, 0, 0)
    # points.InsertNextPoint(1, 0, 0)
    # points.InsertNextPoint(1, 1, 0)
    # points.InsertNextPoint(0, 1, 1)

    # Rotate the above points -90° about the X-axis.
    points.InsertNextPoint((0.0, 0.0, 0.0))
    points.InsertNextPoint((1.0, 0.0, 0.0))
    points.InsertNextPoint((1.0, 0.0, -1.0))
    points.InsertNextPoint((0.0, 1.0, -1.0))

    tetra = vtkTetra()
    for i in range(0, number_of_vertices):
        tetra.GetPointIds().SetId(i, i)

    cell_array = vtkCellArray()
    cell_array.InsertNextCell(tetra)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
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
        voxel.GetPointIds().SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(voxel.GetCellType(), voxel.GetPointIds())

    return ug


def make_hexahedron():
    """
    A regular hexagon (cube) with all faces square and three squares
     around each vertex is created below.

    Set up the coordinates of eight points, (the two faces must be
     in counter-clockwise order as viewed from the outside).

    :return:
    """

    number_of_vertices = 8

    # Create the points.
    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, 0, 0)
    points.InsertNextPoint(1, 1, 0)
    points.InsertNextPoint(0, 1, 0)
    points.InsertNextPoint(0, 0, 1)
    points.InsertNextPoint(1, 0, 1)
    points.InsertNextPoint(1, 1, 1)
    points.InsertNextPoint(0, 1, 1)

    # Create a hexahedron from the points.
    hexahedron = vtkHexahedron()
    for i in range(0, number_of_vertices):
        hexahedron.GetPointIds().SetId(i, i)

    # Add the points and hexahedron to an unstructured grid
    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(hexahedron.GetCellType(), hexahedron.GetPointIds())

    return ug


def make_wedge():
    # A wedge consists of two triangular ends and three rectangular faces.

    number_of_vertices = 6

    points = vtkPoints()

    # points.InsertNextPoint(0, 1, 0)
    # points.InsertNextPoint(0, 0, 0)
    # points.InsertNextPoint(0, 0.5, 0.5)
    # points.InsertNextPoint(1, 1, 0)
    # points.InsertNextPoint(1, 0.0, 0.0)
    # points.InsertNextPoint(1, 0.5, 0.5)

    # Rotate the above points -90° about the X-axis
    #  and translate -1 along the Y-axis.
    points.InsertNextPoint(0.0, 0.0, 0.0)
    points.InsertNextPoint(0.0, 0, 1.0)
    points.InsertNextPoint(0.0, 0.5, 0.5)
    points.InsertNextPoint(1.0, 0.0, 0.0)
    points.InsertNextPoint(1.0, 0, 1.0)
    points.InsertNextPoint(1.0, 0.5, 0.5)

    wedge = vtkWedge()
    for i in range(0, number_of_vertices):
        wedge.GetPointIds().SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(wedge.GetCellType(), wedge.GetPointIds())

    return ug


def make_pyramid():
    # Make a regular square pyramid.
    number_of_vertices = 5

    points = vtkPoints()

    # p0 = [1.0, 1.0, 0.0]
    # p1 = [-1.0, 1.0, 0.0]
    # p2 = [-1.0, -1.0, 0.0]
    # p3 = [1.0, -1.0, 0.0]
    # p4 = [0.0, 0.0, 1.0]

    # Rotate the above points -90° about the X-axis.
    p0 = (1.0, 0, -1.0)
    p1 = (-1.0, 0, -1.0)
    p2 = (-1.0, 0, 1.0)
    p3 = (1.0, 0, 1.0)
    p4 = (0.0, 2.0, 0)

    points.InsertNextPoint(p0)
    points.InsertNextPoint(p1)
    points.InsertNextPoint(p2)
    points.InsertNextPoint(p3)
    points.InsertNextPoint(p4)

    pyramid = vtkPyramid()
    for i in range(0, number_of_vertices):
        pyramid.GetPointIds().SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(pyramid.GetCellType(), pyramid.GetPointIds())

    return ug


def make_pentagonal_prism():
    number_of_vertices = 10

    pentagonal_prism = vtkPentagonalPrism()

    scale = 2.0
    pentagonal_prism.GetPoints().SetPoint(0, 11 / scale, 10 / scale, 10 / scale)
    pentagonal_prism.GetPoints().SetPoint(1, 13 / scale, 10 / scale, 10 / scale)
    pentagonal_prism.GetPoints().SetPoint(2, 14 / scale, 12 / scale, 10 / scale)
    pentagonal_prism.GetPoints().SetPoint(3, 12 / scale, 14 / scale, 10 / scale)
    pentagonal_prism.GetPoints().SetPoint(4, 10 / scale, 12 / scale, 10 / scale)
    pentagonal_prism.GetPoints().SetPoint(5, 11 / scale, 10 / scale, 14 / scale)
    pentagonal_prism.GetPoints().SetPoint(6, 13 / scale, 10 / scale, 14 / scale)
    pentagonal_prism.GetPoints().SetPoint(7, 14 / scale, 12 / scale, 14 / scale)
    pentagonal_prism.GetPoints().SetPoint(8, 12 / scale, 14 / scale, 14 / scale)
    pentagonal_prism.GetPoints().SetPoint(9, 10 / scale, 12 / scale, 14 / scale)

    for i in range(0, number_of_vertices):
        pentagonal_prism.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(pentagonal_prism.GetPoints())
    ug.InsertNextCell(pentagonal_prism.GetCellType(), pentagonal_prism.GetPointIds())

    return ug


def make_hexagonal_prism():
    number_of_vertices = 12

    hexagonal_prism = vtkHexagonalPrism()

    scale = 2.0
    hexagonal_prism.GetPoints().SetPoint(0, 11 / scale, 10 / scale, 10 / scale)
    hexagonal_prism.GetPoints().SetPoint(1, 13 / scale, 10 / scale, 10 / scale)
    hexagonal_prism.GetPoints().SetPoint(2, 14 / scale, 12 / scale, 10 / scale)
    hexagonal_prism.GetPoints().SetPoint(3, 13 / scale, 14 / scale, 10 / scale)
    hexagonal_prism.GetPoints().SetPoint(4, 11 / scale, 14 / scale, 10 / scale)
    hexagonal_prism.GetPoints().SetPoint(5, 10 / scale, 12 / scale, 10 / scale)
    hexagonal_prism.GetPoints().SetPoint(6, 11 / scale, 10 / scale, 14 / scale)
    hexagonal_prism.GetPoints().SetPoint(7, 13 / scale, 10 / scale, 14 / scale)
    hexagonal_prism.GetPoints().SetPoint(8, 14 / scale, 12 / scale, 14 / scale)
    hexagonal_prism.GetPoints().SetPoint(9, 13 / scale, 14 / scale, 14 / scale)
    hexagonal_prism.GetPoints().SetPoint(10, 11 / scale, 14 / scale, 14 / scale)
    hexagonal_prism.GetPoints().SetPoint(11, 10 / scale, 12 / scale, 14 / scale)

    for i in range(0, number_of_vertices):
        hexagonal_prism.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(hexagonal_prism.GetPoints())
    ug.InsertNextCell(hexagonal_prism.GetCellType(), hexagonal_prism.GetPointIds())

    return ug


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
    thickness = d_xyz[2] * abs(thickness_ratio)
    center = ((bounds[1] + bounds[0]) / 2.0,
              bounds[2] - thickness / 2.0,
              (bounds[5] + bounds[4]) / 2.0)
    x_length = bounds[1] - bounds[0] + (d_xyz[0] * expansion_factor)
    z_length = bounds[5] - bounds[4] + (d_xyz[2] * expansion_factor)
    plane = vtkCubeSource()
    plane.SetCenter(center)
    plane.SetXLength(x_length)
    plane.SetYLength(thickness)
    plane.SetZLength(z_length)

    plane_mapper = vtkPolyDataMapper()
    plane_mapper.SetInputConnection(plane.GetOutputPort())

    tile_actor = vtkActor()
    tile_actor.SetMapper(plane_mapper)

    return tile_actor


if __name__ == '__main__':
    main()
