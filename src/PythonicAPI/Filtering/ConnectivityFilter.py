#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import (
    vtkAppendFilter,
    vtkConnectivityFilter,
    vtkDelaunay3D
)
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    append_filter = vtkAppendFilter()
    vtkSphereSource() >> vtkDelaunay3D() >> append_filter
    vtkSphereSource(center=(5, 0, 0)) >> vtkDelaunay3D() >> append_filter

    connectivity_filter = vtkConnectivityFilter(color_regions=True,
                                                extraction_mode=ConnectivityFilterExtractionMode.VTK_EXTRACT_ALL_REGIONS)

    # Visualize
    mapper = vtkDataSetMapper()
    append_filter >> connectivity_filter >> mapper

    actor = vtkActor(mapper=mapper)

    renderer = vtkRenderer(background=colors.GetColor3d('deep_ochre'))
    renderer.AddActor(actor)

    ren_window = vtkRenderWindow(window_name='ConnectivityFilter')
    ren_window.AddRenderer(renderer)
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_window)

    ren_window.Render()
    renderer.active_camera.Zoom(0.9)
    ren_window.Render()
    iren.Start()


# -----------------------------------------------------------------------------
# These handle the "#define VTK_SOME_CONSTANT x" in the VTK C++ code.
# The class name consists of the VTK class name (without the leading vtk)
# appended to the relevant Set/Get Macro name.
# Note: To find these constants, use the link to the header in the
#       documentation for the class.
# ------------------------------------------------------------------------------
@dataclass(frozen=True)
class ConnectivityFilterExtractionMode:
    VTK_EXTRACT_POINT_SEEDED_REGIONS: int = 1
    VTK_EXTRACT_CELL_SEEDED_REGIONS: int = 2
    VTK_EXTRACT_SPECIFIED_REGIONS: int = 3
    VTK_EXTRACT_LARGEST_REGION: int = 4
    VTK_EXTRACT_ALL_REGIONS: int = 5
    VTK_EXTRACT_CLOSEST_POINT_REGION: int = 6


if __name__ == '__main__':
    main()
