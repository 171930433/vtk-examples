#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkInfovisCore import vtkRandomGraphSource
from vtkmodules.vtkViewsInfovis import vtkGraphLayoutView


def selection_callback(caller, event):
    # Use the shift key to select both nodes and edges.
    # The nodes can either vertices or edges.
    sel = caller.current_selection
    node0 = sel.GetNode(0)
    node0_field_type = node0.field_type
    sel_list0 = caller.current_selection.GetNode(0).selection_list
    node1 = sel.GetNode(1)
    node1_field_type = node1.field_type
    sel_list1 = caller.current_selection.GetNode(1).selection_list

    if sel_list0.number_of_tuples > 0:
        # print('node0:')
        print_field_type(node0_field_type)
        for ii in range(sel_list0.number_of_tuples):
            print(' ', sel_list0.GetValue(ii))

    if sel_list1.number_of_tuples > 0:
        # print('node1:')
        print_field_type(node1_field_type)
        for ii in range(sel_list1.number_of_tuples):
            print(' ', sel_list1.GetValue(ii))

        print('- - -')


def print_field_type(field_type):
    if field_type == 3:
        print('Vertex Id(s) Selected:')
    elif field_type == 4:
        print('Edge Id(s) Selected:')
    else:
        print('Unknown type:')


def main():
    source = vtkRandomGraphSource()
    source.Update()

    view = vtkGraphLayoutView()
    view.AddRepresentationFromInputConnection(source.GetOutputPort())

    rep = view.GetRepresentation(0)

    # The vtkRenderedGraphRepresentation should already have a vtkAnnotationLink,
    # so we just want to grab it and add an observer with our callback function
    # attached
    link = rep.GetAnnotationLink()
    link.AddObserver('AnnotationChangedEvent', selection_callback)

    view.GetRenderWindow().SetSize(600, 600)
    view.ResetCamera()
    view.Render()
    view.GetInteractor().Start()


if __name__ == '__main__':
    main()
