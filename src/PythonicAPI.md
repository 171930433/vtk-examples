# PythonicAPI Examples

These examples use the improved VTK Python interface. Some information about the improved Python interface can be found [here](../PythonicAPI/Features/)

The examples here are either newly crafted ones or upgraded existing Python examples using the improved VTK Python interface.

See [More Pythonic VTK wrapping](https://discourse.vtk.org/t/more-pythonic-vtk-wrapping/13092) for the VTK Discourse discussion and [Wrap VTK properties to pythonic properties with snake_case names](https://gitlab.kitware.com/vtk/vtk/-/merge_requests/10820) for the merge request.

## Upgrading an existing example to use the improved VTK Python interface

1. Copy the example from the **src/Python** folder into the **src/PythonicAPI** folder maintaining the same path structure. If there is a corresponding markdown file, copy it.
2. Copy the corresponding test image from **src/Testing/Baseline/Python/** into **src/Testing/Baseline/PythonicAPI/**
3. Edit **src/PythonicAPI.md**, possibly creating a table and headings to match the original example in **src/Python**.
4. Upgrade the Python example.
5. The associated markdown file (if any) may need checking to ensure any links in the document remain valid.
6. Check everything is working and do a Merge Request.

## Adding a new example

Follow the documented procedure [ForDevelopers](https://examples.vtk.org/site/Instructions/ForDevelopers/) remembering that the folder to use is **PythonicAPI**.

## VTK Classes Summary

This Python script, [SelectExamples](../Python/Utilities/SelectExamples), will let you select examples based on a VTK Class and language. It requires Python 3.7 or later. The following tables will produce similar information.

- [VTK Classes with Examples](/Coverage/PythonicAPIVTKClassesUsed.md), this table is really useful when searching for example(s) using a particular class.

- [VTK Classes with No Examples](/Coverage/PythonicAPIVTKClassesNotUsed.md), please add examples in your area of expertise!

## Hello World

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[A hello world example](/PythonicAPI/GeometricObjects/CylinderExample) | Cylinder example from the VTK Textbook and source code. A hello world example.

## Utilities

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[CheckVTKVersion](/PythonicAPI/Utilities/CheckVTKVersion) | Check the VTK version and provide alternatives for different VTK versions.

## Visualization

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[WarpCombustor](/PythonicAPI/VisualizationAlgorithms/WarpCombustor) | Carpet plots of combustor flow energy in a structured grid. Colors and plane displacement represent energy values.
