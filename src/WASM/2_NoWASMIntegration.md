# Examples excluded from WASM

Some examples do not implement a live preview feature in WebAssembly.
There are the reasons:

## No render

A lot of examples are here to show pipelines, algorithms, or utils that
does not always have a render (or whose render is not important), so we
chose not to display a live preview of those that would only show you text.

## Incompatible dependencies

Some examples use external dependencies that either could not be built in WebAssembly
(Qt) or are not Open Source (RenderMan).

Some VTK modules aren't WASM-compatible or not fully working,
like RenderingContextOpenGL2 or RenderingGL2PSOpenGL2.
Those can break some examples that are then removed from VTK-Examples-WASM:

- Images/CombineImages

- Plotting/ChartMatrix, ChartOn3DScene, Diagram, MultiplePlots, ScatterPlot, SurfacePlot

## Irrelevant features

A few examples use features that aren't relevant with WebAssembly usage
(FullScreen, OpenVR).

There are examples which are just here to show different arguments
for the same code (Rotations{A,B,C,D}, WalkCow{A,B}...).
Those are also removed for practical reasons.

## Technical considerations

In order to improve build times, stability and bandwidth,
vtk-examples-wasm does not use Boost Library features even though it is provided
by Emscripten Ports. This forces us to remove a few examples:

- Graphs/AdjacentVertexIterator, BoostBreadthFirstSearchTree

- InfoVis/MutableGraphHelper

Second issue: VTK is initially writen for OpenGL2. As VTK-WASM uses
WebGL2 (OpenGL ES3), a lot of features need to be rewritten to comply
with WebGL standards. It takes a lot of time, and a few examples will have
to wait to be fully integrated:

- Shaders/BozoShader, BozoShaderDemo, CubeMap, MarbleShader, MarbleShaderDemo, SpatterShader

- Visualization/CorrectlyRenderTranslucentGeometry

- VolumeRendering/RayCastIsosurface

At last, the fact that WebAssembly runs within the browser implies that
resources are limited for the programs. We cannot give too much memory or workload
to a single-threaded program running inside a browser tab.

- Meshes/SubdivisionDemo requires ~1GB of memory to run a sufficient number of passes

- Visualization/FroggieSurface needs to allocate a single array of 2GB.

## Full list of excluded/unstable examples:

### Animation

- AnimateActors: No animation

### DataStructures

- VisualizeKDTree: Works but error: Built-in Dual Depth Peeling is not supported on ES3

### ExplicitStructuredGrid

- CreateESGrid: ESGrid isn't rendered

### IO:

- ReadCML: vtkShaderProgram: Links failed: Varying `vertexVCGSOutput` has static-use in the frag shader, but is undeclared in the vert shader

### ImageData:
- ImageDataGeometryFilter, ImageNormalize, ImageWeightedSum: no error but render inaccurate with the screenshot

### Images:
- BackgroundImage: Background render broken

- CombineImages: Error: GLctx is undefined

- CombiningRGBChannels, ImageContinuousDilate3D, ImageContinuousErode3D, ImageCorrelation, ImageDifference, ImageMapper, ImageSobel2D, ImageText, ResizeImage: no error but render inaccurate with the screenshot

- RGBToYIQ: error YIQ color space requires negative numbers

### InfoVis:

- DelimitedTextReader: uncaught exception

### Interaction:

- UserEvent: does not compile: vtkTestFilter.h file not found

### Lighting:

- Light, LightActor: No render of lights

### Medical:

- MedicalDemo4: vtkTextureObject: failed to determine texture parameters

### Meshes:

- PointInterpolator: uncaught exception 1584136

### Modelling:

- Delaunay3DDemo: no slider

- MarchingCubes: no error but render inaccurate with the screenshot

### Picking:

- HighlightSelectedPoints: selection is "all or nothing", unable to select a portion of the points

### Plotting:

- ChartMatrix, ChartOn3DScene, MultiplePlots, ScatterPlot: points size too small

- Diagram: default view shows only half the image, full tab images works well

- PlotLine3D, SurfacePlot: Shader does not compile: Uniform `numClipPlanes` is not linkable between attached shaders

### Points:

- CompareExtractSurface, PoissonExtractSurface: does not compile: vtkPoissonReconstruction.h file not found

- ExtractEnclosedPoints: works but error in console: vtkMultiThreader unable to create a thread

- PowercrustExtractSurface: does not compile: vtkPowerCrustSurfaceReconstruction.h file not found

### PolyData:

- ExternalContour: no render of the left element

- HighlightBadCells: doesn't highlight

### Rendering:

- OutlineGlowPass: No outline

- PBR_HDR_Environment: No mipmap generation

### Shaders:

- BozoShader, BozoShaderDemo, CubeMap, MarbleShader, MarbleShaderDemo, SpatterShader: could not compile vtkShaderProgram

### StructuredGrid:

- BlankPoint: result unaccurate with screenshot

### Texture:

- AnimateVectors: Animation not working

### Utilities:

- RenderScalarToFloatBuffer: warning: readPixels: Format and type RED/FLOAT incompatible with this RGBA32F attachment

### Visualization:

- ChooseTextColorDemo: no text shown

- CorrectlyRenderTranslucentGeometry: works but Error: Built in Dual Depth Peeling is not supported on ES3

- EdgePoints: doesn't show the model

- ExtrudePolyDataAlongLine: does not compile: vtkFrenetSerretFrame.h not found

- FroggieSurface: WebGL2RenderingContext.bufferData: Argument 2 can't be an ArrayBuffer or an ArrayBufferView larger than 2 GB

- RandomProbe: Error: indirect call to null

- LabeledMesh: Labels display at random positions

- TextureMapImageData: no texture

### VolumeRendering:

- FixedPointVolumeRayCastMapperCT, MinIntensityRendering, SimpleRayCast: Failed to determine texture parameters

- RayCastIsosurface: shader failed to compile

### Widgets:

- CameraOrientationWidget: Widget not showing

- SeedWidgetImage: image rendering broken
