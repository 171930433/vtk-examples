#!/usr/bin/env python3


# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkMarchingSquares
from vtkmodules.vtkFiltersGeneral import vtkContourTriangulator
from vtkmodules.vtkIOImage import vtkPNGReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Create a contour from a structured point set (image) and triangulate it.'
    epilogue = '''
    Try with different iso values e.g. -i1000.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)
    parser.add_argument('file_name', help='The path to the image file to use e.g fullhead15.png.')
    parser.add_argument('-i', '--iso_value', help='The contour value for generating the isoline.', default=500,
                        type=int)
    args = parser.parse_args()
    return args.file_name, args.iso_value


def main():
    file_name, iso_value = get_program_parameters()

    colors = vtkNamedColors()

    reader = vtkPNGReader(file_name=file_name)
    if not reader.CanReadFile(file_name):
        print('Error: Could not read', file_name)
        return

    iso = vtkMarchingSquares(value=(0, iso_value))
    reader >> iso

    iso_mapper = vtkDataSetMapper(scalar_visibility=False)
    iso >> iso_mapper

    iso_actor = vtkActor(mapper=iso_mapper)
    iso_actor.property.color = colors.GetColor3d('MediumOrchid')

    poly = vtkContourTriangulator()

    poly_mapper = vtkDataSetMapper(scalar_visibility=False)
    poly_mapper.SetInputConnection(poly.GetOutputPort())
    iso >> poly >> poly_mapper

    poly_actor = vtkActor(mapper=poly_mapper)
    poly_actor.property.color = colors.GetColor3d('Gray')

    # Standard rendering classes.
    renderer = vtkRenderer(background=colors.GetColor3d('DarkSlateGray'))
    ren_win = vtkRenderWindow(size=(300, 300), window_name='ContourTriangulator',
                              multi_samples=0)
    ren_win.AddRenderer(renderer)

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    renderer.AddActor(poly_actor)
    renderer.AddActor(iso_actor)

    camera = renderer.active_camera
    renderer.ResetCamera()
    camera.Azimuth(180)

    ren_win.Render()
    iren.Initialize()
    iren.Start()


if __name__ == '__main__':
    main()
