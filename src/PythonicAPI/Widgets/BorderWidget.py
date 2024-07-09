#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkLookupTable
)
from vtkmodules.vtkFiltersSources import vtkPlatonicSolidSource
from vtkmodules.vtkInteractionWidgets import (
    vtkBorderRepresentation,
    vtkBorderWidget

)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    lut = get_platonic_lut()

    # A renderer, render window and interactor.
    ren = vtkRenderer(background=colors.GetColor3d('SteelBlue'))
    ren_win = vtkRenderWindow(window_name='BorderWidget')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    platonic_solid = vtkPlatonicSolidSource(solid_type=PlatonicSolidSource.SolidType.VTK_SOLID_DODECAHEDRON)
    mapper = vtkPolyDataMapper(lookup_table=lut, scalar_range=(0, 19))
    platonic_solid >> mapper
    actor = vtkActor(mapper=mapper)
    ren.AddActor(actor)

    # Create the widget and its representation
    rep = vtkBorderRepresentation(proportional_resize=True, show_border=True)
    # This has no effect, the border remains white.
    rep.border_property.color = colors.GetColor3d('Yellow')

    widget = vtkBorderWidget(interactor=iren, representation=rep, selectable=False)
    widget.AddObserver('EndInteractionEvent', BorderCallback(ren))

    ren_win.Render()
    ren.active_camera.Elevation(30.0)
    ren.active_camera.Azimuth(180.0)

    iren.Initialize()
    ren_win.Render()
    widget.On()
    iren.Start()


def get_platonic_lut():
    """
    Get a specialised lookup table for the platonic solids.

    Since each face of a vtkPlatonicSolidSource has a different
    cell scalar, we create a lookup table with a different colour
    for each face.
    The colors have been carefully chosen so that adjacent cells
    are colored distinctly.

    :return: The lookup table.
    """
    lut = vtkLookupTable(number_of_table_values=20, table_range=(0.0, 19.0))
    # lut.SetNumberOfTableValues(20)
    # lut.SetTableRange(0.0, 19.0)
    lut.Build()
    lut.SetTableValue(0, 0.1, 0.1, 0.1)
    lut.SetTableValue(1, 0, 0, 1)
    lut.SetTableValue(2, 0, 1, 0)
    lut.SetTableValue(3, 0, 1, 1)
    lut.SetTableValue(4, 1, 0, 0)
    lut.SetTableValue(5, 1, 0, 1)
    lut.SetTableValue(6, 1, 1, 0)
    lut.SetTableValue(7, 0.9, 0.7, 0.9)
    lut.SetTableValue(8, 0.5, 0.5, 0.5)
    lut.SetTableValue(9, 0.0, 0.0, 0.7)
    lut.SetTableValue(10, 0.5, 0.7, 0.5)
    lut.SetTableValue(11, 0, 0.7, 0.7)
    lut.SetTableValue(12, 0.7, 0, 0)
    lut.SetTableValue(13, 0.7, 0, 0.7)
    lut.SetTableValue(14, 0.7, 0.7, 0)
    lut.SetTableValue(15, 0, 0, 0.4)
    lut.SetTableValue(16, 0, 0.4, 0)
    lut.SetTableValue(17, 0, 0.4, 0.4)
    lut.SetTableValue(18, 0.4, 0, 0)
    lut.SetTableValue(19, 0.4, 0, 0.4)
    return lut


class BorderCallback(object):
    def __init__(self, ren):
        self.ren = ren

    def __call__(self, caller, ev):
        # Just do this to demonstrate who called callback and the event that triggered it.
        # print(caller.GetClassName(), 'Event Id:', ev)
        rep = caller.representation
        # Viewport coordinates.
        lower_left = rep.position
        upper_right = rep.position2
        print('Viewport coordinates:')
        print(f'Lower left:  ({lower_left[0]:5.2f}, {lower_left[1]:5.2f}),')
        print(f'Upper right: ({lower_left[0] + upper_right[0]:5.2f}, {lower_left[1] + upper_right[1]:5.2f}),')
        # World coordinates.
        # lower_left_coordinate = rep.position_coordinate
        # lower_left = lower_left_coordinate.GetComputedWorldValue(self.ren)
        # upper_right_coordinate = rep.position2_coordinate
        # upper_right = upper_right_coordinate.GetComputedWorldValue(self.ren)
        # print('World coordinates:')
        # print(f'Lower left:  ({lower_left[0]:5.2f}, {lower_left[1]:5.2f}),')
        # print(f'Upper right: ({upper_right[0]:5.2f}, {upper_right[1]:5.2f}),')


@dataclass(frozen=True)
class PlatonicSolidSource:
    @dataclass(frozen=True)
    class SolidType:
        VTK_SOLID_TETRAHEDRON: int = 0
        VTK_SOLID_CUBE: int = 1
        VTK_SOLID_OCTAHEDRON: int = 2
        VTK_SOLID_ICOSAHEDRON: int = 3
        VTK_SOLID_DODECAHEDRON: int = 4


if __name__ == '__main__':
    main()
