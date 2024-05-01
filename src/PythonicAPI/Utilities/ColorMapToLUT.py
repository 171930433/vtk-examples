#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkElevationFilter
from vtkmodules.vtkFiltersSources import vtkConeSource, vtkSphereSource
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDiscretizableColorTransferFunction,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    use_sphere = False

    colors = vtkNamedColors()
    colors.SetColor('ParaViewBkg', 82, 87, 110, 255)

    ren = vtkRenderer(background=colors.GetColor3d('ParaViewBkg'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='ColorMapToLUT')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    style = vtkInteractorStyleTrackballCamera()
    iren.interactor_style = style

    if use_sphere:
        sphere = vtkSphereSource(theta_resolution=64, phi_resolution=32)
        bounds = sphere.update().output.GetBounds()
    else:
        cone = vtkConeSource(resolution=6, direction=(0, 1, 0), height=1)
        bounds = cone.update().output.GetBounds()

    elevation_filter = vtkElevationFilter(low_point=(0, bounds[2], 0), high_point=(0, bounds[3], 0))

    ctf = get_ctf()

    mapper = vtkPolyDataMapper(lookup_table=ctf, color_mode=Mapper.ColorMode.VTK_COLOR_MODE_MAP_SCALARS)
    if use_sphere:
        sphere >> elevation_filter >> mapper
    else:
        cone >> elevation_filter >> mapper
    mapper.interpolate_scalars_before_mapping = True

    actor = vtkActor(mapper=mapper)

    ren.AddActor(actor)

    ren_win.Render()
    iren.Start()


def get_ctf():
    # name: Fast, creator: Francesca Samsel and Alan W. Scott
    # interpolationspace: RGB, space: rgb
    # file name: Fast.json

    ctf = vtkDiscretizableColorTransferFunction(color_space=ColorTransferFunction.ColorSpace.VTK_CTF_RGB,
                                                scale=ColorTransferFunction.Scale.VTK_CTF_LINEAR,
                                                nan_color=(0.0, 0.0, 0.0),
                                                number_of_values=9, discretize=False)

    ctf.AddRGBPoint(0, 0.05639999999999999, 0.05639999999999999, 0.47)
    ctf.AddRGBPoint(0.17159223942480895, 0.24300000000000013, 0.4603500000000004, 0.81)
    ctf.AddRGBPoint(0.2984914818394138, 0.3568143826543521, 0.7450246485363142, 0.954367702893722)
    ctf.AddRGBPoint(0.4321287371255907, 0.6882, 0.93, 0.9179099999999999)
    ctf.AddRGBPoint(0.5, 0.8994959551205902, 0.944646394975174, 0.7686567142818399)
    ctf.AddRGBPoint(0.5882260353170073, 0.957107977357604, 0.8338185108985666, 0.5089156299842102)
    ctf.AddRGBPoint(0.7061412605695164, 0.9275207599610714, 0.6214389091739178, 0.31535705838676426)
    ctf.AddRGBPoint(0.8476395308725272, 0.8, 0.3520000000000001, 0.15999999999999998)
    ctf.AddRGBPoint(1, 0.59, 0.07670000000000013, 0.11947499999999994)

    return ctf


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


@dataclass(frozen=True)
class Mapper:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_MODE_DEFAULT: int = 0
        VTK_COLOR_MODE_MAP_SCALARS: int = 1
        VTK_COLOR_MODE_DIRECT_SCALARS: int = 2

    @dataclass(frozen=True)
    class ResolveCoincidentTopology:
        VTK_RESOLVE_OFF: int = 0
        VTK_RESOLVE_POLYGON_OFFSET: int = 1
        VTK_RESOLVE_SHIFT_ZBUFFER: int = 2

    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_DEFAULT: int = 0
        VTK_SCALAR_MODE_USE_POINT_DATA: int = 1
        VTK_SCALAR_MODE_USE_CELL_DATA: int = 2
        VTK_SCALAR_MODE_USE_POINT_FIELD_DATA: int = 3
        VTK_SCALAR_MODE_USE_CELL_FIELD_DATA: int = 4
        VTK_SCALAR_MODE_USE_FIELD_DATA: int = 5


if __name__ == '__main__':
    main()
