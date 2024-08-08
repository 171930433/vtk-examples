#include <vtkActor2D.h>
#include <vtkActor.h>
#include <vtkNamedColors.h>
#include <vtkNew.h>
#include <vtkSmartPointer.h>
#include <vtkSphereSource.h>
#include <vtkPointSource.h>
#include <vtkConeSource.h>
#include <vtkNamedColors.h>

#include <vtkPolyDataMapper.h>
#include <vtkProperty.h>
#include <vtkRenderer.h>
#include <vtkTextMapper.h>
#include <vtkTextProperty.h>

#include <vtkRenderWindow.h>
#include <vtkCamera.h>
#include <vtkRenderWindowInteractor.h>

#include <array>
#include <vector>
template <typename _T> using vtkSP = vtkSmartPointer<_T>;

template <typename _T> auto vtkmake_shared()
{
  return vtkSmartPointer<_T>::New();
}

int main()
{

  // Set the background color.
  vtkNew<vtkNamedColors> colors;
  std::array<unsigned char, 4> bkg{51, 77, 102, 255};
  colors->SetColor("BkgColor", bkg.data());

  // 绘制几何物体
  std::vector<vtkSP<vtkPolyDataAlgorithm>> sourceObjects;

  // sphera
  auto sphere = vtkmake_shared<vtkSphereSource>();
  sphere->SetPhiResolution(21);
  sphere->SetThetaResolution(21);
  sourceObjects.push_back(sphere);

  // cone
  auto cone = vtkmake_shared<vtkConeSource>();
  cone->SetResolution(51);
  cone->SetHeight(1.0);
  sourceObjects.push_back(cone);

  // point
  auto points = vtkmake_shared<vtkPointSource>();
  points->SetNumberOfPoints(500);
  sourceObjects.push_back(points);

  //
  std::vector<vtkSP<vtkRenderer>> renderers;
  std::vector<vtkSP<vtkPolyDataMapper>> mappers;
  std::vector<vtkSP<vtkActor>> actors;
  std::vector<vtkSP<vtkTextMapper>> text_mappers;
  std::vector<vtkSP<vtkActor2D>> text_actors;

  // Create one text property for all
  vtkNew<vtkTextProperty> text_property;
  text_property->SetFontSize(16);
  text_property->SetJustificationToCentered();
  text_property->SetColor(colors->GetColor3d("LightGoldenrodYellow").GetData());

  vtkNew<vtkProperty> backProperty;
  backProperty->SetColor(colors->GetColor3d("Tomato").GetData());

  // Create a source, renderer, mapper, and actor for each object
  for (int i = 0; i < sourceObjects.size(); ++i)
  {
    mappers.push_back(vtkmake_shared<vtkPolyDataMapper>());
    mappers.back()->SetInputConnection(sourceObjects[i]->GetOutputPort());

    actors.push_back(vtkmake_shared<vtkActor>());
    actors.back()->SetMapper(mappers.back());
    actors.back()->GetProperty()->SetColor(
        colors->GetColor3d("PeachPuff").GetData());
    actors.back()->SetBackfaceProperty(backProperty);

    // 文字部分
    text_mappers.push_back(vtkmake_shared<vtkTextMapper>());
    text_mappers.back()->SetInput(sourceObjects[i]->GetClassName());
    text_mappers.back()->SetTextProperty(text_property);

    text_actors.push_back(vtkmake_shared<vtkActor2D>());
    text_actors.back()->SetMapper(text_mappers.back());
    text_actors.back()->SetPosition(120, 16);

    renderers.push_back(vtkmake_shared<vtkRenderer>());
  }

  auto gridDimensions = 3;
  vtkNew<vtkRenderWindow> render_window;
  render_window->SetWindowName("SourceObjectsDemo2");

  //
  for (int row = 0; row < gridDimensions; ++row)
  {
    for (int col = 0; col < gridDimensions; ++col)
    {
      auto index = row * gridDimensions + col;
      if (index >= sourceObjects.size())
      {
        break;
      }
      auto x0 = double(col) / gridDimensions;
      auto y0 = double(gridDimensions - row - 1) / gridDimensions;
      auto x1 = double(col + 1) / gridDimensions;
      auto y1 = double(gridDimensions - row) / gridDimensions;

      auto current_render = renderers[index];
      render_window->AddRenderer(current_render);

      current_render->SetViewport(x0, y0, x1, y1);
      current_render->AddActor(actors[index]);
      current_render->AddActor(text_actors[index]);
      current_render->SetBackground(colors->GetColor3d("BkgColor").GetData());
      current_render->ResetCamera();
      current_render->GetActiveCamera()->Azimuth(30);
      current_render->GetActiveCamera()->Elevation(30);
      current_render->GetActiveCamera()->Zoom(0.8);
      current_render->ResetCameraClippingRange();
    }
  }

  vtkNew<vtkRenderWindowInteractor> interactor;
  interactor->SetRenderWindow(render_window);

  render_window->Render();
  interactor->Start();

  return 0;
}