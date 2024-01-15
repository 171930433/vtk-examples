# Adding WASM preview to an example

## Configure your example if it needs to be executed with arguments

First, if it requires files, you will need to ensure those files are stored in
__REPO_NAME__/src/Testing/Data or __REPO_NAME__/src/SupplementaryData/Cxx.

If you have to add a file for your example to work you will also have to add
instructions about the file package that will need to be linked to the WASM file
by editing __REPO_NAME__/src/Admin/WASM/packaged_files.json

Then, you will need to edit __REPO_NAME__/src/Admin/WASM/ArgsNeeded.json.
Remember everything under the package name in packaged_files.json will be mapped
to "/" in the WebAssembly virtual filesystem (e.g. DicomTestImage/brain\_001.dcm
will become /DicomTestImage/brain\_001.dcm).
ArgsNeeded.json needs two variables for each example:
the args in the same order you would put them when running your example from bash
and the names of the file packages your are going to need.
Leave the list empty if there's none.

## test your example

You will need to download [VTK source code](gitlab.kitware.com/vtk/vtk).

Run the script to generate the CMakeLists and the index.html you need:

```
cd __REPO_NAME__/src/Admin
python3 ./GenerateHtmlCMake.py path/to/example path/to/vtk/source
cd path/to/example
```

Then build and run your example [as explained here](../3_BuildingWASM).
If it works well, then you are finished here. If it doesn't because of
an error in VTK pipeline, then revert the changes you made to ArgsNeeded.json
and add the example to the exclusion list. You are welcome to add an issue
to [VTK Gitlab](https://gitlab.kitware.com/vtk/vtk/-/issues) if you think it's
relevant.
