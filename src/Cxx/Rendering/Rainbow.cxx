#include <vtkSmartPointer.h>

#include <vtkMultiBlockPLOT3DReader.h>
#include <vtkMultiBlockDataSet.h>
#include <vtkActor.h>
#include <vtkActor.h>
#include <vtkCamera.h>
#include <vtkLookupTable.h>
#include <vtkPolyDataMapper.h>
#include <vtkPolyDataMapper.h>
#include <vtkRenderWindow.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkRenderer.h>
#include <vtkStructuredGrid.h>
#include <vtkStructuredGridGeometryFilter.h>
#include <vtkStructuredGridOutlineFilter.h>
#include <vtkNamedColors.h>

// This example demonstrates the use and manipulation of lookup tables.

// First create pipeline a simple pipeline that reads a structure grid
// and then extracts a plane from the grid. The plane will be colored
// differently by using different lookup tables.
//
// Note: the Update method is manually invoked because it causes the
// reader to read; later on we use the output of the reader to set
// a range for the scalar values.
int main (int argc, char *argv[])
{
  if (argc < 3)
  {
    std::cout << "Usage: " << argv[0] << " file.xyz file.bin" << std::endl;
    return EXIT_FAILURE;
  }
  vtkSmartPointer<vtkNamedColors> colors =
    vtkSmartPointer<vtkNamedColors>::New();

  vtkSmartPointer<vtkMultiBlockPLOT3DReader> pl3d =
    vtkSmartPointer<vtkMultiBlockPLOT3DReader>::New();
  pl3d->SetXYZFileName(argv[1]);
  pl3d->SetQFileName(argv[2]);
  pl3d->SetScalarFunctionNumber(100);
  pl3d->SetVectorFunctionNumber(202);
  pl3d->Update();

  vtkStructuredGrid *pl3dOutput =
    vtkStructuredGrid::SafeDownCast(pl3d->GetOutput()->GetBlock(0));

  vtkSmartPointer<vtkStructuredGridGeometryFilter> plane =
    vtkSmartPointer<vtkStructuredGridGeometryFilter>::New();
  plane->SetInputData(pl3dOutput);
  plane->SetExtent( 1, 100, 1, 100, 7, 7);

  vtkSmartPointer<vtkLookupTable> lut =
    vtkSmartPointer<vtkLookupTable>::New();

  vtkSmartPointer<vtkPolyDataMapper> planeMapper =
    vtkSmartPointer<vtkPolyDataMapper>::New();
  planeMapper->SetLookupTable(lut);
  planeMapper->SetInputConnection(plane->GetOutputPort());
  planeMapper->SetScalarRange(pl3dOutput->GetScalarRange());

  vtkSmartPointer<vtkActor> planeActor =
    vtkSmartPointer<vtkActor>::New();
  planeActor->SetMapper(planeMapper);

  // This creates an outline around the data.

  vtkSmartPointer<vtkStructuredGridOutlineFilter> outline =
    vtkSmartPointer<vtkStructuredGridOutlineFilter>::New();
  outline->SetInputData(pl3dOutput);

  vtkSmartPointer<vtkPolyDataMapper> outlineMapper =
    vtkSmartPointer<vtkPolyDataMapper>::New();
  outlineMapper->SetInputConnection(outline->GetOutputPort());

  vtkSmartPointer<vtkActor> outlineActor =
    vtkSmartPointer<vtkActor>::New();
  outlineActor->SetMapper(outlineMapper);

  // Much of the following is commented out. To try different lookup tables,
  // uncommented the appropriate portions.
  //

  // This creates a black to white lut.
  //    lut SetHueRange 0 0
  //    lut SetSaturationRange 0 0
  //    lut SetValueRange 0.2 1.0

  // This creates a red to blue lut.
  //    lut SetHueRange 0.0 0.667

  // This creates a blue to red lut.
  //    lut SetHueRange 0.667 0.0

  // This creates a weird effect. The Build() method causes the lookup table
  // to allocate memory and create a table based on the currect hue, saturation,
  // value, and alpha (transparency) range. Here we then manually overwrite the
  // values generated by the Build() method.
  lut->SetNumberOfColors(256);
  lut->SetHueRange(0.0, 0.667 );
  lut->Build();

  // Create the RenderWindow, Renderer and both Actors
  //
  vtkSmartPointer<vtkRenderer> ren1 =
    vtkSmartPointer<vtkRenderer>::New();
  vtkSmartPointer<vtkRenderWindow> renWin =
    vtkSmartPointer<vtkRenderWindow>::New();
  renWin->AddRenderer(ren1);
  vtkSmartPointer<vtkRenderWindowInteractor> iren =
    vtkSmartPointer<vtkRenderWindowInteractor>::New();
  iren->SetRenderWindow(renWin);

  // Add the actors to the renderer, set the background and size
  //
  ren1->AddActor(outlineActor);
  ren1->AddActor(planeActor);

  ren1->SetBackground(colors->GetColor3d("SlateGray").GetData());
  ren1->TwoSidedLightingOff();

  renWin->SetSize( 512, 512);

  iren->Initialize();

  vtkCamera *cam1 = ren1->GetActiveCamera();
  cam1->SetClippingRange( 3.95297, 50);
  cam1->SetFocalPoint( 8.88908, 0.595038, 29.3342);
  cam1->SetPosition( -12.3332, 31.7479, 41.2387);
  cam1->SetViewUp(0.060772, -0.319905, 0.945498);

  iren->Start();
  return EXIT_SUCCESS;
}
