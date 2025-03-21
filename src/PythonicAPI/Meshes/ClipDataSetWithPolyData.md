### Description

The example that shows how to use the vtkClipDataSet to clip a
vtkRectilinearGrid with an arbitrary
polydata. vtkImplicitPolyDataDistance is used to turn the polydata
into an implicit function. Every point of the grid is evaluated before
sending to vtkClipDataSet. This example uses a vtkConeSource to
generate polydata to use, however any polydata could be used,
including stl files.

The left part of the image shows the inside clip and the distance
field on a center slice. The right side shows the outside clip. When
the program exits using the "e" key, the example will report the cell
type for both the inside and outside clips.

!!! note
    vtkClipDataSet tetrahedralizes the volume before clipping. Contrast this with the vtkTableBasedClipDataSet example: [TableBasedClipDataSetWithPolyData](../../../Cxx/Meshes/TableBasedClipDataSetWithPolyData).

Here is the summary reported when the example exits:
<samp>
------------------------
The clipped dataset(inside) contains a  vtkUnstructuredGrid that has 49200 cells
 Cell type  vtkTetra occurs 40736 times.
 Cell type  vtkWedge occurs 8464 times.
------------------------
The clipped dataset(outside) contains a  vtkUnstructuredGrid that has 714202 cells
 Cell type  vtkTetra occurs 704858 times.
 Cell type  vtkWedge occurs 9344 times.
</samp>
