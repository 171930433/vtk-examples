#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingFreeType
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import (
    vtkArrowSource,
    vtkConeSource,
    vtkCubeSource,
    vtkCylinderSource,
    vtkDiskSource,
    vtkLineSource,
    vtkRegularPolygonSource,
    vtkSphereSource
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
    colors.SetColor("BkgColor", [51, 77, 102, 255])

    # Create container to hold the 3D object generators (sources)
    geometric_object_sources = list()

    # Populate the container with the various object sources to be demonstrated
    geometric_object_sources.append(vtkArrowSource())
    geometric_object_sources.append(vtkConeSource())
    geometric_object_sources.append(vtkCubeSource())
    geometric_object_sources.append(vtkCylinderSource())
    geometric_object_sources.append(vtkDiskSource())
    geometric_object_sources.append(vtkLineSource())
    geometric_object_sources.append(vtkRegularPolygonSource())
    geometric_object_sources.append(vtkSphereSource())

    # Define the size of the grid that will hold the objects.
    grid_cols = 3
    grid_rows = 3
    # Define side length (in pixels) of each renderer square.
    renderer_size = 300
    size = (renderer_size * grid_cols, renderer_size * grid_rows)
    render_window = vtkRenderWindow(size=size, window_name='GeometricObjectsDemo')

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    style = vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)

    # Create one text property for all.
    text_scale_mode = {'none': 0, 'prop': 1, 'viewport': 2}
    justification = {'left': 0, 'centered': 1, 'right': 2}
    text_property = vtkTextProperty(color=colors.GetColor3d('LightGoldenrodYellow'), bold=True, italic=True,
                                    shadow=True,
                                    font_size=16, justification=justification['left'])

    # Position text according to its length and centered in the viewport.
    name_len_min = 0
    name_len_max = 0
    for i in range(0, len(geometric_object_sources)):
        sz = len(geometric_object_sources[i].class_name)
        if i == 0:
            name_len_min = name_len_max = sz
        else:
            name_len_min = min(name_len_min, sz)
            name_len_max = max(name_len_max, sz)
    text_positions = list()
    for i in range(0, len(geometric_object_sources)):
        sz = len(geometric_object_sources[i].class_name)
        delta_sz = 0.95 * sz / name_len_max
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

    for row in range(0, grid_rows):
        for col in range(0, grid_cols):
            index = row * grid_cols + col

            # Set the renderer's viewport dimensions (xmin, ymin, xmax, ymax) within the render window.
            # Note that for the Y values, we need to subtract the row index from grid_rows
            # because the viewport Y axis points upwards, but we want to draw the grid from top to down.
            viewport = (
                float(col) / grid_cols,
                float(grid_rows - row - 1) / grid_rows,
                float(col + 1) / grid_cols,
                float(grid_rows - row) / grid_rows
            )

            # Create a renderer for this grid cell.
            renderer = vtkRenderer(background=colors.GetColor3d('BkgColor'), viewport=viewport)

            # Add the corresponding actor and label for this grid cell, if they exist.
            if index < len(geometric_object_sources):
                # Create the mappers and actors for each object.
                mappers.append(vtkPolyDataMapper())
                geometric_object_sources[index] >> mappers[index]

                actors.append(vtkActor(mapper=mappers[index]))
                actors[index].property.color = colors.GetColor3d('PeachPuff')
                # actors[index].backface_property = back_property

                renderer.AddActor(actors[index])

                # Create the text actor and representation.
                text_actors.append(
                    vtkTextActor(input=geometric_object_sources[index].class_name,
                                 text_scale_mode=text_scale_mode['none'],
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

            render_window.AddRenderer(renderer)

    render_window.Render()

    for i in range(0, len(geometric_object_sources)):
        text_widgets[i].On()

    interactor.Start()


if __name__ == '__main__':
    main()
