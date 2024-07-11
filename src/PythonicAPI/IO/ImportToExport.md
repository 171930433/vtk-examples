### Description

This example imports a scene using one of vtk3DSImporter, vtkGLTFImporter, vtkOBJImporter or vtkVRMLImporter and, optionally, exports the scene using one of vtkVRMLExporter, vtkGLTFExporter, vtkX3DExporter or vtkOBJExporter.

The parameters are the input file(s) and an optional export file name with extension.

Some parameters to try out:

- ../../../src/Testing/Data/iflamingo.3ds -o ./new_iflamingo.x3d
- ../../../src/Testing/Data/sextant.wrl -o ./new_sextant.wrl
- ../../../src/Testing/Data/glTF/FlightHelmet/glTF/FlightHelmet.gltf -o ./new_FlightHelmet.gltf
- ../../../src/Testing/Data/trumpet.obj -o ./new_trumpet/new_trumpet.obj
- ../../../src/Testing/Data/doorman/doorman.obj -o ./new_doorman/doorman.obj -m ../../../src/Testing/Data/doorman/doorman.mtl -t ../../../src/Testing/Data/doorman   
