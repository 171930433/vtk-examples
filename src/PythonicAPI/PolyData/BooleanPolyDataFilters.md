### Description

This example uses either the vtkBooleanOperationPolyDataFilter or vtkLoopBooleanPolyDataFilter.
These filters work best with "clean" data, so this example first runs vtkTriangleFilter and then vtkCleanPolyData.

The LoopBooleanPolyDataFilter uses an alternative algorithm to do the boolean operations.

This example can be run in three ways:

1.  *BooleanOperationPolyDataFilter* :- Computes the intersection of two spheres
2.  *BooleanOperationPolyDataFilter* **-o intersection|difference|union** :- Computes the intersection(difference or union) of two spheres
3.  *BooleanOperationPolyDataFilter*  **input1.vtk input2.vtk **-o intersection|difference|union** :- Computes the intersection(difference or union) of two vtkPolyData's

!!! note
    If **-l** is specified, the LoopBooleanPolyDataFilter is used instead of the BooleanOperationPolyDataFilter.

!!! cite
    See [Boolean Operations on Surfaces in VTK Without External Libraries](http://www.vtkjournal.org/browse/publication/797) for details on the algorithm.
