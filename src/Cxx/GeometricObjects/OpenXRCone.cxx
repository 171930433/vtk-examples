#include <vtkActor.h>
#include <vtkConeSource.h>
#include <vtkNamedColors.h>
#include <vtkNew.h>
#include <vtkOpenXRRenderWindow.h>
#include <vtkOpenXRRenderWindowInteractor.h>
#include <vtkOpenXRRenderer.h>
#include <vtkPolyDataMapper.h>

int main(int argc, char* argv[])
{
  // Create a cone along with a mapper and actor for it
  vtkNew<vtkConeSource> coneSource;
  coneSource->Update();
  vtkNew<vtkNamedColors> colors;
  vtkNew<vtkPolyDataMapper> mapper;
  mapper->SetInputConnection(coneSource->GetOutputPort());
  vtkNew<vtkActor> actor;
  actor->SetMapper(mapper);

  // Create OpenXR renderer, render window, and interactor
  vtkNew<vtkOpenXRRenderer> renderer;
  vtkNew<vtkOpenXRRenderWindow> renderWindow;
  renderWindow->Initialize();
  renderWindow->AddRenderer(renderer);
  vtkNew<vtkOpenXRRenderWindowInteractor> renderWindowInteractor;
  renderWindowInteractor->SetRenderWindow(renderWindow);

  // Add the actors to the scene
  renderer->AddActor(actor);
  renderer->SetBackground(colors->GetColor3d("ForestGreen").GetData());

  // Render and interact
  renderWindow->Render();
  renderWindowInteractor->Start();

  return EXIT_SUCCESS;
}
