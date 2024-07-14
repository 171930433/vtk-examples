#!/usr/bin/env python3

"""
The output is:

 10 20 30
 40 50 60
 70 80 90

+-----------------+------------------+
|                 | value            |
+-----------------+------------------+
| 2               | 30               |
| 1               | 20               |
| 0               | 10               |
| 2               | 60               |
| 1               | 50               |
| 0               | 40               |
| 2               | 90               |
| 1               | 80               |
| 0               | 70               |
+-----------------+------------------+

The first column is the column index of the item in the 'value' column.
The row index is given by the number of times we've previously seen the column
index. For some reason, zeros in the matrix are not reported in the table.

For example, the first row says that the value '30' is in column 2 of the matrix
(0-based indexing). Since we have not previously seen an item in column 2, it is
in row 0 of the matrix.

The fourth row says that the value '60' is also in column 2. We infer that '60'
is row 1 of the matrix because we have already seen one item (the '30') in
column 2.

"""

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonCore import vtkDenseArray
from vtkmodules.vtkCommonDataModel import vtkArrayData
from vtkmodules.vtkInfovisCore import (
    vtkAdjacencyMatrixToEdgeTable,
    vtkArrayToTable
)


def main():
    # This is a templated class, note the use of square brackets for the template arguments.
    array = vtkDenseArray['float']()
    array.Resize(3, 3)

    counter = 1
    scale = 10
    for i in range(0, array.extents[0].GetEnd()):
        for j in range(0, array.extents[1].GetEnd()):
            array.SetValue(i, j, counter * scale)
            counter += 1

    array_data = vtkArrayData()
    array_data.AddArray(array)

    # Optional step to check what we entered.
    table = vtkArrayToTable(input_data=array_data)
    table.update()
    table.output.Dump()

    adjacency_matrix_to_edge_table = vtkAdjacencyMatrixToEdgeTable(input_data=array_data)
    adjacency_matrix_to_edge_table.update()
    adjacency_matrix_to_edge_table.output.Dump()


if __name__ == '__main__':
    main()
