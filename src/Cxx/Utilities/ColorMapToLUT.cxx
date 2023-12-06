#include <vtkActor.h>
#include <vtkConeSource.h>
#include <vtkDiscretizableColorTransferFunction.h>
#include <vtkElevationFilter.h>
#include <vtkInteractorStyleTrackballCamera.h>
#include <vtkNamedColors.h>
#include <vtkNew.h>
#include <vtkPolyDataMapper.h>
#include <vtkProperty.h>
#include <vtkRenderWindow.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkRenderer.h>
// #include <vtkSphereSource.h>

#include <array>

namespace {
vtkNew<vtkDiscretizableColorTransferFunction> GetCTF();

}

int main(int, char*[])
{
  std::array<unsigned char, 4> bkg{82, 87, 110, 255};
  vtkNew<vtkNamedColors> colors;
  colors->SetColor("ParaViewBkg", bkg.data());

  vtkNew<vtkRenderer> ren;
  ren->SetBackground(colors->GetColor3d("ParaViewBkg").GetData());
  vtkNew<vtkRenderWindow> renWin;
  renWin->SetSize(640, 480);
  renWin->SetWindowName("ColorMapToLUT");
  renWin->AddRenderer(ren);
  vtkNew<vtkRenderWindowInteractor> iRen;
  iRen->SetRenderWindow(renWin);

  vtkNew<vtkInteractorStyleTrackballCamera> style;
  iRen->SetInteractorStyle(style);

  // vtkNew<vtkSphereSource> sphere;
  // sphere->SetThetaResolution(64);
  // sphere->SetPhiResolution(32);
  // auto bounds = sphere->GetOutput()->GetBounds();

  vtkNew<vtkConeSource> cone;
  cone->SetResolution(6);
  cone->SetDirection(0, 1, 0);
  cone->SetHeight(1);
  cone->Update();
  auto bounds = cone->GetOutput()->GetBounds();

  vtkNew<vtkElevationFilter> elevation_filter;
  elevation_filter->SetLowPoint(0, bounds[2], 0);
  elevation_filter->SetHighPoint(0, bounds[3], 0);
  elevation_filter->SetInputConnection(cone->GetOutputPort());
  // elevation_filter->SetInputConnection(sphere->GetOutputPort());

  auto ctf = GetCTF();

  vtkNew<vtkPolyDataMapper> mapper;
  mapper->SetInputConnection(elevation_filter->GetOutputPort());
  mapper->SetLookupTable(ctf);
  mapper->SetColorModeToMapScalars();
  mapper->InterpolateScalarsBeforeMappingOn();

  vtkNew<vtkActor> actor;
  actor->SetMapper(mapper);

  ren->AddActor(actor);

  renWin->Render();
  iRen->Start();

  return EXIT_SUCCESS;
}

namespace {
vtkNew<vtkDiscretizableColorTransferFunction> GetCTF()
{
  // name: Fast, creator: Francesca Samsel and Alan W. Scott
  // interpolationspace: lab, interpolationtype: linear, space: RGB
  // file name: Fast.xml

  vtkNew<vtkDiscretizableColorTransferFunction> ctf;

  ctf->SetColorSpaceToLab();
  ctf->SetScaleToLinear();

  ctf->SetNanColor(0, 0, 0);
  ctf->SetAboveRangeColor(0, 0, 0);
  ctf->UseAboveRangeColorOn();
  ctf->SetBelowRangeColor(0, 0, 0);
  ctf->UseBelowRangeColorOn();

  ctf->AddRGBPoint(0, 0.05639999999999999, 0.05639999999999999, 0.47);
  ctf->AddRGBPoint(0.17159223942480895, 0.24300000000000013, 0.4603500000000004,
                   0.81);
  ctf->AddRGBPoint(0.2984914818394138, 0.3568143826543521, 0.7450246485363142,
                   0.954367702893722);
  ctf->AddRGBPoint(0.4321287371255907, 0.6882, 0.93, 0.9179099999999999);
  ctf->AddRGBPoint(0.5, 0.8994959551205902, 0.944646394975174,
                   0.7686567142818399);
  ctf->AddRGBPoint(0.5882260353170073, 0.957107977357604, 0.8338185108985666,
                   0.5089156299842102);
  ctf->AddRGBPoint(0.7061412605695164, 0.9275207599610714, 0.6214389091739178,
                   0.31535705838676426);
  ctf->AddRGBPoint(0.8476395308725272, 0.8, 0.3520000000000001,
                   0.15999999999999998);
  ctf->AddRGBPoint(1, 0.59, 0.07670000000000013, 0.11947499999999994);

  ctf->SetNumberOfValues(9);
  ctf->DiscretizeOff();

  return ctf;
}

} // namespace
