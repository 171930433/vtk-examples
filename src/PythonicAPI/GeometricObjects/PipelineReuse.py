#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import (
    vtkAppendPolyData,
    vtkElevationFilter,
    vtkPolyDataNormals,
)
from vtkmodules.vtkFiltersSources import (
    vtkConeSource,
    vtkCylinderSource,
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)


def main():
    colors = vtkNamedColors()

    p = (
            vtkElevationFilter(low_point=(0, -2.5, 0), high_point=(0, 3.5, 0))
            >> vtkPolyDataNormals()
    )

    cone = vtkConeSource(radius=5, resolution=8, height=3, direction=(0, 1, 0), center=(0, 2.0, 0))
    cylinder = vtkCylinderSource(radius=6, resolution=9, height=3, center=(0, -1, 0))

    append = vtkAppendPolyData()
    mapper = vtkPolyDataMapper()
    actor = vtkActor(mapper=mapper)

    # Here we use the pipeline in a functional way. This allows us to reuse the pipeline.
    # p(cone()) returns a data object detached from the pipeline so any changes to the pipeline
    # afterward would not be automatically propagated to the rendering pipeline.
    # Finally, we use an append filter to combine the cone and cylinder.
    (p(cone()), p(cylinder())) >> append >> mapper

    ren = vtkRenderer(background=colors.GetColor3d('DimGray'))
    ren.AddActor(actor)

    ren_win = vtkRenderWindow(size=[600, 600], window_name='PipelineReuse')
    ren_win.AddRenderer(ren)

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    ren_win.Render()

    iren.Start()


if __name__ == '__main__':
    main()
