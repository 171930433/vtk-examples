#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkUnstructuredGridToExplicitStructuredGrid
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleRubberBandPick
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters(argv):
    import argparse
    description = 'Load an explicit structured grid from a file'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('fn', help='The explicit structured grid file name e.g. UNISIM-II-D.vtu.')
    args = parser.parse_args()
    return args.fn


def main(fn):
    reader = vtkXMLUnstructuredGridReader(file_name=fn)

    # global_warning_display=False hides VTK errors.
    converter = vtkUnstructuredGridToExplicitStructuredGrid(global_warning_display=False)
    input_arrays_to_process = ((0, 0, 0, 1, 'BLOCK_I'), (1, 0, 0, 1, 'BLOCK_J'), (2, 0, 0, 1, 'BLOCK_K'))
    for input_array in input_arrays_to_process:
        converter.SetInputArrayToProcess(*input_array)

    grid = (reader >> converter).update().output
    grid.ComputeFacesConnectivityFlagsArray()
    grid.cell_data.SetActiveScalars('ConnectivityFlags')

    scalars = grid.cell_data.GetArray('ConnectivityFlags')

    mapper = vtkDataSetMapper(color_mode=MapperColorMode.VTK_COLOR_MODE_MAP_SCALARS, scalar_range=scalars.range)

    actor = vtkActor(mapper=mapper)
    actor.property.EdgeVisibilityOn()

    grid >> mapper

    colors = vtkNamedColors()

    renderer = vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d('DimGray'))

    window = vtkRenderWindow()
    window.AddRenderer(renderer)
    window.SetWindowName('LoadESGrid')
    window.SetSize(1024, 768)
    window.Render()

    camera = renderer.GetActiveCamera()
    camera.SetPosition(312452.407650, 7474760.406373, 3507.364723)
    camera.SetFocalPoint(314388.388434, 7481520.509575, -2287.477388)
    camera.SetViewUp(0.089920, 0.633216, 0.768734)
    camera.SetDistance(9111.926908)
    camera.SetClippingRange(595.217338, 19595.429475)

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)
    interactor.SetInteractorStyle(vtkInteractorStyleRubberBandPick())
    window.Render()
    interactor.Start()


@dataclass(frozen=True)
class MapperColorMode:
    VTK_COLOR_MODE_DEFAULT: int = 0
    VTK_COLOR_MODE_MAP_SCALARS: int = 1
    VTK_COLOR_MODE_DIRECT_SCALARS: int = 2


if __name__ == '__main__':
    import sys

    fn = get_program_parameters(sys.argv)
    main(fn)
