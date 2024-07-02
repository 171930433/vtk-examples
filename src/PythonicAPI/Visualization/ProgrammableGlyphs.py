#!/usr/bin/env python3

# Python example translated directly from Tcl test
# [vtk_source]/Graphics/Testing/Tcl/progGlyphs.tcl

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkElevationFilter
from vtkmodules.vtkFiltersProgrammable import vtkProgrammableGlyphFilter
from vtkmodules.vtkFiltersSources import (
    vtkPlaneSource,
    vtkSuperquadricSource
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    res = 6
    plane = vtkPlaneSource(resolution=(res, res))
    colors = vtkElevationFilter(low_point=(-0.25, -0.25, -0.25), high_point=(0.25, 0.25, 0.25))
    plane_mapper = vtkPolyDataMapper()
    plane >> colors >> plane_mapper
    plane_actor = vtkActor(mapper=plane_mapper)
    plane_actor.SetMapper(plane_mapper)
    plane_actor.property.representation = Property.Representation.VTK_WIREFRAME

    # Create a simple poly data so we can apply glyph.
    squad = vtkSuperquadricSource()

    def Glyph():
        """
        # The procedure for generating glyphs.
        :return:
        """
        xyz = glypher.point
        x = xyz[0]
        y = xyz[1]
        length = glypher.GetInput(0).length
        scale = length / (2.0 * res)

        squad.scale = (scale, scale, scale)
        squad.center = xyz
        squad.phi_roundness = abs(x) * 5.0
        squad.theta_roundness = abs(y) * 5.0

    glypher = vtkProgrammableGlyphFilter(source_connection=squad.output_port)
    glypher.SetGlyphMethod(Glyph)
    glyph_mapper = vtkPolyDataMapper()
    plane >> colors >> glypher >> glyph_mapper
    glyph_actor = vtkActor(mapper=glyph_mapper)

    colors = vtkNamedColors()

    # Create the rendering stuff.
    ren = vtkRenderer(background=colors.GetColor3d('Silver'))
    ren_win = vtkRenderWindow(size=(450, 450), multi_samples=0, window_name='ProgrammableGlyphs')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win
    ren.AddActor(plane_actor)
    ren.AddActor(glyph_actor)

    ren_win.Render()

    ren.active_camera.Zoom(1.3)

    iren.Start()


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


if __name__ == '__main__':
    main()
