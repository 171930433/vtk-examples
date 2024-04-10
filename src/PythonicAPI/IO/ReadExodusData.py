#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersGeometry import vtkCompositeDataGeometryFilter
from vtkmodules.vtkIOExodus import vtkExodusIIReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Read and display ExodusII data.'
    epilogue = '''
There are two nodal variables in mug.e: "convected" and "diffused".
Try "diffused" and see the difference.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='A required filename e.g mug.e.')
    parser.add_argument('nodal_var', help='The nodal variable e.g. convected.')
    args = parser.parse_args()
    return args.filename, args.nodal_var


def main():
    colors = vtkNamedColors()

    # Input file and variable
    filename, nodal_var = get_program_parameters()

    # Read Exodus Data.
    reader = vtkExodusIIReader(file_name=filename, time_step=10)
    reader.UpdateInformation()
    # This enables all NODAL values.
    reader.all_array_status = (vtkExodusIIReader.NODAL, 1)
    # Uncomment this to print the file information.
    # print(reader)

    # Create the geometry.
    geometry = vtkCompositeDataGeometryFilter()

    # Mapper
    mapper = vtkPolyDataMapper(scalar_mode=Mapper.ScalarMode.VTK_SCALAR_MODE_USE_POINT_FIELD_DATA,
                               interpolate_scalars_before_mapping=True)
    mapper.SelectColorArray(nodal_var)
    reader >> geometry >> mapper
    # Actor
    actor = vtkActor(mapper=mapper)
    actor.SetMapper(mapper)

    # Renderer
    renderer = vtkRenderer(background=colors.GetColor3d('DimGray'))
    renderer.AddViewProp(actor)

    renderer.GetActiveCamera().SetPosition(9.0, 9.0, 7.0)
    renderer.GetActiveCamera().SetFocalPoint(0, 0, 0)
    renderer.GetActiveCamera().SetViewUp(0.2, -0.7, 0.7)
    renderer.GetActiveCamera().SetDistance(14.5)

    # Window and Interactor
    window = vtkRenderWindow(size=(600, 600), window_name='ReadExodusData')
    window.AddRenderer(renderer)

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)
    interactor.Initialize()

    # Show the result
    window.Render()
    interactor.Start()


@dataclass(frozen=True)
class Mapper:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_MODE_DEFAULT: int = 0
        VTK_COLOR_MODE_MAP_SCALARS: int = 1
        VTK_COLOR_MODE_DIRECT_SCALARS: int = 2

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
