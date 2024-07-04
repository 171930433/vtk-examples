#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingContextOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOImage import vtkDICOMImageReader
from vtkmodules.vtkInteractionImage import vtkImageViewer2
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleImage
from vtkmodules.vtkRenderingCore import (
    vtkActor2D,
    vtkRenderWindowInteractor,
    vtkTextMapper,
    vtkTextProperty
)


def get_program_parameters():
    import argparse
    description = 'Read DICOM series data.'
    epilogue = '''
    Obtain and unzip DicomTestImages.zip.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('dirname', help='DicomTestImages.zip')
    args = parser.parse_args()
    return args.dirname


def main():
    colors = vtkNamedColors()

    folder = get_program_parameters()

    # Read all the DICOM files in the specified directory.
    reader = vtkDICOMImageReader(directory_name=folder)
    reader.update()

    # Visualize
    image_viewer = vtkImageViewer2(input_connection=reader.output_port)

    slice_text_prop = vtkTextProperty(font_size=20, font_family=TextProperty.FontFamily.VTK_COURIER,
                                      vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_BOTTOM,
                                      justification=TextProperty.Justification.VTK_TEXT_LEFT)
    # Slice status message.
    msg = StatusMessage.format(image_viewer.GetSliceMin(), image_viewer.GetSliceMax())
    slice_text_mapper = vtkTextMapper(text_property=slice_text_prop, input=msg)

    slice_text_actor = vtkActor2D(mapper=slice_text_mapper, position=(15, 10))

    # Usage hint message.
    usage_text_prop = vtkTextProperty(font_size=14, font_family=TextProperty.FontFamily.VTK_COURIER,
                                      vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_TOP,
                                      justification=TextProperty.Justification.VTK_TEXT_LEFT)
    usage_msg = ('- Slice with mouse wheel\n  or Up/Down-Key\n- Zoom with pressed right\n'
                 '  mouse button while dragging')
    usage_text_mapper = vtkTextMapper(input=usage_msg)
    usage_text_mapper.SetTextProperty(usage_text_prop)

    usage_text_actor = vtkActor2D(mapper=usage_text_mapper)
    usage_text_actor.position_coordinate.coordinate_system = Coordinate.CoordinateSystem.VTK_NORMALIZED_DISPLAY
    usage_text_actor.position_coordinate.value = (0.05, 0.95)

    # Create an interactor with our own style (inherit from
    # vtkInteractorStyleImage) in order to catch mousewheel and key events.
    render_window_interactor = vtkRenderWindowInteractor()
    my_interactor_style = MyVtkInteractorStyleImage()

    # Make imageviewer2 and sliceTextMapper visible to our interactorstyle
    # to enable slice status message updates when  scrolling through the slices.
    my_interactor_style.set_image_viewer(image_viewer)
    my_interactor_style.set_status_mapper(slice_text_mapper)

    # Make the interactor use our own interactor style
    # because SetupInteractor() is defining it's own default interator style
    # this must be called after SetupInteractor().
    # renderWindowInteractor.SetInteractorStyle(myInteractorStyle);
    image_viewer.SetupInteractor(render_window_interactor)
    render_window_interactor.interactor_style = my_interactor_style
    render_window_interactor.Render()

    # Add slice status message and usage hint message to the renderer.
    image_viewer.renderer.AddActor2D(slice_text_actor)
    image_viewer.renderer.AddActor2D(usage_text_actor)

    # Initialize rendering and interaction.
    image_viewer.Render()
    image_viewer.renderer.ResetCamera()
    image_viewer.renderer.background = colors.GetColor3d('SlateGray')
    image_viewer.render_window.size = (800, 800)
    image_viewer.render_window.window_name = 'ReadDICOMSeries'
    image_viewer.Render()
    render_window_interactor.Start()


# Helper class to format the slice status message.
class StatusMessage:
    @staticmethod
    def format(current_slice: int, max_slice: int):
        return f'Slice Number {current_slice + 1}/{max_slice + 1}'


# Define our own interaction style.
class MyVtkInteractorStyleImage(vtkInteractorStyleImage):
    def __init__(self, parent=None):
        super().__init__()
        self.AddObserver('KeyPressEvent', self.key_press_event)
        self.AddObserver('MouseWheelForwardEvent', self.mouse_wheel_forward_event)
        self.AddObserver('MouseWheelBackwardEvent', self.mouse_wheel_backward_event)
        self.image_viewer = None
        self.status_mapper = None
        self.slice = 0
        self.min_slice = 0
        self.max_slice = 0

    def set_image_viewer(self, image_viewer):
        self.image_viewer = image_viewer
        self.min_slice = image_viewer.slice_min
        self.max_slice = image_viewer.slice_max
        self.slice = self.min_slice
        print(f'Slicer: Min = {self.min_slice}, Max= {self.max_slice}')

    def set_status_mapper(self, status_mapper):
        self.status_mapper = status_mapper

    def move_slice_forward(self):
        if self.slice < self.max_slice:
            self.slice += 1
            print(f'MoveSliceForward::Slice = {self.slice}')
            self.image_viewer.SetSlice(self.slice)
            msg = StatusMessage.format(self.slice, self.max_slice)
            self.status_mapper.SetInput(msg)
            self.image_viewer.Render()

    def move_slice_backward(self):
        if self.slice > self.min_slice:
            self.slice -= 1
            print(f'MoveSliceBackward::Slice = {self.slice}')
            self.image_viewer.SetSlice(self.slice)
            msg = StatusMessage.format(self.slice, self.max_slice)
            self.status_mapper.SetInput(msg)
            self.image_viewer.Render()

    def key_press_event(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        if key == 'Up':
            self.move_slice_forward()
        elif key == 'Down':
            self.move_slice_backward()

    def mouse_wheel_forward_event(self, obj, event):
        self.move_slice_forward()

    def mouse_wheel_backward_event(self, obj, event):
        self.move_slice_backward()


@dataclass(frozen=True)
class Coordinate:
    @dataclass(frozen=True)
    class CoordinateSystem:
        VTK_DISPLAY: int = 0
        VTK_NORMALIZED_DISPLAY: int = 1
        VTK_VIEWPORT: int = 2
        VTK_NORMALIZED_VIEWPORT: int = 3
        VTK_VIEW: int = 4
        VTK_POSE: int = 5
        VTK_WORLD: int = 6
        VTK_USERDEFINED: int = 7


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
