### Description

Given a filename, uses the appropriate vtkPolyData reader to read any vtkPolyData file.

To use the snippet, click the *Copy to clipboard* at the upper right of the code blocks.

### Implementation

``` python

# from pathlib import Path
# 
# from vtkmodules.vtkIOGeometry import (
#     vtkBYUReader,
#     vtkOBJReader,
#     vtkSTLReader
# )
# from vtkmodules.vtkIOLegacy import vtkPolyDataReader
# from vtkmodules.vtkIOPLY import vtkPLYReader
# from vtkmodules.vtkIOXML import vtkXMLPolyDataReader

def ReadPolyData(file_name):
    valid_suffixes = ['.g', '.obj', '.stl', '.ply', '.vtk', '.vtp']
    path = Path(file_name)
    ext = None
    if path.suffix:
        ext = path.suffix.lower()
    if path.suffix not in valid_suffixes:
        print(f'No reader for this file suffix: {ext}')
        return None
    else:
        reader = None
        if ext == ".ply":
            reader = vtkPLYReader(file_name=file_name)
        elif ext == ".vtp":
            reader = vtkXMLPolyDataReader(file_name=file_name)
        elif ext == ".obj":
            reader = vtkOBJReader(file_name=file_name)
        elif ext == ".stl":
            reader = vtkSTLReader(file_name=file_name)
        elif ext == ".vtk":
            reader = vtkPolyDataReader(file_name=file_name)
        elif ext == ".g":
            reader = vtkBYUReader(file_name=file_name)

        if reader:
            reader.update()
            poly_data = reader.output
            return poly_data
        else:
            return None

```
