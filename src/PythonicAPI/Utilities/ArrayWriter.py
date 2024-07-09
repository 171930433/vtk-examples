#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonCore import vtkDenseArray
from vtkmodules.vtkCommonDataModel import vtkArrayData
from vtkmodules.vtkIOCore import vtkArrayWriter


def main():
    # This is a templated class, note the use of square brackets for the template arguments.
    array = vtkDenseArray['float']()
    array.Resize(1, 3)
    array.SetValue(0, 0, 1.0)
    array.SetValue(0, 1, 2.0)
    array.SetValue(0, 2, 3.0)

    print(f'The extents are are: ({array.extents[0].GetEnd()}, {array.extents[1].GetEnd()})')
    #     Set the values.
    for i in range(0, array.extents[0].GetEnd()):
        for j in range(0, array.extents[1].GetEnd()):
            array.SetValue(i, j, i + j)

    # Method 1
    array_data = vtkArrayData()
    array_data.AddArray(array)

    writer1 = vtkArrayWriter(file_name='Test1.txt', input_data=array_data)
    writer1.Write()

    # Method 2
    file_name = 'Test2.txt'
    writer2 = vtkArrayWriter()
    writer2.Write(array, file_name)


if __name__ == '__main__':
    main()
