#!/usr/bin/env python

"""
converted from:
 - http://www.org/Wiki/VTK/Examples/Cxx/PolyData/ExtractSelectionCells
"""

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkIdTypeArray
from vtkmodules.vtkCommonDataModel import (
    vtkSelection,
    vtkSelectionNode,
    vtkUnstructuredGrid
)
from vtkmodules.vtkFiltersExtraction import vtkExtractSelection
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkDataSetMapper,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # colors.SetColor('leftBkg', *(0.6, 0.5, 0.4, 1.0))
    # colors.SetColor('centreBkg', *(0.3, 0.1, 0.4, 1.0))
    # colors.SetColor('rightBkg', *(0.4, 0.5, 0.6, 1.0))

    sphere_source = vtkSphereSource()
    sphere_source.update()

    ids = vtkIdTypeArray(number_of_components=1)
    # Specify that we want to extract cells 10 through 19.
    i = 10
    while i < 20:
        ids.InsertNextValue(i)
        i += 1

    selection_node = vtkSelectionNode(selection_list=ids, field_type=vtkSelectionNode.CELL,
                                      content_type=vtkSelectionNode.INDICES)

    selection = vtkSelection()
    selection.AddNode(selection_node)

    extract_selection = vtkExtractSelection()
    extract_selection.SetInputData(1, selection)
    sphere_source.output >> extract_selection

    # In selection.
    selected = vtkUnstructuredGrid()
    selected.ShallowCopy(extract_selection.update().output)

    # Get points that are NOT in the selection.
    selection_node.properties.Set(vtkSelectionNode().INVERSE(), 1)  # invert the selection.

    not_selected = vtkUnstructuredGrid()
    not_selected.ShallowCopy(extract_selection.update().output)

    print(f'There are {sphere_source.output.number_of_points}'
          f' points and {sphere_source.output.number_of_cells} input cells.')
    print(f'There are {selected.number_of_points} points and {selected.number_of_cells} cells in the selection.')
    print(f'There are {not_selected.number_of_points} points'
          f' and {not_selected.number_of_cells} cells NOT in the selection.')

    sphere_property = vtkProperty(color=colors.GetColor3d('MistyRose'))
    backfaces = vtkProperty(color=colors.GetColor3d('Gold'))

    input_mapper = vtkDataSetMapper()
    sphere_source.output >> input_mapper
    input_actor = vtkActor(mapper=input_mapper, property=sphere_property, backface_property=backfaces)

    selected_mapper = vtkDataSetMapper()
    selected >> selected_mapper
    selected_actor = vtkActor(mapper=selected_mapper, property=sphere_property, backface_property=backfaces)

    not_selected_mapper = vtkDataSetMapper()
    not_selected >> not_selected_mapper
    not_selected_actor = vtkActor(mapper=not_selected_mapper, property=sphere_property, backface_property=backfaces)

    # There will be one render window
    render_window = vtkRenderWindow(size=(900, 300), window_name='ExtractSelectionCells')

    # And one interactor
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window

    # Define viewport ranges.
    # (xmin, ymin, xmax, ymax)
    left_viewport = (0.0, 0.0, 0.33, 1.0)
    center_viewport = (0.33, 0.0, 0.66, 1.0)
    right_viewport = (0.66, 0.0, 1.0, 1.0)

    # Create a camera for all renderers
    camera = vtkCamera()

    # Setup the renderers.
    left_renderer = vtkRenderer(background=colors.GetColor3d('BurlyWood'),
                                viewport=left_viewport, active_camera=camera)
    render_window.AddRenderer(left_renderer)

    center_renderer = vtkRenderer(background=colors.GetColor3d('orchid_dark'),
                                  viewport=center_viewport, active_camera=camera)
    render_window.AddRenderer(center_renderer)

    right_renderer = vtkRenderer(background=colors.GetColor3d('CornflowerBlue'),
                                 viewport=right_viewport, active_camera=camera)
    render_window.AddRenderer(right_renderer)

    left_renderer.AddActor(input_actor)
    center_renderer.AddActor(selected_actor)
    right_renderer.AddActor(not_selected_actor)

    left_renderer.ResetCamera()

    render_window.Render()
    interactor.Start()


if __name__ == '__main__':
    main()
