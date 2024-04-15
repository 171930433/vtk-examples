#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import vtkElevationFilter
from vtkmodules.vtkFiltersGeneral import vtkTransformFilter
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

    sphere = vtkSphereSource(phi_resolution=12, theta_resolution=12)

    a_transform = vtkTransform()
    a_transform.Scale(1, 1.5, 2)

    trans_filter = vtkTransformFilter(transform=a_transform)

    color_it = vtkElevationFilter(low_point=(0, 0, -1), high_point=(0, 0, 1))

    lut = vtkLookupTable(hue_range=(0.667, 0), saturation_range=(1, 1), value_range=(1, 1))

    mapper = vtkDataSetMapper(lookup_table=lut)
    sphere >> trans_filter >> color_it >> mapper

    actor = vtkActor(mapper=mapper)

    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='TransformSphere')
    ren_win.AddRenderer(renderer)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    renderer.AddActor(actor)
    renderer.ResetCamera()
    renderer.active_camera.Elevation(60.0)
    renderer.active_camera.Azimuth(30.0)
    renderer.ResetCameraClippingRange()

    ren_win.Render()

    # Interact with the data.
    iren.Start()


if __name__ == '__main__':
    main()
