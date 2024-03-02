#!/usr/bin/env python3

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
    text_scale_mode = {'none': 0, 'prop': 1, 'viewport': 2}
    justification = {'left': 0, 'centered': 1, 'right': 2}
    text_property = vtkTextProperty(color=colors.GetColor3d('LightGoldenrodYellow'), bold=True, italic=True,
                                    shadow=True,
                                    font_size=16, justification=justification['centered'])

    # Position text according to its length and centered in the viewport.
    name_len_min = 0
    name_len_max = 0
    for i in range(0, len(source_objects)):
        sz = len(source_objects[i].class_name)
        if i == 0:
            name_len_min = name_len_max = sz
        else:
            name_len_min = min(name_len_min, sz)
            name_len_max = max(name_len_max, sz)
    text_positions = list()
    for i in range(0, len(source_objects)):
        sz = len(source_objects[i].class_name)
        delta_sz = 0.7 * sz / name_len_max
        x0 = 0.5 - delta_sz / 2.0
        x1 = delta_sz
        # print(f'{i}: {x0:3.2f}, {x1:3.2f} len: {x0 + x1:3.2f}')
        text_positions.append(
            {'p': [x0, 0.01, 0], 'p2': [x1, 0.2, 0]})
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
                # Create the mappers and actors for each object.
                mappers.append(vtkPolyDataMapper())
                source_objects[index] >> mappers[index]

                actors.append(vtkActor(mapper=mappers[index]))
                actors[index].property.color = colors.GetColor3d('PeachPuff')
                actors[index].backface_property = back_property

                renderer.AddActor(actors[index])

                # Create the text actor and representation.
                text_actors.append(
                    vtkTextActor(input=source_objects[index].class_name, text_scale_mode=text_scale_mode['none'],
                                 text_property=text_property))

                # Create the text representation. Used for positioning the text actor.
                text_representations.append(vtkTextRepresentation(enforce_normalized_viewport_bounds=True))
                text_representations[index].GetPositionCoordinate().value = text_positions[index]['p']
                text_representations[index].GetPosition2Coordinate().value = text_positions[index]['p2']

                # Create the text widget, setting the default renderer and interactor.
                text_widgets.append(
                    vtkTextWidget(representation=text_representations[index], text_actor=text_actors[index]))
                text_widgets[index].SetDefaultRenderer(renderer)
                text_widgets[index].SetInteractor(interactor)
                text_widgets[index].SelectableOff()

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


if __name__ == '__main__':
    main()
