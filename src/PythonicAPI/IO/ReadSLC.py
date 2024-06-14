#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkIOImage import vtkSLCReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    input_filename, iso_value = get_program_parameters()

    colors = vtkNamedColors()

    # vtkSLCReader to read.
    reader = vtkSLCReader(file_name=input_filename)

    # Create a mapper.
    mapper = vtkPolyDataMapper()
    reader >> mapper

    # Create the surface using a vtkContourFilter object.
    contour_filter = vtkContourFilter()
    # Change the range(2nd and 3rd Parameter) based on your
    # requirement. The recommended value for 1st parameter is greater than 1
    # contour_filter.GenerateValues(5, 80.0, 100.0)
    contour_filter.SetValue(0, iso_value)

    mapper = vtkPolyDataMapper(scalar_visibility=False)
    reader >> contour_filter >> mapper

    actor = vtkActor(mapper=mapper)
    actor.SetMapper(mapper)
    actor.GetProperty().SetDiffuse(0.8)
    actor.GetProperty().SetDiffuseColor(colors.GetColor3d('Ivory'))
    actor.GetProperty().SetSpecular(0.8)
    actor.GetProperty().SetSpecularPower(120.0)

    # Do an outline.
    outliner = vtkOutlineFilter()
    outline_mapper = vtkPolyDataMapper()
    reader >> outliner >> outline_mapper
    outline_actor = vtkActor(mapper=outline_mapper)
    outline_actor.property.color = colors.GetColor3d('MistyRose')

    # Create a renderer, rendering window and interactor.
    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    render_window = vtkRenderWindow(size=(640, 512), window_name='ReadSLC')
    render_window.AddRenderer(renderer)
    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.render_window = render_window

    # Assign actor to the renderer.
    renderer.AddActor(actor)
    renderer.AddActor(outline_actor)

    # Pick a good view
    cam1 = renderer.GetActiveCamera()
    cam1.focal_point = (0.0, 0.0, 0.0)
    cam1.position = (0.0, -1.0, 0.0)
    cam1.view_up = (0.0, 0.0, -1.0)
    cam1.Azimuth(-90.0)
    renderer.ResetCamera()
    renderer.ResetCameraClippingRange()

    render_window.Render()

    # Enable user interface interactor.
    render_window_interactor.Initialize()
    render_window.Render()
    render_window_interactor.Start()


def get_program_parameters():
    import argparse
    description = 'Read a .slc file.'
    epilogue = ''''''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='vw_knee.slc.')
    parser.add_argument('iso_value', nargs='?', type=float, default=72.0, help='Defaullt 72.')
    args = parser.parse_args()
    return args.filename, args.iso_value


if __name__ == '__main__':
    main()
