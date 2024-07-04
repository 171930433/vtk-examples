#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingFreeType
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkPolyData
)
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import (
    vtkAppendPolyData,
    vtkContourFilter
)
from vtkmodules.vtkFiltersGeneral import (
    vtkTransformFilter,
    vtkTransformPolyDataFilter,
    vtkWarpTo
)
from vtkmodules.vtkFiltersHybrid import vtkImplicitModeller
from vtkmodules.vtkFiltersModeling import vtkRotationalExtrusionFilter
from vtkmodules.vtkFiltersSources import (
    vtkConeSource,
    vtkCubeSource,
    vtkSphereSource
)
from vtkmodules.vtkRenderingCore import (
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty
)
from vtkmodules.vtkRenderingLOD import vtkLODActor


def main():
    colors = vtkNamedColors()

    # Set the colors.
    colors.SetColor('AzimuthArrowColor', 255, 77, 77, 255)
    colors.SetColor('ElevationArrowColor', 77, 255, 77, 255)
    colors.SetColor('RollArrowColor', 255, 255, 77, 255)
    colors.SetColor('SpikeColor', 255, 77, 255, 255)
    colors.SetColor("UpSpikeColor", 77, 255, 255, 255)
    colors.SetColor('BkgColor', 26, 51, 102, 255)

    # Create a rendering window, renderer and interactor.
    ren = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='CameraModel1')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    # Create a camera model.
    cam_cs = vtkConeSource(height=1.5, resolution=12, radius=0.4)
    cam_cbs = vtkCubeSource(center=(0.4, 0, 0), x_length=1.5, z_length=0.8)
    cam_apd = vtkAppendPolyData()
    cam_mapper = vtkPolyDataMapper()
    (cam_cbs, cam_cs) >> cam_apd >> cam_mapper
    cam_actor = vtkLODActor(mapper=cam_mapper, scale=(2, 2, 2))

    # Draw the arrows.
    pd = vtkPolyData()
    ca = vtkCellArray()
    fp = vtkPoints()
    fp.InsertNextPoint(0, 1, 0)
    fp.InsertNextPoint(8, 1, 0)
    fp.InsertNextPoint(8, 2, 0)
    fp.InsertNextPoint(10, 0.01, 0)
    fp.InsertNextPoint(8, -2, 0)
    fp.InsertNextPoint(8, -1, 0)
    fp.InsertNextPoint(0, -1, 0)
    ca.InsertNextCell(7)
    ca.InsertCellPoint(0)
    ca.InsertCellPoint(1)
    ca.InsertCellPoint(2)
    ca.InsertCellPoint(3)
    ca.InsertCellPoint(4)
    ca.InsertCellPoint(5)
    ca.InsertCellPoint(6)
    pd.SetPoints(fp)
    pd.SetPolys(ca)

    pd2 = vtkPolyData()
    ca2 = vtkCellArray()
    fp2 = vtkPoints()
    fp2.InsertNextPoint(0, 1, 0)
    fp2.InsertNextPoint(8, 1, 0)
    fp2.InsertNextPoint(8, 2, 0)
    fp2.InsertNextPoint(10, 0.01, 0)
    ca2.InsertNextCell(4)
    ca2.InsertCellPoint(0)
    ca2.InsertCellPoint(1)
    ca2.InsertCellPoint(2)
    ca2.InsertCellPoint(3)
    pd2.SetPoints(fp2)
    pd2.SetLines(ca2)

    arrow_im = vtkImplicitModeller(input_data=pd, sample_dimensions=(50, 20, 8))
    arrow_cf = vtkContourFilter()
    arrow_cf.SetValue(0, 0.2)
    arrow_wt = vtkWarpTo(position=(5, 0, 5), scale_factor=0.85, absolute=True)

    arrow_t = vtkTransform()
    arrow_t.RotateY(60)
    arrow_t.Translate(-1.33198, 0, -1.479)
    arrow_t.Scale(1, 0.5, 1)

    arrow_tf = vtkTransformFilter(transform=arrow_t)

    arrow_mapper = vtkDataSetMapper(scalar_visibility=False)
    arrow_im >> arrow_cf >> arrow_wt >> arrow_tf >> arrow_mapper

    # Draw the azimuth arrows.
    arrow1_property = vtkProperty(color=colors.GetColor3d('AzimuthArrowColor'),
                                  specular_color=colors.GetColor3d('White'),
                                  specular=0.3, specular_power=20, ambient=0.2, diffuse=0.8)
    a1_actor = vtkLODActor(mapper=arrow_mapper, position=(1, 0, -1), property=arrow1_property)
    a1_actor.RotateZ(180)
    a2_actor = vtkLODActor(mapper=arrow_mapper, position=(1, 0, 1), property=arrow1_property)
    a2_actor.RotateZ(180)
    a2_actor.RotateX(180)

    # Draw the elevation arrows.
    arrow2_property = vtkProperty(color=colors.GetColor3d('ElevationArrowColor'),
                                  specular_color=colors.GetColor3d('White'),
                                  specular=0.3, specular_power=20, ambient=0.2, diffuse=0.8)
    a3_actor = vtkLODActor(mapper=arrow_mapper, position=(1, -1, 0), property=arrow2_property)
    a3_actor.RotateZ(180)
    a3_actor.RotateX(90)
    a4_actor = vtkLODActor(mapper=arrow_mapper, position=(1, 1, 0), property=arrow2_property)
    a4_actor.RotateZ(180)
    a4_actor.RotateX(-90)

    # Draw the DOP.
    arrow_t2 = vtkTransform()
    arrow_t2.Scale(1, 0.6, 1)
    arrow_t2.RotateY(90)
    arrow_tf2 = vtkTransformPolyDataFilter(transform=arrow_t2)
    arrow_ref = vtkRotationalExtrusionFilter(capping=False, resolution=30)
    spike_mapper = vtkPolyDataMapper()
    pd2 >> arrow_tf2 >> arrow_ref >> spike_mapper
    spike_property = vtkProperty(color=colors.GetColor3d('SpikeColor'),
                                 specular_color=colors.GetColor3d('White'),
                                 ambient=0.2, diffuse=0.8)
    a5_actor = vtkLODActor(mapper=spike_mapper, scale=(0.3, 0.3, 0.6), position=(-2, 0, 0), property=spike_property)
    a5_actor.RotateY(90)
    a5_actor.SetPosition(-2, 0, 0)

    up_spike_property = vtkProperty(color=colors.GetColor3d('UpSpikeColor'),
                                    specular_color=colors.GetColor3d('White'),
                                    specular=0.3, specular_power=20, ambient=0.2, diffuse=0.8)
    a7_actor = vtkLODActor(mapper=spike_mapper, scale=(0.2, 0.2, 0.7), position=(1, 0, 0), property=up_spike_property)
    a7_actor.RotateZ(90)
    a7_actor.RotateY(-90)

    # Focal point.
    fps = vtkSphereSource(radius=0.5)
    fps.SetRadius(0.5)
    fp_mapper = vtkPolyDataMapper()
    fps >> fp_mapper
    fp_property = vtkProperty(color=colors.GetColor3d('White'),
                              specular_color=colors.GetColor3d('White'),
                              specular=0.3, specular_power=20, ambient=0.2, diffuse=0.8)
    fp_actor = vtkLODActor(mapper=fp_mapper, scale=(1, 1, 1), position=(-9, 0, 0), property=fp_property)

    # Create the roll arrow.
    arrow_wt2 = vtkWarpTo(position=(5, 0, 2.5), scale_factor=0.95, absolute=True)

    arrow_t3 = vtkTransform()
    arrow_t3.Translate(-2.50358, 0, -1.70408)
    arrow_t3.Scale(0.5, 0.3, 1)

    arrow_tf3 = vtkTransformFilter(transform=arrow_t3)

    arrow_mapper2 = vtkDataSetMapper(scalar_visibility=False)
    arrow_im >> arrow_cf >> arrow_wt2 >> arrow_tf3 >> arrow_mapper2

    # Draw the roll arrow.
    arrow6_property = vtkProperty(color=colors.GetColor3d('RollArrowColor'),
                                  specular_color=colors.GetColor3d('White'),
                                  specular=0.3, specular_power=20, ambient=0.2, diffuse=0.8)
    a6_actor = vtkLODActor(mapper=arrow_mapper2, scale=(1.5, 1.5, 1.5), position=(-4, 0, 0), property=arrow6_property)
    a6_actor.RotateZ(90)

    # Add the actors to the renderer, set the background and size.
    ren.AddActor(cam_actor)
    ren.AddActor(a1_actor)
    ren.AddActor(a2_actor)
    ren.AddActor(a3_actor)
    ren.AddActor(a4_actor)
    ren.AddActor(a5_actor)
    ren.AddActor(a6_actor)
    ren.AddActor(a7_actor)
    ren.AddActor(fp_actor)
    ren.SetBackground(colors.GetColor3d('BkgColor'))
    ren.SetBackground(colors.GetColor3d('SlateGray'))
    ren_win.SetSize(640, 480)
    ren_win.SetWindowName('CameraModel1')

    # Render the image.

    cam1 = ren.active_camera
    ren.ResetCamera()
    cam1.Azimuth(150)
    cam1.Elevation(30)
    cam1.Dolly(1.5)
    ren.ResetCameraClippingRange()

    # Create a TextActor for azimuth  (a1 and a2 actor's color).
    text = get_text_actor('Azimuth', (20, 50), a1_actor.property.color)
    ren.AddActor2D(text)

    # Create a TextActor for elevation  (a3 and a4 actor's color).
    text2 = get_text_actor('Elevation', (20, 100), a3_actor.property.color)
    ren.AddActor2D(text2)

    # Create a TextActor for roll (a6 actor's color).
    text3 = get_text_actor('Roll', (20, 150), a6_actor.property.color)
    ren.AddActor2D(text3)

    iren.Initialize()
    iren.Start()


def get_text_actor(text_str, position, color):
    tprop = vtkTextProperty(font_family=TextProperty.FontFamily.VTK_ARIAL, shadow=False, line_spacing=1.0, font_size=36,
                            color=color)
    return vtkTextActor(input=text_str, display_position=position, text_property=tprop)


@dataclass(frozen=True)
class TextProperty:
    @dataclass(frozen=True)
    class FontFamily:
        VTK_ARIAL: int = 0
        VTK_COURIER: int = 1
        VTK_TIMES: int = 2
        VTK_UNKNOWN_FONT: int = 3

    @dataclass(frozen=True)
    class Justification:
        VTK_TEXT_LEFT: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_RIGHT: int = 2

    @dataclass(frozen=True)
    class VerticalJustification:
        VTK_TEXT_BOTTOM: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_TOP: int = 2


if __name__ == '__main__':
    main()
