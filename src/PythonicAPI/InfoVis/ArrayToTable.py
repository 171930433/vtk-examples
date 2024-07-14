#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonCore import vtkDenseArray
from vtkmodules.vtkCommonDataModel import vtkArrayData
from vtkmodules.vtkInfovisCore import (
    vtkArrayToTable
)


def main():
    # This is a templated class, note the use of square brackets for the template arguments.
    array = vtkDenseArray['int']()
    array.Resize(2, 4)

    print(f'The extents are are: ({array.extents[0].GetEnd()}, {array.extents[1].GetEnd()})')
    #     Set the values.
    for i in range(0, array.extents[0].GetEnd()):
        for j in range(0, array.extents[1].GetEnd()):
            array.SetValue(i, j, i + j)

    array_data = vtkArrayData()
    array_data.AddArray(array)

    table = vtkArrayToTable(input_data=array_data)
    table.update()
    table.output.Dump()


if __name__ == '__main__':
    main()
