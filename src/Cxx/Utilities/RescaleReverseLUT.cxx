#include <vtkActor.h>
#include <vtkActor2D.h>
#include <vtkCylinderSource.h>
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
#include <vtkScalarBarActor.h>
#include <vtkSmartPointer.h>
#include <vtkTextMapper.h>
#include <vtkTextProperty.h>

#include <array>
#include <string>
#include <vector>

namespace {
/**
 * Generate the color transfer function.
 *
 * The seven colors corresponding to the colors that Isaac Newton labelled
 *     when dividing the spectrum of visible light in 1672 are used.
 *
 * The modern variant of these colors can be selected and used instead.
 *
 * See: [Rainbow](https://en.wikipedia.org/wiki/Rainbow)
 *
 * @param modern: Selects either Newton's original seven colors or the modern
 * version.
 *
 * @return The color transfer function.
 */
vtkNew<vtkDiscretizableColorTransferFunction>
GetCTF(bool const& modern = false);

/**
 * Generate a new color transfer function from the old one,
 * adding in the new x and rgb values.
 *
 * @param oldCTF: The old color transfer function.
 * @param newX: The new color x-values.
 * @param newRGB: The color RGB values.
 * @param reverse: If true, reverse the colors.
 *
 * @return The new color transfer function.
 */
vtkNew<vtkDiscretizableColorTransferFunction>
GenerateNewCTF(vtkNew<vtkDiscretizableColorTransferFunction> const& oldCTF,
               std::vector<double> const& newX,
               std::vector<std::array<double, 3>> const& newRGB,
               bool const& reverse = false);

/**
 * Rescale the values.
 *
 * See:
 * https://stats.stackexchange.com/questions/25894/changing-the-scale-of-a-variable-to-0-100
 *
 * @param xv: The values to be rescaled.
 * @param newMin: The new minimum value.
 * @param newMax: The new maximum value.
 *
 * @return The rescaled values.
 */
std::vector<double> Rescale(std::vector<double> const& xv,
                            double const& newMin = 0, double const& newMax = 1);

/**
 * Rescale and, optionally, reverse the colors in the color transfer function.
 *
 * @param ctf: The color transfer function to rescale.
 * @param newMin: The new minimum value.
 * @param newMax: The new maximum value.
 * @param reverse: If true, reverse the colors.
 *
 * @return The rescaled color transfer function.
 */
vtkNew<vtkDiscretizableColorTransferFunction>
RescaleCTF(vtkNew<vtkDiscretizableColorTransferFunction> const& ctf,
           double const& newMin = 0, double const& newMax = 1,
           bool const& reverse = false);
} // namespace

int main(int, char*[])
{
  std::array<unsigned char, 4> bkg{82, 87, 110, 255};
  vtkNew<vtkNamedColors> colors;
  colors->SetColor("ParaViewBkg", bkg.data());

  vtkNew<vtkRenderWindow> renWin;
  renWin->SetSize(640 * 2, 480 * 2);
  renWin->SetWindowName("RescaleReverseLUT");
  vtkNew<vtkRenderWindowInteractor> iRen;
  iRen->SetRenderWindow(renWin);

  vtkNew<vtkInteractorStyleTrackballCamera> style;
  iRen->SetInteractorStyle(style);

  std::vector<vtkNew<vtkDiscretizableColorTransferFunction>> ctf;
  ctf.push_back(GetCTF(false));
  const double* tmp = ctf[0]->GetRange();
  ctf.push_back(RescaleCTF(ctf[0], 0, 1, false));
  ctf.push_back(RescaleCTF(ctf[0], tmp[0], tmp[1], true));
  ctf.push_back(RescaleCTF(ctf[0], 0, 1, true));

  // Define viewport ranges.
  std::array<double, 4> xMins{0.0, 0.0, 0.5, 0.5};
  std::array<double, 4> xMaxs{0.5, 0.5, 1.0, 1.0};
  std::array<double, 4> yMins{0.5, 0.0, 0.5, 0.0};
  std::array<double, 4> yMaxs{1.0, 0.5, 1.0, 0.5};

  // Define titles.
  std::vector<std::string> titles{"Orginal", "Rescaled", "Reversed",
                                  "Rescaled and Reversed"};

  // Create a common text property->
  vtkNew<vtkTextProperty> textProperty;
  textProperty->SetFontSize(36);
  textProperty->SetJustificationToCentered();
  textProperty->SetColor(colors->GetColor3d("LightGoldenrodYellow").GetData());

  std::vector<vtkSmartPointer<vtkCylinderSource>> sources;
  std::vector<vtkSmartPointer<vtkElevationFilter>> elevation_filters;
  std::vector<vtkSmartPointer<vtkPolyDataMapper>> mappers;
  std::vector<vtkSmartPointer<vtkActor>> actors;
  std::vector<vtkSmartPointer<vtkScalarBarActor>> scalarBars;
  std::vector<vtkSmartPointer<vtkRenderer>> renderers;
  std::vector<vtkSmartPointer<vtkTextMapper>> textMappers;
  std::vector<vtkSmartPointer<vtkActor2D>> textActors;

  for (auto i = 0; i < 4; ++i)
  {
    vtkNew<vtkCylinderSource> cylinder;
    cylinder->SetCenter(0.0, 0.0, 0.0);
    cylinder->SetResolution(6);
    cylinder->Update();
    double* bounds = cylinder->GetOutput()->GetBounds();
    sources.push_back(cylinder);

    vtkNew<vtkElevationFilter> elevation_filter;
    elevation_filter->SetScalarRange(0, 1);
    elevation_filter->SetLowPoint(0, bounds[2], 0);
    elevation_filter->SetHighPoint(0, bounds[3], 0);
    elevation_filter->SetInputConnection(sources[i]->GetOutputPort());
    elevation_filters.push_back(elevation_filter);

    vtkNew<vtkPolyDataMapper> mapper;
    mapper->SetInputConnection(elevation_filters[i]->GetOutputPort());
    mapper->SetLookupTable(ctf[i]);
    mapper->SetColorModeToMapScalars();
    mapper->InterpolateScalarsBeforeMappingOn();
    mappers.push_back(mapper);

    vtkNew<vtkActor> actor;
    actor->SetMapper(mappers[i]);
    actors.push_back(actor);

    // Add a scalar bar.
    vtkNew<vtkScalarBarActor> scalarBar;
    scalarBar->SetLookupTable(ctf[i]);
    scalarBars.push_back(scalarBar);

    vtkNew<vtkTextMapper> textMapper;
    textMappers.push_back(textMapper);
    textMappers[i]->SetInput(titles[i].c_str());
    textMappers[i]->SetTextProperty(textProperty);

    vtkNew<vtkActor2D> textActor;
    textActors.push_back(textActor);
    textActors[i]->SetMapper(textMappers[i]);
    // Note: The position of an Actor2D is specified in display coordinates.
    textActors[i]->SetPosition(300, 16);

    vtkNew<vtkRenderer> ren;
    ren->SetBackground(colors->GetColor3d("ParaViewBkg").GetData());
    ren->AddActor(actors[i]);
    ren->AddActor(scalarBars[i]);
    ren->AddActor(textActors[i]);
    ren->SetViewport(xMins[i], yMins[i], xMaxs[i], yMaxs[i]);
    renderers.push_back(ren);

    renWin->AddRenderer(renderers[i]);
  }

  renWin->Render();
  iRen->Start();

  return EXIT_SUCCESS;
}

namespace {
vtkNew<vtkDiscretizableColorTransferFunction> GetCTF(bool const& modern)
{
  // name: Rainbow, creator: Andrew Maclean
  // interpolationspace: RGB, space: rgb
  // file name:

  vtkNew<vtkDiscretizableColorTransferFunction> ctf;

  ctf->SetColorSpaceToRGB();
  ctf->SetScaleToLinear();
  ctf->SetNanColor(0.5, 0.5, 0.5);
  ctf->SetBelowRangeColor(0.0, 0.0, 0.0);
  ctf->UseBelowRangeColorOn();
  ctf->SetAboveRangeColor(1.0, 1.0, 1.0);
  ctf->UseAboveRangeColorOn();

  if (modern)
  {
    ctf->AddRGBPoint(-1.0, 1.0, 0.0, 0.0);                 // Red
    ctf->AddRGBPoint(-2.0 / 3.0, 1.0, 128.0 / 255.0, 0.0); // Orange #ff8000
    ctf->AddRGBPoint(-1.0 / 3.0, 1.0, 1.0, 0.0);           // Yellow
    ctf->AddRGBPoint(0.0, 0.0, 1.0, 0.0);                  // Green  #00ff00
    ctf->AddRGBPoint(1.0 / 3.0, 0.0, 1.0, 1.0);            // Cyan
    ctf->AddRGBPoint(2.0 / 3.0, 0.0, 0.0, 1.0);            // Blue
    ctf->AddRGBPoint(1.0, 128.0 / 255.0, 0.0, 1.0);        // Violet #8000ff
  }
  else
  {
    ctf->AddRGBPoint(-1.0, 1.0, 0.0, 0.0);                 // Red
    ctf->AddRGBPoint(-2.0 / 3.0, 1.0, 165.0 / 255.0, 0.0); // Orange #00a500
    ctf->AddRGBPoint(-1.0 / 3.0, 1.0, 1.0, 0.0);           // Yellow
    ctf->AddRGBPoint(0.0, 0.0, 125.0 / 255.0, 0.0);        // Green  #008000
    ctf->AddRGBPoint(1.0 / 3.0, 0.0, 153.0 / 255.0, 1.0);  // Blue   #0099ff
    ctf->AddRGBPoint(2.0 / 3.0, 68.0 / 255.0, 0,
                     153.0 / 255.0);                // Indigo #4400ff
    ctf->AddRGBPoint(1.0, 153.0 / 255.0, 0.0, 1.0); // Violet #9900ff
  }

  ctf->SetNumberOfValues(7);
  ctf->DiscretizeOn();

  return ctf;
}

vtkNew<vtkDiscretizableColorTransferFunction>
GenerateNewCTF(vtkNew<vtkDiscretizableColorTransferFunction> const& oldCTF,
               std::vector<double> const& newX,
               std::vector<std::array<double, 3>> const& newRGB,
               bool const& reverse)
{
  vtkNew<vtkDiscretizableColorTransferFunction> newCTF;
  newCTF->SetScale(oldCTF->GetScale());
  newCTF->SetColorSpace(oldCTF->GetColorSpace());
  newCTF->SetNanColor(oldCTF->GetNanColor());
  if (!reverse)
  {
    newCTF->SetBelowRangeColor(oldCTF->GetBelowRangeColor());
    newCTF->SetUseBelowRangeColor(oldCTF->GetUseBelowRangeColor());
    newCTF->SetAboveRangeColor(oldCTF->GetAboveRangeColor());
    newCTF->SetUseAboveRangeColor(oldCTF->GetUseAboveRangeColor());
  }
  else
  {
    newCTF->SetBelowRangeColor(oldCTF->GetAboveRangeColor());
    newCTF->SetUseBelowRangeColor(oldCTF->GetUseAboveRangeColor());
    newCTF->SetAboveRangeColor(oldCTF->GetBelowRangeColor());
    newCTF->SetUseAboveRangeColor(oldCTF->GetUseBelowRangeColor());
  }
  newCTF->SetNumberOfValues(newX.size());
  newCTF->SetDiscretize(oldCTF->GetDiscretize());
  if (!reverse)
  {
    for (size_t i = 0; i < newX.size(); ++i)
    {
      newCTF->AddRGBPoint(newX[i], newRGB[i][0], newRGB[i][1], newRGB[i][2]);
    }
  }
  else
  {
    auto sz = newX.size();
    for (size_t i = 0; i < sz; i++)
    {
      auto j = sz - (i + 1);
      newCTF->AddRGBPoint(newX[i], newRGB[j][0], newRGB[j][1], newRGB[j][2]);
    }
  }
  newCTF->Build();
  return newCTF;
}

std::vector<double> Rescale(std::vector<double> const& values,
                            double const& newMin, double const& newMax)
{
  std::vector<double> res;
  double oldMin = *std::min_element(values.begin(), values.end());
  double oldMax = *std::max_element(values.begin(), values.end());
  for (size_t i = 0; i < values.size(); ++i)
  {
    double newV =
        (newMax - newMin) / (oldMax - oldMin) * (values[i] - oldMin) + newMin;
    // double newV1 =
    //     (newMax - newMin) / (oldMax - oldMin) * (values[i] - oldMax) +
    //     newMax;
    res.push_back(newV);
  }
  return res;
}

vtkNew<vtkDiscretizableColorTransferFunction>
RescaleCTF(vtkNew<vtkDiscretizableColorTransferFunction> const& ctf,
           double const& newMin, double const& newMax, bool const& reverse)
{
  double r0;
  double r1;

  if (newMin > newMax)
  {
    r0 = newMax;
    r1 = newMin;
  }
  else
  {
    r0 = newMin;
    r1 = newMax;
  }

  std::vector<double> xv;
  std::vector<std::array<double, 3>> rgbv;
  double nv[6] = {0, 0, 0, 0, 0, 0};
  for (auto i = 0; i < ctf->GetNumberOfValues(); ++i)
  {
    ctf->GetNodeValue(i, nv);
    double x = nv[0];
    std::array<double, 3> rgb;
    for (auto j = 1; j < 4; ++j)
    {
      rgb[j - 1] = nv[j];
    }
    xv.push_back(x);
    rgbv.push_back(rgb);
  }
  std::vector<double> xvr = Rescale(xv, r0, r1);

  return GenerateNewCTF(ctf, xvr, rgbv, reverse);
}

} // namespace
