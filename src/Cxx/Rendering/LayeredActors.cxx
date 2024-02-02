#include <vtkActor.h>
#include <vtkAxesActor.h>
#include <vtkCallbackCommand.h>
#include <vtkCamera.h>
#include <vtkCubeSource.h>
#include <vtkInteractorObserver.h>
#include <vtkInteractorStyleTrackballCamera.h>
#include <vtkNamedColors.h>
#include <vtkNew.h>
#include <vtkPolyDataMapper.h>
#include <vtkProperty.h>
#include <vtkRenderWindow.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkRenderer.h>
#include <vtkRendererCollection.h>
#include <vtkTransform.h>

#include <array>
#include <cstdlib>
#include <iostream>

namespace {
/**
 * Copy an array to the internal buffer within the vector class.
 *
 * @param arr - The array.
 * @return - The vector corresponding to the array.
 */
template <typename T>
std::vector<T> CopyArrayToVector(T* arr, std::size_t arr_len)
{
  return std::vector<T>(arr, arr + arr_len);
}

//! The positional information relating to the camera.
struct Orientation
{
  std::vector<double> position{0.0, 0.0, 0.0};
  std::vector<double> focalPoint{0.0, 0.0, 0.0};
  std::vector<double> viewUp{0.0, 0.0, 0.0};
  double distance = 0;
  std::vector<double> clipplingRange{0.0, 0.0};
  std::vector<double> orientation{0.0, 0.0, 0.0};
};

/**
 * Select the layer to manipulate.
 */
void SelectLayer(vtkObject* caller, long unsigned int eventId, void* clientData,
                 void* callData);

/**
 * Orient layer 0 based on the camera orientation in layer 1 or vice versa.
 */
void OrientLayer(vtkObject* caller, long unsigned int eventId, void* clientData,
                 void* callData);

//! Get the camera orientation.
/*
 * @param ren - the renderer.
 * @return The orientation parameters.
 */
Orientation GetOrientation(vtkRenderer* ren);

//! Set the camera orientation.
/*
 *
 * @param ren - the renderer.
 * @param p - The orientation parameters.
 * @return
 */
void SetOrientation(vtkRenderer* ren, Orientation const& p);

} // namespace

int main(int, char*[])
{
  vtkNew<vtkNamedColors> colors;

  vtkNew<vtkCubeSource> cubeSource;
  cubeSource->SetXLength(4.0);
  cubeSource->SetYLength(9.0);
  cubeSource->SetZLength(1.0);
  cubeSource->SetCenter(0.0, 0.0, 0.0);

  // Make the slab and axes actors.
  vtkNew<vtkPolyDataMapper> cubeMapper;
  cubeMapper->SetInputConnection(cubeSource->GetOutputPort());

  vtkNew<vtkProperty> back;
  back->SetColor(colors->GetColor3d("Sienna").GetData());

  vtkNew<vtkActor> cubeActor;
  cubeActor->GetProperty()->SetDiffuseColor(
      colors->GetColor3d("BurlyWood").GetData());
  cubeActor->SetMapper(cubeMapper);
  cubeActor->GetProperty()->EdgeVisibilityOn();
  cubeActor->GetProperty()->SetLineWidth(2.0);
  cubeActor->GetProperty()->SetEdgeColor(
      colors->GetColor3d("PapayaWhip").GetData());
  cubeActor->SetBackfaceProperty(back);

  vtkNew<vtkTransform> transform;
  transform->Translate(0.0, 0.0, 0.0);

  vtkNew<vtkAxesActor> axes;
  // The axes can be positioned with a user transform.
  axes->SetUserTransform(transform);

  // The renderers, render window and interactor.
  std::array<vtkNew<vtkRenderer>, 2> renderers;
  vtkNew<vtkRenderWindow> renWin;
  for (auto&& ren : renderers)
  {
    renWin->AddRenderer(ren);
  }
  renWin->SetSize(800, 800);
  renWin->SetWindowName("LayeredActors");

  vtkNew<vtkRenderWindowInteractor> iRen;
  iRen->SetRenderWindow(renWin);

  vtkNew<vtkInteractorStyleTrackballCamera> style;
  iRen->SetInteractorStyle(style);

  // Define the renderers and allocate them to layers.
  // Layer 0 - background not transparent.
  renderers[0]->SetBackground(colors->GetColor3d("DarkSlateGray").GetData());
  renderers[0]->AddActor(cubeActor);
  renderers[0]->SetLayer(0);

  // Layer 1 - the background is transparent,
  //       so we only see the layer 0 background color
  renderers[1]->AddActor(axes);
  renderers[1]->SetBackground(colors->GetColor3d("MidnightBlue").GetData());
  renderers[1]->SetLayer(1);

  // Set a common camera view for each layer.
  for (const auto& renderer : renderers)
  {
    auto camera = renderer->GetActiveCamera();
    camera->Elevation(-30.0);
    camera->Azimuth(-30.0);
    renderer->ResetCamera();
  }

  // We have two layers.
  renWin->SetNumberOfLayers(static_cast<int>(renderers.size()));

  renWin->Render();

  vtkNew<vtkCallbackCommand> selectLayerCB;
  selectLayerCB->SetCallback(SelectLayer);
  iRen->AddObserver(vtkCommand::KeyPressEvent, selectLayerCB);
  vtkNew<vtkCallbackCommand> orientLayerCB;
  orientLayerCB->SetCallback(OrientLayer);
  iRen->AddObserver(vtkCommand::EndInteractionEvent, orientLayerCB);

  iRen->Start();

  return EXIT_SUCCESS;
}

namespace {
void SelectLayer(vtkObject* caller, long unsigned int vtkNotUsed(eventId),
                 void* vtkNotUsed(clientData), void* vtkNotUsed(callData))
{
  vtkRenderWindowInteractor* iRen =
      static_cast<vtkRenderWindowInteractor*>(caller);
  vtkRendererCollection* renderers = iRen->GetRenderWindow()->GetRenderers();
  if (renderers->GetNumberOfItems() < 2)
  {
    std::cerr << "We need at least two renderers, we have only "
              << renderers->GetNumberOfItems() << std::endl;
    return;
  }
  renderers->InitTraversal();
  // Top item.
  vtkRenderer* ren0 = renderers->GetNextItem();
  // Bottom item.
  vtkRenderer* ren1 = renderers->GetNextItem();

  std::string key = iRen->GetKeySym();

  if (key == "0")
  {
    std::cout << "Selected layer: " << key << std::endl;
    iRen->GetRenderWindow()
        ->GetInteractor()
        ->GetInteractorStyle()
        ->SetDefaultRenderer(ren0);
    ren0->InteractiveOn();
    ren1->InteractiveOff();
  }
  if (key == "1")
  {
    std::cout << "Selected layer: " << key << std::endl;
    iRen->GetRenderWindow()
        ->GetInteractor()
        ->GetInteractorStyle()
        ->SetDefaultRenderer(ren1);
    ren0->InteractiveOff();
    ren1->InteractiveOn();
  }
}

void OrientLayer(vtkObject* caller, long unsigned int vtkNotUsed(eventId),
                 void* vtkNotUsed(clientData), void* vtkNotUsed(callData))
{
  vtkRenderWindowInteractor* iRen =
      static_cast<vtkRenderWindowInteractor*>(caller);
  vtkRendererCollection* renderers = iRen->GetRenderWindow()->GetRenderers();
  if (renderers->GetNumberOfItems() < 2)
  {
    std::cerr << "We need at least two renderers, we have only "
              << renderers->GetNumberOfItems() << std::endl;
    return;
  }
  renderers->InitTraversal();
  // Top item.
  vtkRenderer* ren0 = renderers->GetNextItem();
  // Bottom item.
  vtkRenderer* ren1 = renderers->GetNextItem();

  if (ren1->GetInteractive())
  {
    auto orient1 = GetOrientation(ren1);
    SetOrientation(ren0, orient1);
    ren0->ResetCamera();
  }
  else
  {
    auto orient0 = GetOrientation(ren0);
    SetOrientation(ren1, orient0);
    ren1->ResetCamera();
  }
}

Orientation GetOrientation(vtkRenderer* ren)
{
  Orientation p;

  vtkCamera* camera = ren->GetActiveCamera();
  p.position = CopyArrayToVector<double>(camera->GetPosition(), 3);
  p.focalPoint = CopyArrayToVector<double>(camera->GetFocalPoint(), 3);
  p.viewUp = CopyArrayToVector<double>(camera->GetViewUp(), 3);
  p.distance = camera->GetDistance();
  p.clipplingRange = CopyArrayToVector<double>(camera->GetClippingRange(), 2);
  p.orientation = CopyArrayToVector<double>(camera->GetOrientation(), 3);

  return p;
}

void SetOrientation(vtkRenderer* ren, Orientation const& p)
{
  vtkCamera* camera = ren->GetActiveCamera();
  camera->SetPosition(p.position.data());
  camera->SetFocalPoint(p.focalPoint.data());
  camera->SetViewUp(p.viewUp.data());
  camera->SetDistance(p.distance);
  camera->SetClippingRange(p.clipplingRange.data());
}

} // namespace
