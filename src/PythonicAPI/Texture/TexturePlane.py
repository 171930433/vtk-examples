#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkPlaneSource
from vtkmodules.vtkIOImage import vtkImageReader2Factory
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTexture
)


def main():
    file_name = get_program_parameters()

    colors = vtkNamedColors()

    # Load in the texture map. A texture is any unsigned char image. If it
    # is not of this type, you will have to map it through a lookup table
    # or by using vtkImageShiftScale.
    #
    reader_factory = vtkImageReader2Factory()
    texture_file = reader_factory.CreateImageReader2(file_name)
    texture_file.file_name = file_name

    atext = vtkTexture(interpolate=True)
    texture_file >> atext

    # Create a plane source and actor. The vtkPlanesSource generates
    # texture coordinates.
    plane = vtkPlaneSource()

    plane_mapper = vtkPolyDataMapper()
    plane >> plane_mapper

    plane_actor = vtkActor(mapper=plane_mapper, texture=atext)

    # Create the RenderWindow, Renderer and Interactor.
    renderer = vtkRenderer(background=colors.GetColor3d('DarkSlateGray'))
    ren_win = vtkRenderWindow(size=(640, 480), window_name='TexturePlane')
    ren_win.AddRenderer(renderer)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Add the actors to the renderer, set the background and size.
    renderer.AddActor(plane_actor)

    # Render the image.
    ren_win.Render()

    renderer.ResetCamera()
    renderer.active_camera.Elevation(-30)
    renderer.active_camera.Roll(-20)
    renderer.ResetCameraClippingRange()
    ren_win.Render()
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'How to do basic texture mapping.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='masonry.bmp.')
    args = parser.parse_args()
    return args.filename


if __name__ == '__main__':
    main()
