### Description

This script allows you to select examples whose classes are in `language 1` but not in `language 2`.

Useful for ensuring that examples for missing classes will be added to `language 2`.

In order to do this, a JSON file listing the vtk examples by VTK class is obtained from the gh-pages branch of the vtk-examples GitHub site. When this script runs, it checks for the existence of this JSON file in your temporary folder, downloading it, if it doesn't exist. If it already exists, then it is updated if the file is more than ten minutes old.

When you run this script by specifying the Language (one of: `CSharp`, `Cxx`, `Java`, `Python`, `PythonicAPI`) for `language 1` and `language 2`, a markdown file is created with the missing class in `language 2` and a link to the relevant example(s) in `language 1`.

!!! note
    Options are also provided to force an overwrite of the downloaded the JSON file (`-o`) or to change the URL to the JSON file (`-j`)
