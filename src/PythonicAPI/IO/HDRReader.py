##!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkIOImage import vtkHDRReader
from vtkmodules.vtkInteractionImage import vtkImageViewer
from vtkmodules.vtkRenderingCore import vtkRenderWindowInteractor


def get_program_parameters():
    import argparse
    description = 'Demonstrate the use of HDRReader'
    epilogue = '''
This example shows how to read in an HDR file.
A callback is used to print out the color window (move the mouse horizontally over the image)
 and color level (move the mouse vertically over the image).

   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('file_name', help='Path to the hdr file e.g. Skyboxes/spiaggia_di_mondello_1k.hdr.')
    args = parser.parse_args()
    return args.file_name


def main():
    file_name = get_program_parameters()

    reader = vtkHDRReader(file_name=file_name)

    # Check that the image can be read.
    if not reader.CanReadFile(file_name):
        print('CanReadFile failed for ', file_name)
        return
    reader.UpdateInformation()

    # Get the whole extent.
    we = reader.data_extent

    reader.UpdateExtent(we)
    size = (we[1] - we[0], we[3] - we[2])

    # Visualize
    image_viewer = vtkImageViewer(input_data=reader.update().output, color_window=1, color_level=1, position=(0, 100),
                                  size=size)
    image_viewer.render_window.window_name = 'HDRReader'

    iren = vtkRenderWindowInteractor()
    image_viewer.SetupInteractor(iren)
    image_viewer.Render()

    iren.AddObserver('EndInteractionEvent', ColorCallback(image_viewer))

    iren.Start()


class ColorCallback(object):
    def __init__(self, image_viewer):
        self.image_viewer = image_viewer

    def __call__(self, caller, ev):
        print(f'Color window: {self.image_viewer.color_window} level: {self.image_viewer.color_level}')


if __name__ == '__main__':
    main()
