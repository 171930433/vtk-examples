#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import (
    vtkElevationFilter,
    vtkPolyDataNormals,
)
from vtkmodules.vtkFiltersSources import (
    vtkConeSource,
    vtkCylinderSource
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

    # extraction_mode = {'point_seeded_regions': 1, 'cell_seeded_regions': 2, 'specified_regions': 3, 'largest_region': 4,
    #                    'all_regions': 5, 'closest_point_region': 6}
    # pipeline = (
    #         vtkElevationFilter()
    #         >> vtkShrinkFilter()
    #         >> vtkGeometryFilter()
    #         >> vtkPolyDataConnectivityFilter(color_regions=True, extraction_mode=extraction_mode['all_regions'])
    #         >> vtkPolyDataNormals()
    # )
    p1 = (
            vtkElevationFilter(low_point=(0, -2, 2), high_point=(0, 3, 2))
            >> vtkPolyDataNormals()
    )
    p2 = (
            vtkElevationFilter(low_point=(0, -2, 2), high_point=(0, 3, 2))
            >> vtkPolyDataNormals()
    )

    cone = vtkConeSource(radius=5, resolution=8, height=2, direction=(0, 1, 0), center=(0, 1.5001, 0))
    cone_mapper = vtkPolyDataMapper()
    cone_actor = vtkActor(mapper=cone_mapper)

    cylinder = vtkCylinderSource(radius=6, resolution=9, height=3, center=(0, -1, 0))
    cylinder_mapper = vtkPolyDataMapper()
    cylinder_actor = vtkActor(mapper=cylinder_mapper)

    # This works since p1 and p2 are separate pipelines.
    cone >> p1 >> cone_mapper
    cylinder >> p2 >> cylinder_mapper

    # Only the cylinder is mapped because whilst p1 is assigned to p2, it is, in fact, p1.
    # p2 = p1
    # Will not work because update() is the same as update().output.
    # p2 = p1.update()
    # AttributeError: 'Pipeline' object has no attribute 'DeepCopy'
    # p2 = p1.DeepCopy()
    #
    # cylinder >> p2 >> cylinder_mapper

    ren = vtkRenderer(background=colors.GetColor3d('DimGray'))
    ren.AddActor(cone_actor)
    ren.AddActor(cylinder_actor)

    ren_win = vtkRenderWindow(size=[600, 600], window_name='PipelineReuse')
    ren_win.AddRenderer(ren)

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    ren_win.Render()

    iren.Start()


if __name__ == '__main__':
    main()
