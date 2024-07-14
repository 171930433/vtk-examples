#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkImagingSources import vtkImageCanvasSource2D
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleImage
from vtkmodules.vtkRenderingAnnotation import vtkCaptionActor2D
from vtkmodules.vtkRenderingCore import (
    vtkImageActor,
    vtkRenderWindowInteractor,
    vtkRenderWindow,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    draw_color1 = tuple(colors.GetColor3ub('DimGray'))
    draw_color2 = tuple(colors.GetColor3ub('HotPink'))

    # Create a blank, gray image.
    drawing = vtkImageCanvasSource2D(scalar_type=ImageCanvasSource2D.ScalarType.VTK_UNSIGNED_CHAR,
                                     number_of_scalar_components=3,
                                     extent=(0, 20, 0, 50, 0, 0), draw_color=draw_color1)
    drawing.FillBox(0, 20, 0, 50)

    # Draw a circle of radius 5 centered at (9,10).
    drawing.draw_color = draw_color2
    drawing.DrawCircle(9, 10, 5)

    actor = vtkImageActor()
    drawing >> actor.mapper

    ren = vtkRenderer(background=colors.GetColor3d('SkyBlue'),
                      background2=colors.GetColor3d('MidnightBlue'),
                      gradient_background=2)
    ren_win = vtkRenderWindow(window_name='CaptionActor2D', number_of_layers=2)
    ren_win.AddRenderer(ren)
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    ren.AddActor(actor)

    ren_win.Render()

    style = MyStyle()
    iren.interactor_style = style
    style.default_renderer = ren
    style.current_renderer = ren
    iren.Start()


class MyStyle(vtkInteractorStyleImage):

    def __init__(self):
        super().__init__()

        self.AddObserver('LeftButtonPressEvent', self.OnLeftButtonDown)
        self.count = 0

    def OnLeftButtonDown(self, obj, event):
        self.interactor.picker.Pick(self.interactor.GetEventPosition()[0],
                                    self.interactor.GetEventPosition()[1],
                                    0,
                                    self.current_renderer)
        picked = self.interactor.picker.pick_position
        self.add_number(picked)

        # Forward events.
        super().OnLeftButtonDown()

        super().interactor.Render()

    def add_number(self, p):
        colors = vtkNamedColors()
        p = list(p)
        if p[0] == 0 and p[1] == 0:
            # Not in the box.
            return
        s = f'adding marker at: {p[0]:6.4f} {p[1]:6.4f}'

        # # Normally, with an image you would do:
        # s = self.image.spacing
        # o = self.image.origin
        # p[0] = int((p[0] - o[0]) / s[0] + 0.5)
        # p[1] = int((p[1] - o[1]) / s[1] + 0.5)
        # Here we do:
        p[0] = int(p[0]) + 0.5
        p[1] = int(p[1]) + 0.5
        s += f' -> {p[0]:3.1f} {p[1]:3.1f}'

        # Create an actor for the text
        caption_actor = vtkCaptionActor2D(caption=str(self.count), attachment_point=p, border=False,
                                          three_dimensional_leader=False)
        caption_actor.caption_text_property.bold = False
        caption_actor.caption_text_property.italic = False
        caption_actor.caption_text_property.shadow = False

        self.current_renderer.AddViewProp(caption_actor)
        print(f'For point: {self.count:3d} {s}')

        self.count += 1


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
class ImageCanvasSource2D:
    @dataclass(frozen=True)
    class ScalarType:
        VTK_CHAR: int = 2
        VTK_UNSIGNED_CHAR: int = 3
        VTK_SHORT: int = 4
        VTK_UNSIGNED_SHORT: int = 5
        VTK_INT: int = 6
        VTK_UNSIGNED_INT: int = 7
        VTK_LONG: int = 8
        VTK_UNSIGNED_LONG: int = 9
        VTK_FLOAT: int = 10
        VTK_DOUBLE: int = 11


if __name__ == '__main__':
    main()
