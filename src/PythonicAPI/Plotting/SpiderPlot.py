#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkFloatArray,
    vtkMinimalStandardRandomSequence
)
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkRenderingAnnotation import vtkSpiderPlotActor
from vtkmodules.vtkRenderingCore import (
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    num_tuples = 12

    bitter = vtkFloatArray(number_of_tuples=num_tuples)
    crispy = vtkFloatArray(number_of_tuples=num_tuples)
    crunchy = vtkFloatArray(number_of_tuples=num_tuples)
    salty = vtkFloatArray(number_of_tuples=num_tuples)
    oily = vtkFloatArray(number_of_tuples=num_tuples)

    rand_seq = vtkMinimalStandardRandomSequence()
    rand_seq.seed = 8775070

    for i in range(num_tuples):
        bitter.SetTuple1(i, rand_seq.GetRangeValue(1, 10))
        rand_seq.Next()
        crispy.SetTuple1(i, rand_seq.GetRangeValue(-1, 1))
        rand_seq.Next()
        crunchy.SetTuple1(i, rand_seq.GetRangeValue(1, 100))
        rand_seq.Next()
        salty.SetTuple1(i, rand_seq.GetRangeValue(0, 10))
        rand_seq.Next()
        oily.SetTuple1(i, rand_seq.GetRangeValue(5, 25))
        rand_seq.Next()

    dobj = vtkDataObject()
    dobj.field_data.AddArray(bitter)
    dobj.field_data.AddArray(crispy)
    dobj.field_data.AddArray(crunchy)
    dobj.field_data.AddArray(salty)
    dobj.field_data.AddArray(oily)

    actor = vtkSpiderPlotActor(title='Spider Plot', input_data=dobj, legend_visibility=True,
                               independent_variables=SpiderPlotActor_IndependentVariables.VTK_IV_COLUMN)
    actor.position_coordinate.value = (0.05, 0.1, 0.0)
    actor.position2_coordinate.value = (0.95, 0.85, 0.0)
    actor.property.color = colors.GetColor3d('Red')

    actor.axis_label = (0, "Bitter")
    actor.axis_range = (0, 1, 10)

    actor.axis_label = (1, "Crispy")
    actor.axis_range = (1, -1, 1)

    actor.axis_label = (2, "Crunchy")
    actor.axis_range = (2, 1, 100)

    actor.axis_label = (3, "Salty")
    actor.axis_range = (3, 0, 10)

    actor.axis_label = (4, "Oily")
    actor.axis_range = (4, 5, 25)

    actor.legend_actor.number_of_entries = num_tuples

    for i in range(num_tuples):
        r = rand_seq.GetRangeValue(0.4, 1.0)
        rand_seq.Next()
        g = rand_seq.GetRangeValue(0.4, 1.0)
        rand_seq.Next()
        b = rand_seq.GetRangeValue(0.4, 1.0)
        rand_seq.Next()
        actor.plot_color = (i, r, g, b)

    actor.title_text_property.color = colors.GetColor3d('MistyRose')
    actor.label_text_property.color = colors.GetColor3d('MistyRose')

    ren = vtkRenderer(background=colors.GetColor3d('DarkSlateGray'))
    ren_win = vtkRenderWindow(size=(600, 500), window_name='SpiderPlot')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)
    ren.AddActor(actor)

    iren.Initialize()
    ren_win.Render()
    iren.Start()


@dataclass(frozen=True)
class SpiderPlotActor_IndependentVariables:
    VTK_IV_COLUMN: int = 0
    VTK_IV_ROW: int = 1


if __name__ == '__main__':
    main()
