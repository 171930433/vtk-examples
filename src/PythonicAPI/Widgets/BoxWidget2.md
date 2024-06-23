### Description

This example uses a vtkBoxWidget2 to manipulate an actor. The widget only contains the interaction logic; the actual box is drawn by the accompanying vtkBoxRepresentation.
Contrary to the older vtkBoxWidget, this widget doesn't provide functionality to assign it to one or more actors, so that has to be implemented manually.
The box is dimensioned and positioned by passing a bounding box to the `PlaceWidget` method, with the `SetPlaceFactor` method providing a scaling factor in relation to that bounding box. These methods are found in vtkBoxRepresentation.
The transformations applied to the box can be used to manipulate any number of object(s), via a custom callback class or function, which is passed to the box widget through the `AddObserver` method.

The older implementation vtkBoxWidget provides functionality to receive a vtkProp3D for the initial positioning and sizing, but the transformation synchronization still needs to be done manually. See [BoxWidget](../BoxWidget) for a simple example of how to use it.
