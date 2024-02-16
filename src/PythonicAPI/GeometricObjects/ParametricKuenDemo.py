#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonComputationalGeometry import vtkParametricKuen
from vtkmodules.vtkCommonCore import (
    vtkCommand,
    vtkMath
)
from vtkmodules.vtkFiltersSources import vtkParametricFunctionSource
from vtkmodules.vtkInteractionWidgets import (
    vtkSliderRepresentation2D,
    vtkSliderWidget
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    colors.SetColor('BkgColor', [26, 51, 102, 255])

    # Create a parametric function source, renderer, mapper, and actor
    surface = vtkParametricKuen(minimum_u=-4.5, maximum_u=4.5, minimum_v=0.05, maximum_v=vtkMath.Pi() - .05)
    source = vtkParametricFunctionSource(parametric_function=surface)
    mapper = vtkPolyDataMapper()
    source >> mapper

    back_property = vtkProperty(color=colors.GetColor3d('Tomato'))

    actor = vtkActor(mapper=mapper, backface_property=back_property)
    actor.property.diffuse_color = colors.GetColor3d('Banana')
    actor.property.specular = 0.5
    actor.property.specular_power = 20

    renderer = vtkRenderer(background=colors.GetColor3d('BkgColor'))
    renderer.AddActor(actor)

    render_window = vtkRenderWindow(size=(640, 480), window_name='ParametricKuenDemo')
    render_window.AddRenderer(renderer)

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Setup a slider widget for each varying parameter.
    slider_dimensions = {'tube_width': 0.008, 'slider_length': 0.008, 'title_height': 0.02, 'label_height': 0.02}
    slider_range_name = {'minimum_value': -4.5, 'maximum_value': 4.5, 'value': -4.5, 'title_text': 'U min'}
    slider_position = {'point1': (0.1, 0.1), 'point2': (.9, .1)}
    slider_widget_minimum_u = make_slider_widget(slider_dimensions, slider_range_name, slider_position, interactor)
    slider_widget_minimum_u.AddObserver('InteractionEvent', SliderCallbackMinimumU(surface))

    slider_range_name = {'minimum_value': -4.5, 'maximum_value': 4.5, 'value': 4.5, 'title_text': 'U max'}
    slider_position = {'point1': (0.1, 0.9), 'point2': (0.9, 0.9)}
    slider_widget_maximum_u = make_slider_widget(slider_dimensions, slider_range_name, slider_position, interactor)
    slider_widget_maximum_u.AddObserver('InteractionEvent', SliderCallbackMaximumU(surface))

    slider_range_name = {'minimum_value': 0.05, 'maximum_value': vtkMath.Pi(), 'value': 0.0, 'title_text': 'V min'}
    slider_position = {'point1': (0.1, 0.1), 'point2': (0.1, 0.9)}
    slider_widget_minimum_v = make_slider_widget(slider_dimensions, slider_range_name, slider_position, interactor)
    slider_widget_minimum_v.AddObserver(vtkCommand.InteractionEvent, SliderCallbackMinimumV(surface))

    slider_range_name = {'minimum_value': -0.05, 'maximum_value': vtkMath.Pi() - 0.5, 'value': vtkMath.Pi(), 'title_text': 'V max'}
    slider_position = {'point1': (0.9, 0.1), 'point2': (0.9, 0.9)}
    slider_widget_maximum_v = make_slider_widget(slider_dimensions, slider_range_name, slider_position, interactor)
    slider_widget_maximum_v.AddObserver(vtkCommand.InteractionEvent, SliderCallbackMaximumV(surface))

    render_window.Render()
    renderer.active_camera.Azimuth(60)
    renderer.active_camera.Elevation(-60)
    renderer.active_camera.Zoom(0.9)
    renderer.ResetCameraClippingRange()

    interactor.Initialize()
    interactor.Start()


def make_slider_widget(slider_dimensions, slider_range_name, slider_position, interactor):
    """
    Make a slider widget.
    :param slider_dimensions: Dimensions of the slider.
    :param slider_range_name: Slider range and name.
    :param slider_position: The position of the slider.
    :param interactor: The vtkInteractor.
    :return: The slider widget.
    """

    slider_rep = vtkSliderRepresentation2D(minimum_value=slider_range_name['minimum_value'],
                                           maximum_value=slider_range_name['maximum_value'],
                                           value=slider_range_name['value'],
                                           title_text=slider_range_name['title_text'],
                                           tube_width=slider_dimensions['tube_width'],
                                           slider_length=slider_dimensions['slider_length'],
                                           title_height=slider_dimensions['title_height'],
                                           label_height=slider_dimensions['label_height'],
                                           )

    slider_rep.point1_coordinate.SetCoordinateSystemToNormalizedDisplay()
    slider_rep.point1_coordinate.value = slider_position['point1']
    slider_rep.point2_coordinate.SetCoordinateSystemToNormalizedDisplay()
    slider_rep.point2_coordinate.value = slider_position['point2']

    slider = vtkSliderWidget(representation=slider_rep)
    slider.SetInteractor(interactor)
    slider.SetAnimationModeToAnimate()
    slider.EnabledOn()

    return slider


# These callbacks do the actual work.
# Callbacks for the interactions
class SliderCallbackMinimumU():
    def __init__(self, kuen):
        self.kuen = kuen

    def __call__(self, caller, ev):
        sliderWidget = caller
        value = sliderWidget.representation.value
        if value > 0.9 * self.kuen.GetMaximumU():
            value = 0.99 * self.kuen.GetMaximumU()
            sliderWidget.GetRepresentation().SetValue(value)
        self.kuen.minimum_u = value


class SliderCallbackMaximumU():
    def __init__(self, kuen):
        self.kuen = kuen

    def __call__(self, caller, ev):
        sliderWidget = caller
        value = sliderWidget.representation.value
        if value < self.kuen.GetMinimumU() + .01:
            value = self.kuen.GetMinimumU() + .01
            sliderWidget.GetRepresentation().SetValue(value)
        self.kuen.maximum_u = value


class SliderCallbackMinimumV():
    def __init__(self, kuen):
        self.kuen = kuen

    def __call__(self, caller, ev):
        sliderWidget = caller
        value = sliderWidget.representation.value
        if value > 0.9 * self.kuen.GetMaximumV():
            value = 0.99 * self.kuen.GetMaximumV()
            sliderWidget.GetRepresentation().SetValue(value)
        self.kuen.minimum_v = value


class SliderCallbackMaximumV():
    def __init__(self, kuen):
        self.kuen = kuen

    def __call__(self, caller, ev):
        slider_widget = caller
        value = slider_widget.representation.value
        if value < self.kuen.GetMinimumV() + .01:
            value = self.kuen.GetMinimumV() + .01
            slider_widget.GetRepresentation().SetValue(value)
        self.kuen.maximum_v = value


if __name__ == '__main__':
    main()
