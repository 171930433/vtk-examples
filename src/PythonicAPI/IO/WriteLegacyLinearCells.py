#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import (
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
from vtkmodules.vtkIOLegacy import vtkUnstructuredGridWriter


def main():
    linear_cells = make_linear_cells()

    # Write each linear cell into  a file
    for k, v in linear_cells.items():
        file_name = k + '.vtk'
        print(f'Writing: {file_name}')
        writer = vtkUnstructuredGridWriter(file_name=file_name)
        v >> writer
        writer.Write()


def make_linear_cells():
    linear_cells = dict()

    linear_cells['Vertex'] = make_unstructured_grid(vtkVertex())
    linear_cells['PolyVertex'] = make_poly_vertex()
    linear_cells['Line'] = make_unstructured_grid(vtkLine())
    linear_cells['PolyLine'] = make_poly_line()
    linear_cells['Triangle'] = make_unstructured_grid(vtkTriangle())
    linear_cells['TriangleStrip'] = make_triangle_strip()
    linear_cells['Polygon'] = make_polygon()
    linear_cells['Pixel'] = make_unstructured_grid(vtkPixel())
    linear_cells['Quad'] = make_unstructured_grid(vtkQuad())
    linear_cells['Tetra'] = make_unstructured_grid(vtkTetra())
    linear_cells['Voxel'] = make_unstructured_grid(vtkVoxel())
    linear_cells['Hexahedron'] = make_unstructured_grid(vtkHexahedron())
    linear_cells['Wedge'] = make_unstructured_grid(vtkWedge())
    linear_cells['Pyramid'] = make_unstructured_grid(vtkPyramid())
    linear_cells['PentagonalPrism'] = make_unstructured_grid(vtkPentagonalPrism())
    linear_cells['HexagonalPrism'] = make_unstructured_grid(vtkHexagonalPrism())

    return linear_cells


def make_unstructured_grid(a_cell):
    pcoords = a_cell.parametric_coords
    for i in range(0, a_cell.number_of_points):
        a_cell.point_ids.SetId(i, i)
        a_cell.points.SetPoint(i, (pcoords[3 * i]), (pcoords[3 * i + 1]), (pcoords[3 * i + 2]))

    ug = vtkUnstructuredGrid()
    ug.points = a_cell.points
    ug.InsertNextCell(a_cell.cell_type, a_cell.point_ids)
    return ug


def make_poly_vertex():
    # A polyvertex is a cell representing a set of 3D vertices.
    number_of_vertices = 6

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, 0, 0)
    points.InsertNextPoint(0, 1, 0)
    points.InsertNextPoint(0, 0, 1)
    points.InsertNextPoint(1, 0, .4)
    points.InsertNextPoint(0, 1, .6)

    poly_vertex = vtkPolyVertex()
    poly_vertex.point_ids.SetNumberOfIds(number_of_vertices)

    for i in range(0, number_of_vertices):
        poly_vertex.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(poly_vertex.cell_type, poly_vertex.point_ids)

    return ug


def make_poly_line():
    # A polyline is a cell that represents a set of 1D lines
    number_of_vertices = 5

    points = vtkPoints()
    points.InsertNextPoint(0, .5, 0)
    points.InsertNextPoint(.5, 0, 0)
    points.InsertNextPoint(1, .3, 0)
    points.InsertNextPoint(1.5, .4, 0)
    points.InsertNextPoint(2.0, .4, 0)

    poly_line = vtkPolyLine()
    poly_line.point_ids.SetNumberOfIds(number_of_vertices)

    for i in range(0, number_of_vertices):
        poly_line.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(poly_line.cell_type, poly_line.point_ids)

    return ug


def make_triangle_strip():
    # A triangle is a cell that represents a triangle strip
    number_of_vertices = 10

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(.5, 1, 0)
    points.InsertNextPoint(1, -.1, 0)
    points.InsertNextPoint(1.5, .8, 0)
    points.InsertNextPoint(2.0, -.1, 0)
    points.InsertNextPoint(2.5, .9, 0)
    points.InsertNextPoint(3.0, 0, 0)
    points.InsertNextPoint(3.5, .8, 0)
    points.InsertNextPoint(4.0, -.2, 0)
    points.InsertNextPoint(4.5, 1.1, 0)

    triangle_strip = vtkTriangleStrip()
    triangle_strip.point_ids.SetNumberOfIds(number_of_vertices)
    for i in range(0, number_of_vertices):
        triangle_strip.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(triangle_strip.cell_type, triangle_strip.point_ids)

    return ug


def make_polygon():
    # A polygon is a cell that represents a polygon
    number_of_vertices = 6

    points = vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(1, -.1, 0)
    points.InsertNextPoint(.8, .5, 0)
    points.InsertNextPoint(1, 1, 0)
    points.InsertNextPoint(.6, 1.2, 0)
    points.InsertNextPoint(0, .8, 0)

    polygon = vtkPolygon()
    polygon.point_ids.SetNumberOfIds(number_of_vertices)
    for i in range(0, number_of_vertices):
        polygon.point_ids.SetId(i, i)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.InsertNextCell(polygon.cell_type, polygon.point_ids)

    return ug


if __name__ == '__main__':
    main()
