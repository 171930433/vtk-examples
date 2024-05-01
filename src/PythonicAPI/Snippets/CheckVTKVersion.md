### Description

This enables us to check the VTK version and provide alternatives for different VTK versions.

`True` is returned if the requested VTK version is >= the current version.

To use the snippet, click the *Copy to clipboard* at the upper right of the code blocks.

### Implementation

``` Python

from vtkmodules.vtkCommonCore import (
    VTK_VERSION_NUMBER,
    vtkVersion
)

def vtk_version_ok(major: int, minor: int, build: int):
    """
    Check the VTK version.

    :param major: Major version.
    :param minor: Minor version.
    :param build: Build version.
    :return: True if the requested VTK version is greater or equal to the actual VTK version.
    """
    needed_version = 10000000000 * int(major) + 100000000 * int(minor) + int(build)
    vtk_version_number = VTK_VERSION_NUMBER
    if vtk_version_number >= needed_version:
        return True
    else:
        return False

```

### Typical usage

``` Python

    current_version = tuple(map(int, vtkVersion.GetVTKVersion().split('.')))
    if vtk_version_ok(*current_version):
        try:
            print(f'This code works for VTK Version {vtkVersion.GetVTKVersion()}.')
            # ...
        except AttributeError:
            pass
    else:
        print(f'This is code for older versions of VTK <= {vtkVersion.GetVTKVersion()}.')
        # ...
    print('Rest of the code.')
    # ...

```

See:

- [CheckVTKVersion](../../Utilities/CheckVTKVersion) for a test/example.
