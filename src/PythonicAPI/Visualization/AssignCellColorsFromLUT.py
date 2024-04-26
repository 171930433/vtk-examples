#!/usr/bin/env python3

"""
Demonstrates how to assign colors to cells in a vtkPolyData structure using
 lookup tables.
Two techniques are demonstrated:
1) Using a lookup table of predefined colors.
2) Using a lookup table generated from a color transfer function.

The resultant display shows in the left-hand column, the cells in a plane
colored by the two lookup tables and in the right-hand column, the same
polydata that has been read in from a file demonstrating that the structures
are identical.

The top row of the display uses the color transfer function to create a
 green to tan transition in a diverging color space.
 Note that the central square is white indicating the midpoint.
The bottom row of the display uses a lookup table of predefined colors.
"""

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkLookupTable,
    vtkUnsignedCharArray
)
from vtkmodules.vtkFiltersSources import vtkPlaneSource
from vtkmodules.vtkIOXML import (
    vtkXMLPolyDataReader,
    vtkXMLPolyDataWriter,
    vtkXMLWriterBase
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkColorTransferFunction,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def make_lut(table_size):
    """
    Make a lookup table from a set of named colors.
    :param: table_size - The table size
    :return: The lookup table.
    """
    nc = vtkNamedColors()

    lut = vtkLookupTable()
    lut.SetNumberOfTableValues(table_size)
    lut.Build()

    # Fill in a few known colors, the rest will be generated if needed.
    lut.table_value = (0, nc.GetColor4d('Black'))
    lut.table_value = (1, nc.GetColor4d('Banana'))
    lut.table_value = (2, nc.GetColor4d('Tomato'))
    lut.table_value = (3, nc.GetColor4d('Wheat'))
    lut.table_value = (4, nc.GetColor4d('Lavender'))
    lut.table_value = (5, nc.GetColor4d('Flesh'))
    lut.table_value = (6, nc.GetColor4d('Raspberry'))
    lut.table_value = (7, nc.GetColor4d('Salmon'))
    lut.table_value = (8, nc.GetColor4d('Mint'))
    lut.table_value = (9, nc.GetColor4d('Peacock'))

    return lut


def make_lut_from_ctf(table_size):
    """
    Use a color transfer Function to generate the colors in the lookup table.
    See: http://www.org/doc/nightly/html/classvtkColorTransferFunction.html
    :param: table_size - The table size
    :return: The lookup table.
    """
    ctf = vtkColorTransferFunction()
    ctf.SetColorSpaceToDiverging()
    # Green to tan.
    ctf.AddRGBPoint(0.0, 0.085, 0.532, 0.201)
    ctf.AddRGBPoint(0.5, 0.865, 0.865, 0.865)
    ctf.AddRGBPoint(1.0, 0.677, 0.492, 0.093)

    lut = vtkLookupTable(number_of_table_values=table_size)
    lut.Build()

    for i in range(0, table_size):
        rgba = (*ctf.GetColor(float(i) / table_size), 1.0)
        lut.table_value = (i, rgba)

    return lut


def make_cell_data(table_size, lut, colors):
    """
    Create the cell data using the colors from the lookup table.
    :param: table_size - The table size
    :param: lut - The lookup table.
    :param: colors - A reference to a vtkUnsignedCharArray().
    """
    for i in range(1, table_size):
        rgb = [0.0, 0.0, 0.0]
        lut.GetColor(float(i) / (table_size - 1), rgb)
        ucrgb = list(map(int, [x * 255 for x in rgb]))
        colors.InsertNextTuple3(ucrgb[0], ucrgb[1], ucrgb[2])
        s = '[' + ', '.join(['{:0.6f}'.format(x) for x in rgb]) + ']'
        print(s, ucrgb)


def main():
    """
    :return: The render window interactor.
    """

    nc = vtkNamedColors()

    # Provide some geometry
    resolution = 3

    # 11 = column 1 row 1, 12 = column 1, row 2
    plane11 = vtkPlaneSource(x_resolution=resolution, y_resolution=resolution)
    plane12 = vtkPlaneSource(x_resolution=resolution, y_resolution=resolution)

    table_size = max(resolution * resolution + 1, 10)
    #  Get the lookup tables mapping cell data to colors
    lut1 = make_lut(table_size)
    lut2 = make_lut_from_ctf(table_size)

    # Force an update so we can set cell data.
    plane11.update()
    plane12.update()

    color_data1 = vtkUnsignedCharArray()
    color_data1.SetName('colors')  # Any name will work here.
    color_data1.SetNumberOfComponents(3)
    print('Using a lookup table from a set of named colors.')
    make_cell_data(table_size, lut1, color_data1)
    # Then use SetScalars() to add it to the vtkPolyData structure,
    # this will then be interpreted as a color table.
    plane11.output.cell_data.SetScalars(color_data1)

    color_data2 = vtkUnsignedCharArray()
    color_data2.SetName('colors')  # Any name will work here.
    color_data2.SetNumberOfComponents(3)
    print('Using a lookup table created from a color transfer function.')
    make_cell_data(table_size, lut2, color_data2)
    plane12.output.cell_data.SetScalars(color_data2)

    # Set up mappers.
    mappers = dict()

    # Instead of doing this:
    # mappers['11'] = vtkPolyDataMapper(scalar_range=(0, table_size - 1), lookup_table=lut1)
    # We just use the color data that we created from the lookup table and
    # the lookup table and assigned to the cells:
    mappers['11'] = vtkPolyDataMapper(scalar_mode=Mapper.ScalarMode.VTK_SCALAR_MODE_USE_CELL_DATA)
    plane11 >> mappers['11']
    mappers['12'] = vtkPolyDataMapper(scalar_mode=Mapper.ScalarMode.VTK_SCALAR_MODE_USE_CELL_DATA)
    plane12 >> mappers['12']

    # We set the data mode to ASCII, so we can see the data in a text editor.
    writer = vtkXMLPolyDataWriter(file_name='pdlut.vtp', data_mode=vtkXMLWriterBase.Ascii)
    mappers['11'].input >> writer
    writer.Write()
    writer.file_name = 'pdctf.vtp'
    mappers['12'].input >> writer
    writer.Write()

    # Let's read in the data we wrote out.
    reader1 = vtkXMLPolyDataReader(file_name='pdlut.vtp')
    mappers['21'] = vtkPolyDataMapper(scalar_mode=Mapper.ScalarMode.VTK_SCALAR_MODE_USE_CELL_DATA)
    reader1 >> mappers['21']

    reader2 = vtkXMLPolyDataReader(file_name='pdctf.vtp')
    mappers['22'] = vtkPolyDataMapper(scalar_mode=Mapper.ScalarMode.VTK_SCALAR_MODE_USE_CELL_DATA)
    reader2 >> mappers['22']

    vp_names = ('11', '12', '21', '22')

    # Define viewport ranges.
    # (xmin, ymin, xmax, ymax)
    viewports = {
        '11': (0.0, 0.0, 0.5, 0.5),
        '12': (0.0, 0.5, 0.5, 1.0),
        '21': (0.5, 0.0, 1.0, 0.5),
        '22': (0.5, 0.5, 1.0, 1.0)
    }

    ren_win = vtkRenderWindow(size=(600, 600), window_name='AssignCellColorsFromLUT')

    # Set up the renders.
    ren_bkg = nc.GetColor3d('MidnightBlue')
    for vp in vp_names:
        actor = vtkActor(mapper=mappers[vp])
        ren = vtkRenderer(background=ren_bkg, viewport=viewports[vp])
        ren.AddActor(actor)
        ren_win.AddRenderer(ren)

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win
    ren_win.Render()

    return iren


@dataclass(frozen=True)
class Mapper:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_MODE_DEFAULT: int = 0
        VTK_COLOR_MODE_MAP_SCALARS: int = 1
        VTK_COLOR_MODE_DIRECT_SCALARS: int = 2

    @dataclass(frozen=True)
    class ResolveCoincidentTopology:
        VTK_RESOLVE_OFF: int = 0
        VTK_RESOLVE_POLYGON_OFFSET: int = 1
        VTK_RESOLVE_SHIFT_ZBUFFER: int = 2

    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_DEFAULT: int = 0
        VTK_SCALAR_MODE_USE_POINT_DATA: int = 1
        VTK_SCALAR_MODE_USE_CELL_DATA: int = 2
        VTK_SCALAR_MODE_USE_POINT_FIELD_DATA: int = 3
        VTK_SCALAR_MODE_USE_CELL_FIELD_DATA: int = 4
        VTK_SCALAR_MODE_USE_FIELD_DATA: int = 5


if __name__ == '__main__':
    interactor = main()
    interactor.Start()
