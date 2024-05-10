#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersGeneral import vtkShrinkFilter
from vtkmodules.vtkFiltersHyperTree import vtkHyperTreeGridToUnstructuredGrid
from vtkmodules.vtkFiltersSources import vtkHyperTreeGridSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()
    # Create a hyper tree grid source.

    descriptor = [
        'RRR .R. .RR ..R ..R .R.|R.......................... ',
        '........................... ........................... ',
        '.............R............. ....RR.RR........R......... ',
        '.....RRRR.....R.RR......... ........................... ',
        '........................... ',
        '...........................|........................... ',
        '........................... ........................... ',
        '...RR.RR.......RR.......... ........................... ',
        'RR......................... ........................... ',
        '........................... ........................... ',
        '........................... ........................... ',
        '........................... ........................... ',
        '............RRR............|........................... ',
        '........................... .......RR.................. ',
        '........................... ........................... ',
        '........................... ........................... ',
        '........................... ........................... ',
        '........................... ',
        '...........................|........................... ',
        '...........................',
    ]

    source = vtkHyperTreeGridSource(max_depth=6, dimensions=(4, 4, 3), grid_scale=(1.5, 1.0, 0.7), branch_factor=4,
                                    descriptor=''.join(descriptor))

    # Hyper tree grid to unstructured grid filter.
    htg2ug = vtkHyperTreeGridToUnstructuredGrid()

    shrink = vtkShrinkFilter(shrink_factor=0.8)

    mapper = vtkDataSetMapper(scalar_visibility=False)

    source >> htg2ug >> shrink >> mapper

    actor = vtkActor(mapper=mapper)
    actor.property.diffuse_color = colors.GetColor3d('Burlywood')

    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    render_window = vtkRenderWindow(size=(640, 480), window_name='HyperTreeGridSource')
    render_window.AddRenderer(renderer)
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window

    renderer.AddActor(actor)
    renderer.ResetCamera()
    renderer.GetActiveCamera().Azimuth(150)
    renderer.GetActiveCamera().Elevation(30)
    renderer.ResetCameraClippingRange()

    render_window.Render()

    interactor.Start()


if __name__ == '__main__':
    main()
