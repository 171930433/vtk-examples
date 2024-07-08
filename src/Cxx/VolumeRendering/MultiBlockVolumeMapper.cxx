#include <vtkColorSeries.h>
#include <vtkImageData.h>
#include <vtkMultiBlockDataSet.h>
#include <vtkMultiBlockVolumeMapper.h>
#include <vtkNamedColors.h>
#include <vtkNew.h>
#include <vtkRenderWindow.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkRenderer.h>
#include <vtkVolumeProperty.h>

int main(int argc, char* argv[])
{
  // set up vtkMultiBlockDataSet (just a bunch of colored blocks):
  const int dim[3] = {10, 10, 10};
  double spc[3] = {0.1, 0.1, 0.1};
  vtkNew<vtkMultiBlockDataSet> mb;
  vtkNew<vtkColorSeries> colors;
  colors->SetColorScheme(vtkColorSeries::BREWER_QUALITATIVE_SET3);
  for (int i=0; i<8; ++i)
  {
    vtkNew<vtkImageData> img;
    img->SetDimensions(dim);
    img->AllocateScalars(VTK_UNSIGNED_CHAR, 4);
    img->SetSpacing(spc);

    // position the volumes by their origin:
    // shift object by the length of a volume in the axis directions so as to make them non-overlapping:
    std::array<int, 3> ofs{ i % 2, (i / 2) % 2,  i / 4 };
    img->SetOrigin(
        ofs[0] * (dim[0]-1) * spc[0],
        ofs[1] * (dim[1]-1) * spc[1],
        ofs[2] * (dim[2]-1) * spc[2]
    );

    // set colors:
    auto col = colors->GetColor(i);
    for (int x = 0; x < dim[0]; ++x)
    {
      for (int y = 0; y < dim[1]; ++y)
      {
        for (int z = 0; z < dim[2]; ++z)
        {
          for (int c = 0; c < 3; ++c)
          {
            img->SetScalarComponentFromDouble(x, y, z, c, col[c]);
          }
          img->SetScalarComponentFromDouble(x, y, z, 3, 255);
        }
      }
    }
    mb->SetBlock(i, img);
  }

  // setting up the vtkMultiBlockVolumeMapper:
  vtkNew<vtkMultiBlockVolumeMapper> volMapper;
  volMapper->SetInputDataObject(mb);
  vtkNew<vtkVolume> volume;
  vtkNew<vtkVolumeProperty> volProp;
  volProp->SetIndependentComponents(false);
  volume->SetMapper(volMapper);
  volume->SetProperty(volProp);
  volume->SetVisibility(true);

  // standard render window and renderer setup:
  vtkNew<vtkRenderer> renderer;
  vtkNew<vtkNamedColors> namedColors;
  renderer->SetBackground(namedColors->GetColor3d("ForestGreen").GetData());
  renderer->AddVolume(volume);
  vtkNew<vtkRenderWindow> renWin;
  renWin->AddRenderer(renderer);
  renWin->Render();
  vtkNew<vtkRenderWindowInteractor> iren;
  iren->SetRenderWindow(renWin);
  iren->Start();

  return EXIT_SUCCESS;
}
