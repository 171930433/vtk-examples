#include <vtkActor.h>
#include <vtkCamera.h>
#include <vtkCellTypes.h>
#include <vtkClipDataSet.h>
#include <vtkDataSetMapper.h>
#include <vtkNamedColors.h>
#include <vtkNew.h>
#include <vtkPlane.h>
#include <vtkProperty.h>
#include <vtkRenderWindow.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkRenderer.h>
#include <vtkTransform.h>
#include <vtkUnstructuredGrid.h>
#include <vtkUnstructuredGridReader.h>

#include <iostream>
#include <string>

int main(int argc, char* argv[])
{
  if (argc < 2)
  {
    std::cout << "Usage: " << argv[0] << " filename.vtk e.g. treemesh.vtk"
              << std::endl;
    return EXIT_FAILURE;
  }

  // If false, output using the original code.
  auto correctOutput = true;

  // Create the reader for the data.
  std::string filename = argv[1];
  std::cout << "Loading " << filename.c_str() << std::endl;
  vtkNew<vtkUnstructuredGridReader> reader;
  reader->SetFileName(filename.c_str());
  reader->Update();

  double bounds[6];
  reader->GetOutput()->GetBounds(bounds);
  double center[3];
  reader->GetOutput()->GetCenter(center);

  vtkNew<vtkNamedColors> colors;
  vtkNew<vtkRenderer> renderer;
  renderer->SetBackground(colors->GetColor3d("Wheat").GetData());
  renderer->UseHiddenLineRemovalOn();

  vtkNew<vtkRenderWindow> renderWindow;
  renderWindow->AddRenderer(renderer);
  renderWindow->SetSize(640, 480);

  vtkNew<vtkRenderWindowInteractor> interactor;
  interactor->SetRenderWindow(renderWindow);

  double xnorm[3] = {-1.0, -1.0, 1.0};

  vtkNew<vtkPlane> clipPlane;
  clipPlane->SetOrigin(reader->GetOutput()->GetCenter());
  clipPlane->SetNormal(xnorm);

  vtkNew<vtkClipDataSet> clipper;
  vtkNew<vtkClipDataSet> clipper1;

  if (correctOutput)
  {
    clipper->SetClipFunction(clipPlane);
    clipper->SetInputData(reader->GetOutput());
    clipper->SetValue(0.0);
    clipper->GenerateClippedOutputOn();
    clipper->Update();

    // Set inside out, generate the clipped output and
    //  use the clipped output for the clipped mapper.
    // If this is done a similar image to
    //  ClipUnstructuredGridWithPlane is created.
    clipper1->SetClipFunction(clipPlane);
    clipper1->SetInputData(reader->GetOutput());
    clipper1->SetValue(0.0);
    clipper1->InsideOutOn();
    clipper1->GenerateClippedOutputOn();
    clipper1->Update();
  }
  else
  {
    clipper->SetClipFunction(clipPlane);
    clipper->SetInputData(reader->GetOutput());
    clipper->SetValue(0.0);
    clipper->GenerateClippedOutputOn();
    clipper->Update();
  }

  vtkNew<vtkDataSetMapper> insideMapper;
  insideMapper->SetInputData(clipper->GetOutput());
  insideMapper->ScalarVisibilityOff();

  vtkNew<vtkActor> insideActor;
  insideActor->SetMapper(insideMapper);
  insideActor->GetProperty()->SetDiffuseColor(
      colors->GetColor3d("Banana").GetData());
  insideActor->GetProperty()->SetAmbient(0.3);
  insideActor->GetProperty()->EdgeVisibilityOn();

  vtkNew<vtkDataSetMapper> clippedMapper;
  if (correctOutput)
  {
    clippedMapper->SetInputData(clipper1->GetClippedOutput());
  }
  else
  {
    clippedMapper->SetInputData(clipper->GetClippedOutput());
  }
  clippedMapper->ScalarVisibilityOff();

  vtkNew<vtkActor> clippedActor;
  clippedActor->SetMapper(clippedMapper);
  clippedActor->GetProperty()->SetDiffuseColor(
      colors->GetColor3d("Tomato").GetData());
  insideActor->GetProperty()->SetAmbient(0.3);
  clippedActor->GetProperty()->EdgeVisibilityOn();

  // Create transforms to make a better visualization
  vtkNew<vtkTransform> insideTransform;
  insideTransform->Translate(-(bounds[1] - bounds[0]) * .75, 0, 0);
  insideTransform->Translate(center[0], center[1], center[2]);
  insideTransform->RotateY(-120.0);
  insideTransform->Translate(-center[0], -center[1], -center[2]);
  insideActor->SetUserTransform(insideTransform);

  vtkNew<vtkTransform> clippedTransform;
  clippedTransform->Translate((bounds[1] - bounds[0]) * .75, 0, 0);
  clippedTransform->Translate(center[0], center[1], center[2]);
  if (correctOutput)
  {
    clippedTransform->RotateY(60.0);
  }
  else
  {
    clippedTransform->RotateY(-120.0);
  }
  clippedTransform->Translate(-center[0], -center[1], -center[2]);
  clippedActor->SetUserTransform(clippedTransform);

  renderer->AddViewProp(clippedActor);
  renderer->AddViewProp(insideActor);

  renderer->ResetCamera();
  renderer->GetActiveCamera()->Dolly(1.4);
  renderer->ResetCameraClippingRange();
  renderWindow->Render();
  renderWindow->SetWindowName("ClipUnstructuredGridWithPlane2");
  renderWindow->Render();

  interactor->Start();

  // Generate a report
  vtkIdType numberOfCells = clipper->GetOutput()->GetNumberOfCells();
  std::cout << "------------------------" << std::endl;
  std::cout << "The inside dataset contains a " << std::endl
            << clipper->GetOutput()->GetClassName() << " that has "
            << numberOfCells << " cells" << std::endl;
  typedef std::map<int, int> CellContainer;
  CellContainer cellMap;
  for (vtkIdType i = 0; i < numberOfCells; i++)
  {
    cellMap[clipper->GetOutput()->GetCellType(i)]++;
  }

  for (auto c : cellMap)
  {
    std::cout << "\tCell type " << vtkCellTypes::GetClassNameFromTypeId(c.first)
              << " occurs " << c.second << " times." << std::endl;
  }

  std::cout << "------------------------" << std::endl;
  CellContainer outsideCellMap;
  if (correctOutput)
  {
    numberOfCells = clipper1->GetClippedOutput()->GetNumberOfCells();
    std::cout << "The clipped dataset contains a " << std::endl
              << clipper1->GetClippedOutput()->GetClassName() << " that has "
              << numberOfCells << " cells" << std::endl;
    for (vtkIdType i = 0; i < numberOfCells; i++)
    {
      outsideCellMap[clipper1->GetClippedOutput()->GetCellType(i)]++;
    }
  }
  else
  {
    numberOfCells = clipper->GetClippedOutput()->GetNumberOfCells();
    std::cout << "The clipped dataset contains a " << std::endl
              << clipper->GetClippedOutput()->GetClassName() << " that has "
              << numberOfCells << " cells" << std::endl;
    for (vtkIdType i = 0; i < numberOfCells; i++)
    {
      outsideCellMap[clipper->GetClippedOutput()->GetCellType(i)]++;
    }
  }

  for (auto c : outsideCellMap)
  {
    std::cout << "\tCell type " << vtkCellTypes::GetClassNameFromTypeId(c.first)
              << " occurs " << c.second << " times." << std::endl;
  }
  return EXIT_SUCCESS;
}
