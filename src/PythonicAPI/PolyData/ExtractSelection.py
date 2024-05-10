#!/usr/bin/env python3

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
from vtkmodules.vtkFiltersSources import vtkPointSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkDataSetMapper,
    vtkProperty,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main(argv):
    colors = vtkNamedColors()

    point_source = vtkPointSource(number_of_points=50)
    point_source.update()

    ids = vtkIdTypeArray(number_of_components=1)
    # Set values.
    for i in range(10, 20):
        ids.InsertNextValue(i)

    selection_node = vtkSelectionNode(selection_list=ids, field_type=vtkSelectionNode.POINT,
                                      content_type=vtkSelectionNode.INDICES)

    selection = vtkSelection()
    selection.AddNode(selection_node)

    extract_selection = vtkExtractSelection()
    extract_selection.SetInputData(1, selection)
    point_source.output >> extract_selection

    # In selection.
    selected = vtkUnstructuredGrid()
    selected.ShallowCopy(extract_selection.update().output)

    # Get points that are NOT in the selection.
    selection_node.properties.Set(vtkSelectionNode().INVERSE(), 1)  # invert the selection.

    not_selected = vtkUnstructuredGrid()
    not_selected.ShallowCopy(extract_selection.update().output)

    print(f'There are {point_source.output.number_of_points} input points.')
    print(f'There are {selected.number_of_points} points and {selected.number_of_cells} cells in the selection.')
    print(f'There are {not_selected.number_of_points} points'
          f' and {not_selected.number_of_cells} cells NOT in the selection.')

    point_property = vtkProperty(color=colors.GetColor3d('MidnightBlue'), point_size=5)

    input_mapper = vtkDataSetMapper()
    point_source.output >> input_mapper
    input_actor = vtkActor(mapper=input_mapper, property=point_property)

    selected_mapper = vtkDataSetMapper()
    selected >> selected_mapper
    selected_actor = vtkActor(mapper=selected_mapper, property=point_property)

    not_selected_mapper = vtkDataSetMapper()
    not_selected >> not_selected_mapper
    not_selected_actor = vtkActor(mapper=not_selected_mapper, property=point_property)

    # There will be one render window.
    render_window = vtkRenderWindow()
    render_window.SetSize(900, 300)
    render_window.SetWindowName('ExtractSelectedIds')

    # And one interactor.
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window

    # Define viewport ranges.
    # (xmin, ymin, xmax, ymax)
    left_viewport = (0.0, 0.0, 0.33, 1.0)
    center_viewport = (0.33, 0.0, 0.66, 1.0)
    right_viewport = (0.66, 0.0, 1.0, 1.0)

    # Create a camera for all renderers.
    camera = vtkCamera()

    # Setup the renderers
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
    import sys

    main(sys.argv)
