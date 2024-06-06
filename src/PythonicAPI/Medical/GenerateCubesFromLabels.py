#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import (
    vtkDataObject,
    vtkDataSetAttributes
)
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import vtkThreshold
from vtkmodules.vtkFiltersGeneral import vtkTransformFilter
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkIOImage import vtkMetaImageReader
from vtkmodules.vtkImagingCore import vtkImageWrapPad
from vtkmodules.vtkInteractionWidgets import vtkCameraOrientationWidget
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    file_name, start_label, end_label = get_program_parameters()
    if start_label > end_label:
        end_label, start_label = start_label, end_label

    # Generate cubes from labels
    # 1) Read the meta file
    # 2) Convert point data to cell data
    # 3) Convert to geometry and display

    reader = vtkMetaImageReader(file_name=file_name)
    reader.update()

    # Pad the volume so that we can change the point data into cell
    # data.
    extent = reader.output.extent
    padded_extent = (extent[0], extent[1] + 1, extent[2], extent[3] + 1, extent[4], extent[5] + 1)
    pad = vtkImageWrapPad(output_whole_extent=padded_extent)
    (reader >> pad).update()

    # Copy the scalar point data of the volume into the scalar cell data
    pad.output.cell_data.SetScalars(reader.output.point_data.scalars)

    selector = vtkThreshold(input_array_to_process=(0, 0, 0,
                                                    vtkDataObject.FIELD_ASSOCIATION_CELLS,
                                                    vtkDataSetAttributes.SCALARS),
                            lower_threshold=start_label, upper_threshold=end_label)

    # Shift the geometry by 1/2
    transform = vtkTransform()
    transform.Translate(-0.5, -0.5, -0.5)

    transform_model = vtkTransformFilter(transform=transform)

    geometry = vtkGeometryFilter()

    mapper = vtkPolyDataMapper(scalar_range=(start_label, end_label),
                               scalar_mode=Mapper.ScalarMode.VTK_SCALAR_MODE_USE_CELL_DATA,
                               color_mode=Mapper.ColorMode.VTK_COLOR_MODE_MAP_SCALARS)
    pad >> selector >> transform_model >> geometry >> mapper

    actor = vtkActor(mapper=mapper)

    renderer = vtkRenderer(background=colors.GetColor3d('DarkSlateBlue'))
    render_window = vtkRenderWindow(size=(640, 480), window_name='GenerateCubesFromLabels')
    render_window.AddRenderer(renderer)

    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    renderer.AddActor(actor)

    render_window.Render()

    camera = renderer.GetActiveCamera()
    camera.position = (130.171200, 942.438334, -262.344068)
    camera.focal_point = (279.491372, 262.325784, 172.209964)
    camera.view_up = (0.235239, -0.486113, -0.841639)
    camera.distance = 820.784260
    camera.clipping_range = (224.710879, 1514.926115)

    omw = vtkCameraOrientationWidget(parent_renderer=renderer)
    # Enable the widget.
    omw.On()

    render_window_interactor.Start()


def get_program_parameters():
    import argparse
    description = 'Convert the point data from a labeled volume into cell data.'
    epilogue = '''
 The surfaces are displayed as vtkPolydata.
     '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='Input volume e.g. Frog/frogtissue.mhd.')
    parser.add_argument('startlabel', type=int, help='The starting label in the input volume, e,g, 1.')
    parser.add_argument('endlabel', type=int, help='The ending label in the input volume e.g. 29')
    args = parser.parse_args()
    return args.filename, args.startlabel, args.endlabel


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
