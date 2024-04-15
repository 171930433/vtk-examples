#!/usr/bin/env python3

from dataclasses import dataclass

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

    colors.SetColor('BkgColor', (26, 51, 102, 255))

    # Create a parametric function source, renderer, mapper, and actor
    surface = vtkParametricKuen(minimum_u=-4.5, maximum_u=4.5, minimum_v=0.05, maximum_v=vtkMath.Pi() - 0.05)
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
    interactor.render_window = render_window

    # Setup a slider widget for each varying parameter.
    slider_properties = SliderProperties()

    # Setup a slider widget for each varying parameter.
    slider_properties.title_text = 'U min'
    slider_properties.range['maximum_value'] = 4.5
    slider_properties.range['minimum_value'] = -4.5
    slider_properties.range['value'] = -4.5
    slider_properties.dimensions['tube_width'] = 0.008
    slider_properties.dimensions['slider_length'] = 0.008
    slider_properties.dimensions['label_height'] = 0.02
    slider_properties.dimensions['title_height'] = 0.02
    slider_properties.position = {'point1': (0.1, 0.1), 'point2': (0.9, 0.1)}
    slider_widget_minimum_u = make_slider_widget(slider_properties, interactor)
    slider_widget_minimum_u.AddObserver(vtkCommand.InteractionEvent, SliderCallbackMinimumU(surface))

    slider_properties.title_text = 'U max'
    slider_properties.range['value'] = 4.5
    slider_properties.position = {'point1': (0.1, 0.9), 'point2': (0.9, 0.9)}
    slider_widget_maximum_u = make_slider_widget(slider_properties, interactor)
    slider_widget_maximum_u.AddObserver(vtkCommand.InteractionEvent, SliderCallbackMaximumU(surface))

    slider_properties.title_text = 'V min'
    slider_properties.range['maximum_value'] = vtkMath.Pi() - 0.05
    slider_properties.range['minimum_value'] = 0.05
    slider_properties.range['value'] = 0.05
    slider_properties.position = {'point1': (0.1, 0.1), 'point2': (0.1, 0.9)}
    slider_widget_minimum_v = make_slider_widget(slider_properties, interactor)
    slider_widget_minimum_v.AddObserver(vtkCommand.InteractionEvent, SliderCallbackMaximumU(surface))

    slider_properties.title_text = 'V max'
    slider_properties.range['value'] = vtkMath.Pi() - 0.05
    slider_properties.position = {'point1': (0.9, 0.1), 'point2': (0.9, 0.9)}
    slider_widget_maximum_v = make_slider_widget(slider_properties, interactor)
    slider_widget_maximum_v.AddObserver(vtkCommand.InteractionEvent, SliderCallbackMaximumU(surface))

    render_window.Render()
    renderer.active_camera.Azimuth(60)
    renderer.active_camera.Elevation(-60)
    renderer.active_camera.Zoom(0.9)
    renderer.ResetCameraClippingRange()

    interactor.Initialize()
    interactor.Start()


class SliderProperties:
    """
    These are default values.
    """
    dimensions = {
        'tube_width': 0.008,
        'slider_length': 0.01, 'slider_width': 0.02,
        'end_cap_length': 0.005, 'end_cap_width': 0.05,
        'title_height': 0.03, 'label_height': 0.025,
    }
    colors = {
        'title_color': 'White', 'label_color': 'White', 'slider_color': 'White',
        'selected_color': 'HotPink', 'bar_color': 'White', 'bar_ends_color': 'White',
    }
    range = {'minimum_value': 0.0, 'maximum_value': 1.0, 'value': 0.0}
    title_text = '',
    position = {'point1': (0.1, 0.1), 'point2': (0.9, 0.1)}


def make_slider_widget(slider_properties, interactor):
    """
    Make a slider widget.
    :param slider_properties: range, title name, dimensions, colors, and position.
    :param interactor: The vtkInteractor.
    :return: The slider widget.
    """
    colors = vtkNamedColors()

    slider_rep = vtkSliderRepresentation2D(minimum_value=slider_properties.range['minimum_value'],
                                           maximum_value=slider_properties.range['maximum_value'],
                                           value=slider_properties.range['value'],
                                           title_text=slider_properties.title_text,
                                           tube_width=slider_properties.dimensions['tube_width'],
                                           slider_length=slider_properties.dimensions['slider_length'],
                                           slider_width=slider_properties.dimensions['slider_width'],
                                           end_cap_length=slider_properties.dimensions['end_cap_length'],
                                           end_cap_width=slider_properties.dimensions['end_cap_width'],
                                           title_height=slider_properties.dimensions['title_height'],
                                           label_height=slider_properties.dimensions['label_height'],
                                           )

    # Set the color properties.
    slider_rep.title_property.color = colors.GetColor3d(slider_properties.colors['title_color'])
    slider_rep.label_property.color = colors.GetColor3d(slider_properties.colors['label_color'])
    slider_rep.tube_property.color = colors.GetColor3d(slider_properties.colors['bar_color'])
    slider_rep.cap_property.color = colors.GetColor3d(slider_properties.colors['bar_ends_color'])
    slider_rep.slider_property.color = colors.GetColor3d(slider_properties.colors['slider_color'])
    slider_rep.selected_property.color = colors.GetColor3d(slider_properties.colors['selected_color'])

    # Set the position.
    slider_rep.point1_coordinate.coordinate_system = Coordinate.CoordinateSystem.VTK_NORMALIZED_VIEWPORT
    slider_rep.point1_coordinate.value = slider_properties.position['point1']
    slider_rep.point2_coordinate.coordinate_system = Coordinate.CoordinateSystem.VTK_NORMALIZED_VIEWPORT
    slider_rep.point2_coordinate.value = slider_properties.position['point2']

    widget = vtkSliderWidget(representation=slider_rep, interactor=interactor, enabled=True)
    widget.SetAnimationModeToAnimate()

    return widget


# These callbacks do the actual work.
# Callbacks for the interactions
class SliderCallbackMinimumU:
    def __init__(self, kuen):
        self.kuen = kuen

    def __call__(self, caller, ev):
        sliderWidget = caller
        value = sliderWidget.representation.value
        if value > 0.99 * self.kuen.maximum_u:
            value = self.kuen.maximum_u
            sliderWidget.GetRepresentation().value = value
        self.kuen.minimum_u = value


class SliderCallbackMaximumU:
    def __init__(self, kuen):
        self.kuen = kuen

    def __call__(self, caller, ev):
        sliderWidget = caller
        value = sliderWidget.representation.value
        if value < self.kuen.minimum_u + .01:
            value = self.kuen.minimum_u
            sliderWidget.GetRepresentation().value = value
        self.kuen.maximum_u = value


class SliderCallbackMinimumV:
    def __init__(self, kuen):
        self.kuen = kuen

    def __call__(self, caller, ev):
        sliderWidget = caller
        value = sliderWidget.representation.value
        if value > 0.99 * self.kuen.maximum_v:
            value = self.kuen.maximum_v
            sliderWidget.GetRepresentation().value = value
        self.kuen.minimum_v = value


class SliderCallbackMaximumV():
    def __init__(self, kuen):
        self.kuen = kuen

    def __call__(self, caller, ev):
        slider_widget = caller
        value = slider_widget.representation.value
        if value < self.kuen.minimum_v + .01:
            value = self.kuen.minimum_v
            slider_widget.GetRepresentation().value = value
        self.kuen.maximum_v = value


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


if __name__ == '__main__':
    main()
