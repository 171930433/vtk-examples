#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkSuperquadricSource
from vtkmodules.vtkIOImage import vtkJPEGReader
from vtkmodules.vtkImagingSources import vtkImageCanvasSource2D
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkImageSlice,
    vtkImageSliceMapper,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def get_program_parameters():
    import argparse
    description = 'Add a background image to a render window.'
    epilogue = '''
        Add a background image to a render window.
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)
    parser.add_argument('-f', '--filename', default=None,
                        help='An optional filename e.g. Gourds2.jpg.')
    args = parser.parse_args()
    return args.filename


def main():
    colors = vtkNamedColors()

    #  Verify input arguments0
    fn = get_program_parameters()
    if fn:
        # Read the image.
        jpeg_reader = vtkJPEGReader(file_name=fn)
        if not jpeg_reader.CanReadFile(fn):
            print('Error reading file:', fn)
            return
        image_data = jpeg_reader.update().output
    else:
        canvas_source = vtkImageCanvasSource2D(extent=(0, 100, 0, 100, 0, 0), number_of_scalar_components=3,
                                               scalar_type=ImageCanvasSource2D.ScalarType.VTK_UNSIGNED_CHAR)
        # Do the drawing.
        canvas_source.SetDrawColor(colors.GetColor4ub('warm_grey'))
        canvas_source.FillBox(0, 100, 0, 100)
        canvas_source.SetDrawColor(colors.GetColor4ub('DarkCyan'))
        canvas_source.FillTriangle(10, 10, 25, 10, 25, 25)
        canvas_source.SetDrawColor(colors.GetColor4ub('LightCoral'))
        canvas_source.FillTube(75, 75, 0, 75, 5.0)
        image_data = canvas_source.update().output

    # Create an image actor to display the image.
    image_mapper = vtkImageSliceMapper()
    image_slice = vtkImageSlice(mapper=image_mapper)
    image_data >> image_mapper

    # Create a superquadric
    superquadric_source = vtkSuperquadricSource(phi_roundness=1.1, theta_roundness=0.2)

    # Create a mapper and actor
    superquadric_mapper = vtkPolyDataMapper()
    superquadric_actor = vtkActor(mapper=superquadric_mapper)
    superquadric_actor.property.color = colors.GetColor3d('NavajoWhite')

    superquadric_source >> superquadric_mapper

    # Set up the render window and renderers such that there is
    # a background layer and a foreground layer
    # Create a renderer to display the image in the background.
    background_renderer = vtkRenderer(layer=0, interactive=False)
    #  Render the scene in the next layer.
    scene_renderer = vtkRenderer(layer=1)

    # Add actors to the renderers
    scene_renderer.AddActor(superquadric_actor)
    background_renderer.AddActor(image_slice)

    render_window = vtkRenderWindow(number_of_layers=2)
    render_window.AddRenderer(background_renderer)
    render_window.AddRenderer(scene_renderer)
    render_window.SetWindowName('BackgroundImage')

    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Render once to figure out where the background camera will be.
    render_window.Render()

    # Set up the background camera to fill the renderer with the image.
    origin = image_data.origin
    spacing = image_data.spacing
    extent = image_data.extent

    camera = background_renderer.GetActiveCamera()
    camera.ParallelProjectionOn()

    xc = origin[0] + 0.5 * (extent[0] + extent[1]) * spacing[0]
    yc = origin[1] + 0.5 * (extent[2] + extent[3]) * spacing[1]
    # xd = (extent[1] - extent[0] + 1) * spacing[0]
    yd = (extent[3] - extent[2] + 1) * spacing[1]
    d = camera.GetDistance()
    camera.SetParallelScale(0.5 * yd)
    camera.SetFocalPoint(xc, yc, 0.0)
    camera.SetPosition(xc, yc, d)

    # Render again to set the correct view.
    render_window.Render()

    # Interact with the window.
    render_window_interactor.Start()


@dataclass(frozen=True)
class ImageCanvasSource2D:
    @dataclass(frozen=True)
    class ScalarType:
        VTK_CHAR: int = 2
        VTK_UNSIGNED_CHAR: int = 3
        VTK_SHORT: int = 4
        VTK_UNSIGNED_SHORT: int = 5
        VTK_INT: int = 6
        VTK_UNSIGNED_INT: int = 7
        VTK_LONG: int = 8
        VTK_UNSIGNED_LONG: int = 9
        VTK_FLOAT: int = 10
        VTK_DOUBLE: int = 11


if __name__ == '__main__':
    main()
