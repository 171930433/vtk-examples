#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersGeneral import vtkWarpVector
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkIOLegacy import vtkPolyDataReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Produces figure 6-14(a) Beam displacement from the VTK Textbook.'
    epilogue = '''
        Produce figure 6–14(a) Beam displacement from the VTK Textbook..
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)
    parser.add_argument('filename', help='plate.vtk')
    args = parser.parse_args()
    return args.filename


def main():
    file_name = get_program_parameters()

    colors = vtkNamedColors()

    # Set the colors.
    colors.SetColor('PlateColor', 255, 160, 140, 255)
    colors.SetColor('BkgColor', 65, 99, 149, 255)

    # Read a vtk file.
    plate = vtkPolyDataReader(file_name=file_name, vectors_name='mode2')

    warp = vtkWarpVector(scale_factor=0.5)

    plate_mapper = vtkDataSetMapper()
    plate >> warp >> plate_mapper

    plate_actor = vtkActor(mapper=plate_mapper)
    plate_actor.property.color = colors.GetColor3d('PlateColor')
    plate_actor.RotateX(-90)

    # Create the outline.
    outline = vtkOutlineFilter()
    outline_mapper = vtkPolyDataMapper()
    plate >> outline >> outline_mapper
    
    outline_actor = vtkActor(mapper=outline_mapper)
    outline_actor.RotateX(-90)
    outline_actor.property.color = colors.GetColor3d('White')

    # Create the RenderWindow, Renderer and Interactor.
    ren = vtkRenderer(background=colors.GetColor3d('BkgColor'))
    ren_win = vtkRenderWindow(size=(500, 500), window_name='PlateVibration')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Add the actors to the renderer.
    ren.AddActor(plate_actor)
    ren.AddActor(outline_actor)

    # Render the image.
    ren_win.Render()
    # This closely matches the original illustration.
    ren.active_camera.position = (-3.7, 13, 15.5)
    ren.ResetCameraClippingRange()

    ren_win.Render()

    iren.Start()


if __name__ == '__main__':
    main()
