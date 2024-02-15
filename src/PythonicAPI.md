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

## Tutorials

## Hello World

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[A hello world example](/PythonicAPI/GeometricObjects/CylinderExample) | Cylinder example from the VTK Textbook and source code. A hello world example.

## Simple Operations

## Input and Output

### Graph Formats

### 3D File Formats

#### Standard Formats

##### Input

###### Importers

##### Output

#### VTK Formats

##### Input

##### Output

#### Legacy VTK Formats

### Image Format

#### Input

#### Output

## Geometric Objects

### Cells

### Sources

### Non Linear

### Parametric Objects

## Implicit Functions and Iso-surfaces

## Working with 3D Data

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[ConnectivityFilter](/PythonicAPI/Filtering/ConnectivityFilter) | Color any dataset type based on connectivity.
[LineOnMesh](/PythonicAPI/DataManipulation/LineOnMesh) | Plot a spline on a terrain-like surface.
[MeshLabelImageColor](/PythonicAPI/DataManipulation/MeshLabelImageColor) | Mesh a single label from a label image. Then smooth and color the vertices according to the displacement error introduced by the smoothing.

### Data Types

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[OverlappingAMR](/PythonicAPI/CompositeData/OverlappingAMR) | Demonstrates how to create and populate  VTK's Overlapping AMR Grid type with data.

### Data Type Conversions

### Point Cloud Operations

### Working with Meshes

This section includes examples of manipulating meshes.

#### Clipping

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[SolidClip](/PythonicAPI/Meshes/SolidClip) | Create a "solid" clip. The "ghost" of the part clipped away is also shown.

### Working with Structured 3D Data

#### vtkImageData

#### vtkExplicitStructuredGrid

#### vtkStructuredGrid

#### vtkStructuredPoints

#### vtkRectilinearGrid

### Working with Unstructured 3D Data

This section includes vtkUnstructuredGrid.

#### vtkUnstructuredGrid

### Registration

### Medical

### Surface reconstruction

## Utilities

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[CheckVTKVersion](/PythonicAPI/Utilities/CheckVTKVersion) | Check the VTK version and provide alternatives for different VTK versions.

### Arrays

### Events

## Math Operations

## Graphs

### Graph Conversions

## Data Structures

### Timing Demonstrations

### KD-Tree

### Oriented Bounding Box (OBB) Tree

### Octree

### Modified BSP Tree

### HyperTreeGrid

## VTK Concepts

## Rendering

## Lighting

## Texture Mapping

## Tutorial

If you are new to VTK then these tutorials will help to get you started.

## Visualization

See [this tutorial](http://www.vtk.org/Wiki/VTK/Tutorials/3DDataTypes) for a brief explanation of the VTK terminology of mappers, actors, etc.

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[WarpCombustor](/PythonicAPI/VisualizationAlgorithms/WarpCombustor) | Carpet plots of combustor flow energy in a structured grid. Colors and plane displacement represent energy values.

## Working with vtkImageData

## Volume Rendering

## User Interaction

## Working with Images

## Image Processing

## Widgets

## Plotting

## Animation

## Annotation

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[TextOrigin](/PythonicAPI/Annotation/TextOrigin) | This example demonstrates the use of vtkVectorText and vtkFollower. vtkVectorText is used to create 3D annotation.

## InfoVis

## PyQt
