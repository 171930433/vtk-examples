#!/usr/bin/env python3

# Translated from dispPlot.tcl

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkFiltersCore import (
    vtkPolyDataNormals,
    vtkVectorDot
)
from vtkmodules.vtkFiltersGeneral import vtkWarpVector
from vtkmodules.vtkIOLegacy import vtkPolyDataReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkColorTransferFunction,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Produce figure 6–15(b) from the VTK Textbook.'
    epilogue = '''
        Produce figure 6–15(b) from the VTK Textbook.
        Surface plot of a vibrating plane.

        The color_scheme option allows you to select a series of colour schemes.
        0: The default:- cool maximum negative motion, warm maximum positive motion, white at the nodes.
        1: An alternative:- green maximum negative motion, purple maximum positive motion, white at the nodes.
        2: The original:- white at maximum motion, black at the nodes.

   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)
    parser.add_argument('filename', help='plate.vtk')
    parser.add_argument('color_scheme', default=0, type=int, nargs='?', help='The particular color scheme to use.')
    args = parser.parse_args()
    return args.filename, args.color_scheme


def main():
    file_name, color_scheme = get_program_parameters()

    color_scheme = abs(color_scheme)
    if color_scheme > 2:
        color_scheme = 0

    colors = vtkNamedColors()

    # Read a vtk file.
    plate = vtkPolyDataReader(file_name=file_name, vectors_name='mode8')

    # Deform the geometry, compute normals
    # and generate scalars from the dot product
    # of vectors and normals.
    warp = vtkWarpVector(scale_factor=0.5)
    normals = vtkPolyDataNormals()
    color = vtkVectorDot()

    lut = vtkLookupTable()
    make_lut(color_scheme, lut)

    plate_mapper = vtkDataSetMapper(scalar_range=(-1, 1), lookup_table=lut)
    plate >> warp >> normals >> color >> plate_mapper

    plate_actor = vtkActor(mapper=plate_mapper)

    # Create the RenderWindow, Renderer and both Actors.
    ren = vtkRenderer(background=colors.GetColor3d('Wheat'))
    ren_win = vtkRenderWindow(size=(512, 512), window_name='DisplacementPlot')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Add the actors to the renderer, set the background and size.
    ren.AddActor(plate_actor)

    ren.active_camera.position = (13.3991, 14.0764, 9.97787)
    ren.active_camera.focal_point = (1.50437, 0.481517, 4.52992)
    ren.active_camera.view_angle = 30
    ren.active_camera.view_up = (- 0.120861, 0.458556, - 0.880408)
    ren.active_camera.clipping_range = (12.5724, 26.8374)
    # Render the image.
    ren_win.Render()

    iren.Start()


def make_lut(color_scheme, lut):
    # See: [Diverging Color Maps for Scientific Visualization]
    #      (http:#www.kennethmoreland.com/color-maps/)
    nc = 256
    ctf = vtkColorTransferFunction()

    if color_scheme == 1:
        # Green to purple diverging.
        ctf.color_space = ColorTransferFunction.ColorSpace.VTK_CTF_DIVERGING
        ctf.AddRGBPoint(0.0, 0.085, 0.532, 0.201)
        ctf.AddRGBPoint(0.5, 0.865, 0.865, 0.865)
        ctf.AddRGBPoint(1.0, 0.436, 0.308, 0.631)
        lut.number_of_table_values = nc
        lut.Build()
        for i in range(0, nc):
            rgba = list(ctf.GetColor(float(i) / nc)) + [1.0]
            lut.SetTableValue(i, rgba)
    elif color_scheme == 2:
        # Make a lookup table, black in the centre with bright areas
        #   at the beginning and end of the table.
        # This is from the original code.
        nc2 = nc / 2.0
        lut.number_of_colors = nc
        lut.Build()
        for i in range(0, int(nc2)):
            # White to black.
            v = (nc2 - i) / nc2
            lut.SetTableValue(i, v, v, v, 1)
        for i in range(int(nc2), nc):
            # Black to white.
            v = (i - nc2) / nc2
            lut.SetTableValue(i, v, v, v, 1)
    else:
        # Cool to warm diverging.
        ctf.SetColorSpaceToDiverging()
        ctf.color_space = ColorTransferFunction.ColorSpace.VTK_CTF_DIVERGING
        ctf.AddRGBPoint(0.0, 0.230, 0.299, 0.754)
        ctf.AddRGBPoint(1.0, 0.706, 0.016, 0.150)
        lut.number_of_table_values = nc
        lut.Build()
        for i in range(0, nc):
            rgba = list(ctf.GetColor(float(i) / nc)) + [1.0]
            lut.SetTableValue(i, rgba)


@dataclass(frozen=True)
class ColorTransferFunction:
    @dataclass(frozen=True)
    class ColorSpace:
        VTK_CTF_RGB: int = 0
        VTK_CTF_HSV: int = 1
        VTK_CTF_LAB: int = 2
        VTK_CTF_DIVERGING: int = 3
        VTK_CTF_LAB_CIEDE2000: int = 4
        VTK_CTF_STEP: int = 5

    @dataclass(frozen=True)
    class Scale:
        VTK_CTF_LINEAR: int = 0
        VTK_CTF_LOG10: int = 1


if __name__ == '__main__':
    main()
