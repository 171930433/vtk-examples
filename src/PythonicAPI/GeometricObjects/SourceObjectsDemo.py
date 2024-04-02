#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingFreeType
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import (
    vtkConeSource,
    vtkCubeSource,
    vtkCylinderSource,
    vtkDiskSource,
    vtkLineSource,
    vtkPlaneSource,
    vtkPointSource,
    vtkSphereSource,
    vtkTextSource
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkInteractionWidgets import (
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty
)


def main():
    colors = vtkNamedColors()

    # Set the background color.
    colors.SetColor('BkgColor', [51, 77, 102, 255])

    source_objects = list()
    source_objects.append(vtkSphereSource(phi_resolution=21, theta_resolution=21))
    source_objects.append(vtkConeSource(resolution=51))
    source_objects.append(vtkCylinderSource(resolution=51))
    source_objects.append(vtkCubeSource())
    source_objects.append(vtkPlaneSource())
    source_objects.append(vtkTextSource(text='Hello'))
    source_objects[-1].BackingOff()
    source_objects.append(vtkPointSource(number_of_points=500))
    source_objects.append(vtkDiskSource(circumferential_resolution=51))
    source_objects.append(vtkLineSource())

    grid_dimensions = 3
    renderer_size = 300
    size = (renderer_size * grid_dimensions, renderer_size * grid_dimensions)
    render_window = vtkRenderWindow(size=size, window_name='SourceObjectsDemo')

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    style = vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)

    # Create one text property for all.
    text_property = vtkTextProperty(color=colors.GetColor3d('LightGoldenrodYellow'), bold=True, italic=True,
                                    shadow=True,
                                    font_size=12, justification=TextPropertyJustification.VTK_TEXT_CENTERED)

    # Position text according to its length and centered in the viewport.
    surface_names = list()
    for i in range(0, len(source_objects)):
        surface_names.append(source_objects[i].class_name)
    text_positions = get_text_positions(surface_names, justification='center')

    back_property = vtkProperty(color=colors.GetColor3d('Tomato'))

    mappers = list()
    actors = list()
    text_representations = list()
    text_actors = list()
    text_widgets = list()

    for row in range(0, grid_dimensions):
        for col in range(0, grid_dimensions):
            index = row * grid_dimensions + col
            x0 = float(col) / grid_dimensions
            y0 = float(grid_dimensions - row - 1) / grid_dimensions
            x1 = float(col + 1) / grid_dimensions
            y1 = float(grid_dimensions - row) / grid_dimensions

            renderer = vtkRenderer(background=colors.GetColor3d('BkgColor'), viewport=(x0, y0, x1, y1))

            # Add the corresponding actor and label for this grid cell, if they exist.
            if index < len(source_objects):
                name = source_objects[index].class_name
                # Create the mappers and actors for each object.
                mappers.append(vtkPolyDataMapper())
                source_objects[index] >> mappers[index]

                actors.append(vtkActor(mapper=mappers[index]))
                actors[index].property.color = colors.GetColor3d('PeachPuff')
                actors[index].backface_property = back_property

                renderer.AddActor(actors[index])

                # Create the text actor and representation.
                text_actors.append(
                    vtkTextActor(input=source_objects[index].class_name,
                                 text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_NONE,
                                 text_property=text_property))

                # Create the text representation. Used for positioning the text actor.
                text_representations.append(vtkTextRepresentation(enforce_normalized_viewport_bounds=True))
                text_representations[index].GetPositionCoordinate().value = text_positions[name]['p']
                text_representations[index].GetPosition2Coordinate().value = text_positions[name]['p2']

                # Create the text widget, setting the default renderer and interactor.
                text_widgets.append(
                    vtkTextWidget(representation=text_representations[index], text_actor=text_actors[index],
                                  default_renderer=renderer, interactor=interactor, selectable=False))

                renderer.ResetCamera()
                renderer.active_camera.Azimuth(30)
                renderer.active_camera.Elevation(30)
                renderer.GetActiveCamera().Zoom(0.8)
                renderer.ResetCameraClippingRange()

            render_window.AddRenderer(renderer)

    render_window.Render()

    for i in range(0, len(source_objects)):
        text_widgets[i].On()

    interactor.Start()


def get_text_positions(available_surfaces, justification='center'):
    """
    Get positioning information for the names of the surfaces.

    :param available_surfaces: The surfaces
    :param justification: left, center or right
    :return: A list of positioning information.
    """
    # Position the source name according to its length and justification in the viewport.
    # Top
    # y0 = 0.79
    # Bottom
    y0 = 0.01
    dy = 0.2
    # The gap between the left or right edge of the screen and the text.
    dx = 0.01
    # The size of the maximum length of the text in screen units.
    x_scale = 0.7

    name_len_min = 0
    name_len_max = 0
    first = True
    for k in available_surfaces:
        sz = len(k)
        if first:
            name_len_min = name_len_max = sz
            first = False
        else:
            name_len_min = min(name_len_min, sz)
            name_len_max = max(name_len_max, sz)
    text_positions = dict()
    for k in available_surfaces:
        sz = len(k)
        delta_sz = x_scale * sz / name_len_max
        if delta_sz <= 2.0 * dx:
            dx = 0.01
            delta_sz -= 0.02
        else:
            delta_sz -= 2.0 * dx

        if justification.lower() in ['center', 'centre']:
            x0 = 0.5 - delta_sz / 2.0
        elif justification.lower() == 'right':
            x0 = 1.0 - delta_sz
            if dx < x0:
                x0 -= dx
            else:
                x0 = dx
            if x0 + delta_sz >= 1:
                delta_sz -= dx
                x0 -= dx
        else:
            # Default is left justification.
            x0 = dx
            if x0 + dx >= 1.0:
                x0 = dx - x0
            if x0 + delta_sz >= 1:
                delta_sz -= dx
                x0 = dx

        # For debugging!
        # print(
        #     f'{k:16s}: (x0, y0) = ({x0:3.2f}, {y0:3.2f}), (x1, y1) = ({x0 + delta_sz:3.2f}, {y0 + dy:3.2f})'
        #     f', width={delta_sz:3.2f}')
        text_positions[k] = {'p': [x0, y0, 0], 'p2': [delta_sz, dy, 0]}

    return text_positions


# -----------------------------------------------------------------------------
# These handle the "#define VTK_SOME_CONSTANT x" in the VTK C++ code.
# The class name consists of the VTK class name (without the leading vtk)
# appended to the relevant Set/Get Macro name.
# Note: To find these constants, use the link to the header in the
#       documentation for the class.
# ------------------------------------------------------------------------------
@dataclass(frozen=True)
class TextPropertyJustification:
    VTK_TEXT_LEFT: int = 0
    VTK_TEXT_CENTERED: int = 1
    VTK_TEXT_RIGHT: int = 2


@dataclass(frozen=True)
class TextPropertyVerticalJustification:
    VTK_TEXT_BOTTOM: int = 0
    VTK_TEXT_CENTERED: int = 1
    VTK_TEXT_TOP: int = 2


if __name__ == '__main__':
    main()
