#!/usr/bin/env python3

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


def main():
    print('VTK Version:', vtkVersion.GetVTKVersion())
    if not vtk_version_ok(9, 0, 0):
        print('You need VTK version 9.0.0 or greater to run this program.')
        return

    test_versions = ((9, 2, 20220831), (9, 19, 0))
    for ver in test_versions:
        if vtk_version_ok(*ver):
            print(f'This code works for VTK Versions >= {".".join(map(str, ver))}')
        else:
            print(f'You need VTK Version {".".join(map(str, ver))} or greater.')

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


if __name__ == '__main__':
    main()
