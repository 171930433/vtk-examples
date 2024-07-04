#!/usr/bin/env python3

"""
PineRootConnectivityA

Note: Make sure PineRootConnectivity.py is in the same directory as this program.
"""

import PineRootConnectivity


def main():
    file_name, no_connectivity = PineRootConnectivity.get_program_parameters()
    no_connectivity = True
    PineRootConnectivity.pine_root_connectivity(file_name, no_connectivity)


if __name__ == '__main__':
    main()
