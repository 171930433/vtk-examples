# PythonicAPI Examples

!!! Warning
    These examples only work with VTK Version: 9.3.20240428 or greater.

These examples:

- Use the improved VTK Python interface. Some information about the improved Python interface can be found [here](../PythonicAPIComments/)
- Are either newly crafted examples or upgrades of existing Python examples

See:

- [More Pythonic VTK wrapping](https://discourse.vtk.org/t/more-pythonic-vtk-wrapping/13092) for the VTK Discourse discussion
- [Wrap VTK properties to pythonic properties with snake_case names](https://gitlab.kitware.com/vtk/vtk/-/merge_requests/10820) for the merge request

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

This Python script, [SelectExamples](../PythonicAPI/Utilities/SelectExamples), will let you select examples based on a VTK Class and language. It requires Python 3.7 or later. The following tables will produce similar information.

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

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[ReadAllPolyDataTypesDemo](/PythonicAPI/IO/ReadAllPolyDataTypesDemo) | Read all VTK polydata file types.
[ReadExodusData](/PythonicAPI/IO/ReadExodusData) | A simple script for reading and viewing ExodusII data interactively.
[TransientHDFReader](/PythonicAPI/IO/TransientHDFReader) | Read transient data written inside a vtkhdf file.

###### Importers

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[3DSImporter](/PythonicAPI/IO/3DSImporter) | Import a 3D Studio scene that includes multiple actors.

##### Output

#### VTK Formats

##### Input

##### Output

#### Legacy VTK Formats

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[ReadLegacyUnstructuredGrid](/PythonicAPI/IO/ReadLegacyUnstructuredGrid) | Read an unstructured grid that contains 11 linear cells.

### Image Format

#### Input

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[HDRReader](/PythonicAPI/IO/HDRReader) | Read a high-dynamic-range imaging file.

#### Output

## Geometric Objects

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[GeometricObjectsDemo](/PythonicAPI/GeometricObjects/GeometricObjectsDemo) |
[PipelineReuse](/PythonicAPI/GeometricObjects/PipelineReuse) | How to reuse a pipeline.
[Planes](/PythonicAPI/GeometricObjects/Planes) | We create a convex hull of the planes for display purposes.
[SourceObjectsDemo](/PythonicAPI/GeometricObjects/SourceObjectsDemo) | Examples of source objects that procedurally generate polygonal models.  These nine images represent just some of the capability of VTK. From upper left in reading order: sphere, cone, cylinder, cube, plane, text, random point cloud, disk (with or without hole), and line source. Other polygonal source objects are available; check subclasses of vtkPolyDataAlgorithm.

### Cells

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[CellTypeSource](/PythonicAPI/GeometricObjects/CellTypeSource) | Generate tessellated cells.
[ConvexPointSet](/PythonicAPI/GeometricObjects/ConvexPointSet) | Generate a ConvexPointSet cell.

### Sources

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[EarthSource](/PythonicAPI/GeometricObjects/EarthSource) | Create the Earth.
[Frustum](/PythonicAPI/GeometricObjects/Frustum) |
[TessellatedBoxSource](/PythonicAPI/GeometricObjects/TessellatedBoxSource) | Generate a box with tessellated sides.

### Non Linear

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[IsoparametricCellsDemo](/PythonicAPI/GeometricObjects/IsoparametricCellsDemo) | Nonlinear isoparametric cell types in VTK.

### Parametric Objects

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[ParametricObjectsDemo](/PythonicAPI/GeometricObjects/ParametricObjectsDemo) | Demonstrates the Parametric classes added by Andrew Maclean and additional classes added by Tim Meehan. The parametric spline is also included. Options are provided to display single objects, add backface, add normals and print out an image.
[ParametricKuenDemo](/PythonicAPI/GeometricObjects/ParametricKuenDemo) | Interactively change the parameters for a Kuen Surface.

## Implicit Functions and Iso-surfaces

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[BooleanOperationImplicitFunctions](/PythonicAPI/ImplicitFunctions/BooleanOperationImplicitFunctions) | Demonstrate booleans of two different implicit functions
[ContourTriangulator](/PythonicAPI/Modelling/ContourTriangulator) | Create a contour from a structured point set (image) and triangulate it.
[DiscreteFlyingEdges3D](/PythonicAPI/Modelling/DiscreteFlyingEdges3D) | Generate surfaces from labeled data.
[ExtractData](/PythonicAPI/VisualizationAlgorithms/ExtractData) | Implicit functions used to select data: Two ellipsoids are combined using the union operation used to select voxels from a volume. Voxels are shrunk 50 percent.
[IceCream](/PythonicAPI/VisualizationAlgorithms/IceCream) | How to use boolean combinations of implicit functions to create a model of an ice cream cone.
[ImplicitQuadric](/PythonicAPI/ImplicitFunctions/ImplicitQuadric) | Create an ellipsoid using an implicit quadric
[ImplicitSphere](/PythonicAPI/ImplicitFunctions/ImplicitSphere) | Demonstrate sampling of a sphere implicit function
[ImplicitSphere1](/PythonicAPI/ImplicitFunctions/ImplicitSphere1) | Demonstrate sampling of a sphere implicit function
[SampleFunction](/PythonicAPI/ImplicitFunctions/SampleFunction) | Sample and visualize an implicit function.
[SmoothDiscreteFlyingEdges3D](/PythonicAPI/Modelling/SmoothDiscreteFlyingEdges3D) | Generate smooth surfaces from labeled data.

## Working with 3D Data

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[AlignTwoPolyDatas](/PythonicAPI/PolyData/AlignTwoPolyDatas) | Align two vtkPolyData's.
[BooleanPolyDataFilters](/PythonicAPI/PolyData/BooleanPolyDataFilters) | This example performs a boolean operation (intersection, union or difference) of two PolyData using either a vtkBooleanOperationPolyDataFilter or a vtkLoopBooleanPolyDataFilter
[ConnectivityFilter](/PythonicAPI/Filtering/ConnectivityFilter) | Color any dataset type based on connectivity.
[Curvatures](/PythonicAPI/PolyData/Curvatures) | Compute Gaussian, and Mean Curvatures.
[CurvaturesAdjustEdges](/PythonicAPI/PolyData/CurvaturesAdjustEdges) | Get the Gaussian and Mean curvatures of a surface with adjustments for edge effects.
[ExtractPolyLinesFromPolyData](/PythonicAPI/PolyData/ExtractPolyLinesFromPolyData) | Extract polylines from polydata.
[ExtractSelection](/PythonicAPI/PolyData/ExtractSelection) |Extract selected points.
[ExtractSelectionCells](/PythonicAPI/PolyData/ExtractSelectionCells) | Extract cell, select cell.
[Finance](/PythonicAPI/Modelling/Finance) | Visualization of multidimensional financial data. The gray/wireframe surface represents the total data population. The red surface represents data points delinquent on loan payment.
[FinanceFieldData](/PythonicAPI/Modelling/FinanceFieldData) | Visualization of multidimensional financial data. The yellow surface represents the total data population. The red surface represents data points delinquent on loan payment.
[Glyph2D](/PythonicAPI/Filtering/Glyph2D) |
[LineOnMesh](/PythonicAPI/DataManipulation/LineOnMesh) | Plot a spline on a terrain-like surface.
[MeshLabelImageColor](/PythonicAPI/DataManipulation/MeshLabelImageColor) | Mesh a single label from a label image. Then smooth and color the vertices according to the displacement error introduced by the smoothing.
[SmoothMeshGrid](/PythonicAPI/PolyData/SmoothMeshGrid) | Create a terrain with regularly spaced points and smooth it with ?vtkLoopSubdivisionFilter? and ?vtkButterflySubdivisionFilter?.

### Data Types

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[CompositePolyDataMapper](/PythonicAPI/CompositeData/CompositePolyDataMapper) |
[OverlappingAMR](/PythonicAPI/CompositeData/OverlappingAMR) | Demonstrates how to create and populate  VTK's Overlapping AMR Grid type with data.

### Data Type Conversions

### Point Cloud Operations

### Working with Meshes

This section includes examples of manipulating meshes.

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[DeformPointSet](/PythonicAPI/Meshes/DeformPointSet) | Use the vtkDeformPointSet filter to deform a vtkSphereSource with arbitrary polydata.
[DelaunayMesh](/PythonicAPI/Modelling/DelaunayMesh) | Two-dimensional Delaunay triangulation of a random set of points. Points and edges are shown highlighted with sphere glyphs and tubes.
[PointInterpolator](/PythonicAPI/Meshes/PointInterpolator) | Plot a scalar field of points onto a PolyData surface.

#### Clipping

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[SolidClip](/PythonicAPI/Meshes/SolidClip) | Create a "solid" clip. The "ghost" of the part clipped away is also shown.

### Working with Structured 3D Data

#### ?vtkImageData?

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[ImageWeightedSum](/PythonicAPI/ImageData/ImageWeightedSum) | Add two or more images.

#### ?vtkExplicitStructuredGrid?

| Example Name | Description | Image |
| ------------ | ----------- | ----- |
[CreateESGrid](/PythonicAPI/ExplicitStructuredGrid/CreateESGrid) | Create an explicit structured grid and convert this to an unstructured grid or vice versa.
[LoadESGrid](/PythonicAPI/ExplicitStructuredGrid/LoadESGrid) | Load a VTU file and convert the dataset to an explicit structured grid.

#### ?vtkStructuredGrid?

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[BlankPoint](/PythonicAPI/StructuredGrid/BlankPoint) | Blank a point of a vtkStructuredGrid.
[SGrid](/PythonicAPI/StructuredGrid/SGrid) | Creating a structured grid dataset of a semi-cylinder. Vectors are created whose magnitude is proportional to radius and oriented in tangential direction.

#### ?vtkStructuredPoints?

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[Vol](/PythonicAPI/StructuredPoints/Vol) | Creating a image data dataset. Scalar data is generated from the equation for a sphere. Volume dimensions are 26 x 26 x 26.

#### ?vtkRectilinearGrid?

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[RGrid](/PythonicAPI/RectilinearGrid/RGrid) | Creating a rectilinear grid dataset. The coordinates along each axis are defined using an instance of vtkDataArray.
[VisualizeRectilinearGrid](/PythonicAPI/RectilinearGrid/VisualizeRectilinearGrid) | Visualize the cells of a rectilinear grid.

### Working with Unstructured 3D Data

This section includes ?vtkUnstructuredGrid?.

#### ?vtkUnstructuredGrid?

### Registration

### Medical

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[GenerateModelsFromLabels](/PythonicAPI/Medical/GenerateModelsFromLabels) | Create models from labeled volume data.
[MedicalDemo1](/PythonicAPI/Medical/MedicalDemo1) | Create a skin surface from volume data.

### Surface reconstruction

## Utilities

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[CheckVTKVersion](/PythonicAPI/Utilities/CheckVTKVersion) | Check the VTK version and provide alternatives for different VTK versions.
[ClassesInLang1NotInLang2](/PythonicAPI/Utilities/ClassesInLang1NotInLang2) | Select VTK classes with corresponding examples in one language but not in another.
[JSONColorMapToLUT](/PythonicAPI/Utilities/JSONColorMapToLUT) | Take a JSON description of a colormap and convert it to a VTK colormap.
[ColorMapToLUT](/PythonicAPI/Utilities/ColorMapToLUT) | Use vtkDiscretizableColorTransferFunction to generate a VTK colormap.
[RescaleReverseLUT](/PythonicAPI/Utilities/RescaleReverseLUT) | Demonstrate how to adjust a colormap so that the colormap scalar range matches the scalar range on the object. You can optionally reverse the colors.
[ResetCameraOrientation](/PythonicAPI/Utilities/ResetCameraOrientation) | Reset camera orientation to a previously saved orientation.
[SaveSceneToFieldData](/PythonicAPI/Utilities/SaveSceneToFieldData) | Save a vtkCamera's state in a vtkDataSet's vtkFieldData and restore it.
[SaveSceneToFile](/PythonicAPI/Utilities/SaveSceneToFile) | Save a vtkCamera's state in a file and restore it.
[Screenshot](/PythonicAPI/Utilities/Screenshot) |
[SelectExamples](/PythonicAPI/Utilities/SelectExamples) | Given a VTK Class and a language, select the matching examples.
[ShareCamera](/PythonicAPI/Utilities/ShareCamera) | Share a camera between multiple renderers.
[VTKWithNumpy](/PythonicAPI/Utilities/VTKWithNumpy) |
[XMLColorMapToLUT](/PythonicAPI/Utilities/XMLColorMapToLUT) | Take an XML description of a colormap and convert it to a VTK colormap.

### Arrays

### Events

## Math Operations

## Graphs

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[GraphToPolyData](/PythonicAPI/Graphs/GraphToPolyData) | Convert a graph to a PolyData.
[LabelVerticesAndEdges](/PythonicAPI/Graphs/LabelVerticesAndEdges) | Label vertices and edges.
[SideBySideGraphs](/PythonicAPI/Graphs/SideBySideGraphs) | Display two graphs side by side.
[ScaleVertices](/PythonicAPI/Graphs/ScaleVertices) | Size/scale vertices based on a data array.
[VisualizeDirectedGraph](/PythonicAPI/Graphs/VisualizeDirectedGraph) | Visualize a directed graph.

### Graph Conversions

## Data Structures

### Timing Demonstrations

### KD-Tree

### Oriented Bounding Box (OBB) Tree

### Octree

### Modified BSP Tree

### HyperTreeGrid

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[HyperTreeGridSource](/PythonicAPI/HyperTreeGrid/HyperTreeGridSource) | Create a vtkHyperTreeGrid.

## VTK Concepts

## Rendering

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[ColoredSphere](/PythonicAPI/Rendering/ColoredSphere) | A simple sphere.
[GradientBackground](/PythonicAPI/Rendering/GradientBackground) | Demonstrates the background shading options.
[PBR_Skybox](/PythonicAPI/Rendering/PBR_Skybox) | Demonstrates physically based rendering, a skybox and image based lighting.
[PBR_Skybox_Texturing](/PythonicAPI/Rendering/PBR_Skybox_Texturing) | Demonstrates physically based rendering, a skybox, image based lighting and texturing.
[PBR_Skybox_Anisotropy](/PythonicAPI/Rendering/PBR_Skybox_Anisotropy) | Demonstrates physically based rendering, a skybox, image based lighting, and anisotropic texturing.
[TransformSphere](/PythonicAPI/Rendering/TransformSphere) | The addition of a transform filter to [ColoredSphere](/PythonicAPI/Rendering/ColoredSphere).

## Lighting

## Texture Mapping

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[AnimateVectors](/PythonicAPI/Texture/AnimateVectors) | One frame from a vector field animation using texture maps.
[TextureCutQuadric](/PythonicAPI/Texture/TextureCutQuadric) | Cut a quadric with boolean textures.
[TextureCutSphere](/PythonicAPI/Texture/TextureCutSphere) | Examples of texture thresholding using a boolean combination of two planes to cut nested spheres.
[TexturePlane](/PythonicAPI/Texture/TexturePlane) | Example of texture mapping.
[TextureThreshold](/PythonicAPI/Texture/TextureThreshold) | Demonstrate the use of scalar thresholds to show values of flow density on three planes.

## Tutorial

If you are new to VTK then these tutorials will help to get you started.

## Visualization

See [this tutorial](http://www.vtk.org/Wiki/VTK/Tutorials/3DDataTypes) for a brief explanation of the VTK terminology of mappers, actors, etc.

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[AnnotatedCubeActor](/PythonicAPI/Visualization/AnnotatedCubeActor) | Annotated cube.
[AssignCellColorsFromLUT](/PythonicAPI/Visualization/AssignCellColorsFromLUT) | Demonstrates how to assign colors to cells in a vtkPolyData structure using lookup tables.
[BillboardTextActor3D](/PythonicAPI/Visualization/BillboardTextActor3D) | Label points with billboards.
[ColoredAnnotatedCube](/PythonicAPI/Visualization/ColoredAnnotatedCube) | How to color the individual faces of an annotated cube.
[CollisionDetection](/PythonicAPI/Visualization/CollisionDetection) | Collison between two spheres.
[CubeAxesActor](/PythonicAPI/Visualization/CubeAxesActor) | Display three orthogonal axes with  with labels.
[CurvaturesNormalsElevations](/PythonicAPI/Visualization/CurvaturesNormalsElevations) | Gaussian and Mean curvatures of a surface with arrows colored by elevation to display the normals.
[DataSetSurface](/PythonicAPI/VisualizationAlgorithms/DataSetSurface) | Cutting a hexahedron with a plane. The red line on the surface shows the cut.
[FlyingHeadSlice](/PythonicAPI/VisualizationAlgorithms/FlyingHeadSlice) | Flying edges used to generate contour lines.
[HyperStreamline](/PythonicAPI/VisualizationAlgorithms/HyperStreamline) | Example of hyperstreamlines, the four hyperstreamlines shown are integrated along the minor principal stress axis. A plane (colored with a different lookup table) is also shown.
[PointDataSubdivision](/PythonicAPI/Visualization/PointDataSubdivision) | Demonstrates the use of the vtkLinearSubdivisionFilter and vtkButterflySubdivisionFilter.
[PseudoVolumeRendering](/PythonicAPI/VolumeRendering/PseudoVolumeRendering) | Here we use 20 cut planes, each with an opacity of of 0.25. They are then rendered back-to-front to simulate volume rendering.
[QuadricVisualization](/PythonicAPI/Visualization/QuadricVisualization) | Visualizing a quadric function.
[TensorEllipsoids](/PythonicAPI/VisualizationAlgorithms/TensorEllipsoids) | Display the scaled and oriented principal axes as tensor ellipsoids representing the stress tensor.
[WarpCombustor](/PythonicAPI/VisualizationAlgorithms/WarpCombustor) | Carpet plots of combustor flow energy in a structured grid. Colors and plane displacement represent energy values.

## Working with ?vtkImageData?

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[ImageNormalize](/PythonicAPI/ImageData/ImageNormalize) | Normalize an image.

## Volume Rendering

## User Interaction

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[CallBack](/PythonicAPI/Interaction/CallBack) | Setting up a callback with client data. Two different methods are demonstrated.
[CellPicking](/PythonicAPI/Picking/CellPicking) | Cell Picking.
[HighlightPickedActor](/PythonicAPI/Picking/HighlightPickedActor) | Pick and highlight an actor based on mouse clicks.
[HighlightWithSilhouette](/PythonicAPI/Picking/HighlightWithSilhouette) | Highlight a picked actor by adding a silhouette.
[InteractorStyleTrackballActor](/PythonicAPI/Interaction/InteractorStyleTrackballActor) |
[InteractorStyleTrackballCamera](/PythonicAPI/Interaction/InteractorStyleTrackballCamera) |
[MouseEvents](/PythonicAPI/Interaction/MouseEvents) | Subclass the interactor style.
[MouseEventsObserver](/PythonicAPI/Interaction/MouseEventsObserver) | Use an observer.

## Working with Images

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[BackgroundImage](/PythonicAPI/Images/BackgroundImage) | Display an image as the "background" of a scene, and render a superquadric in front of it.

## Image Processing

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[Attenuation](/PythonicAPI/ImageProcessing/Attenuation) | This MRI image illustrates attenuation that can occur due to sensor position.  The artifact is removed by dividing by the attenuation profile determined manually.
[EnhanceEdges](/PythonicAPI/ImageProcessing/EnhanceEdges) | High-pass filters can extract and enhance edges in an image. Subtraction of the Laplacian (middle) from the original image (left) results in edge enhancement or a sharpening operation (right).
[GaussianSmooth](/PythonicAPI/ImageProcessing/GaussianSmooth) | Low-pass filters can be implemented as convolution with a Gaussian kernel.
[ImageWarp](/PythonicAPI/Images/ImageWarp) | Combine the imaging and visualization pipelines to deform an image in the z-direction. The vtkMergeFilter is used to combine the warped surface with the original color data.
[VTKSpectrum](/PythonicAPI/ImageProcessing/VTKSpectrum) | The discrete Fourier transform changes an image from the spatial domain into the frequency domain, where each pixel represents a sinusoidal function. This figure shows an image and its power spectrum displayed using a logarithmic transfer function.

## Widgets

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[BalloonWidget](/PythonicAPI/Widgets/BalloonWidget) | Uses a vtkBalloonWidget to draw labels when the mouse stays above an actor.
[CompassWidget](/PythonicAPI/Widgets/CompassWidget) | Draws an interactive compass.
[ContourWidget](/PythonicAPI/Widgets/ContourWidget) | Draw a contour (line) which can be deformed by the user.

## Plotting

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[MultiplePlots](/PythonicAPI/Plotting/MultiplePlots) | Display multiple plots by using viewports in a single render window.
[ScatterPlot](/PythonicAPI/Plotting/ScatterPlot) | Scatter plot.
[SpiderPlot](/PythonicAPI/Plotting/SpiderPlot) | Spider plot.
[SurfacePlot](/PythonicAPI/Plotting/SurfacePlot) | Surface plot.

## Animation

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[Animation](/PythonicAPI/Utilities/Animation) | Move a sphere across a scene.

## Annotation

| Example Name | Description | Image |
| -------------- | ------------- | ------- |
[TextOrigin](/PythonicAPI/Annotation/TextOrigin) | This example demonstrates the use of vtkVectorText and vtkFollower. vtkVectorText is used to create 3D annotation.

## InfoVis

## PyQt
