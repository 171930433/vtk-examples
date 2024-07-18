#include <vtkActor.h>
#include <vtkActor2D.h>
#include <vtkCamera.h>
#include <vtkCellArray.h>
#include <vtkCubeSource.h>
#include <vtkDataSetMapper.h>
#include <vtkGlyph3DMapper.h>
#include <vtkLabeledDataMapper.h>
#include <vtkNamedColors.h>
#include <vtkNew.h>
#include <vtkPoints.h>
#include <vtkPolyDataMapper.h>
#include <vtkProperty.h>
#include <vtkProperty2D.h>
#include <vtkRenderWindow.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkRenderer.h>
#include <vtkSmartPointer.h>
#include <vtkSphereSource.h>
#include <vtkTextMapper.h>
#include <vtkTextProperty.h>
#include <vtkUnstructuredGrid.h>

#include <vtkHexagonalPrism.h>
#include <vtkHexahedron.h>
#include <vtkLine.h>
#include <vtkPentagonalPrism.h>
#include <vtkPixel.h>
#include <vtkPolyLine.h>
#include <vtkPolyVertex.h>
#include <vtkPolygon.h>
#include <vtkPyramid.h>
#include <vtkQuad.h>
#include <vtkTetra.h>
#include <vtkTriangle.h>
#include <vtkTriangleStrip.h>
#include <vtkVertex.h>
#include <vtkVoxel.h>
#include <vtkWedge.h>

#include <vtk_cli11.h>

#include <cstdlib>
#include <string>
#include <vector>

// These functions return an vtkUnstructured grid corresponding to the object.
namespace {

vtkNew<vtkUnstructuredGrid> MakeVertex();
vtkNew<vtkUnstructuredGrid> MakePolyVertex();
vtkNew<vtkUnstructuredGrid> MakeLine();
vtkNew<vtkUnstructuredGrid> MakePolyLine();
vtkNew<vtkUnstructuredGrid> MakeTriangle();
vtkNew<vtkUnstructuredGrid> MakeTriangleStrip();
vtkNew<vtkUnstructuredGrid> MakePolygon();
vtkNew<vtkUnstructuredGrid> MakePixel();
vtkNew<vtkUnstructuredGrid> MakeQuad();
vtkNew<vtkUnstructuredGrid> MakeTetra();
vtkNew<vtkUnstructuredGrid> MakeVoxel();
vtkNew<vtkUnstructuredGrid> MakeHexahedron();
vtkNew<vtkUnstructuredGrid> MakeWedge();
vtkNew<vtkUnstructuredGrid> MakePyramid();
vtkNew<vtkUnstructuredGrid> MakePentagonalPrism();
vtkNew<vtkUnstructuredGrid> MakeHexagonalPrism();

/**
 * Make a tile slightly larger or smaller than the bounds in the
 *   X and Z directions and thinner or thicker in the Y direction.
 *
 * A thickness_ratio of zero reduces the tile to an XZ plane.
 *
 * @param bounds - the bounds for the tile.
 * @param expansionFactor - the expansion factor in the XZ plane.
 * @param thicknessRatio - the thickness ratio in the Y direction, >= 0.
 * @return An actor corresponding to the tile.
 */
vtkNew<vtkActor> MakeTile(double* const& bounds,
                          double const& expansionFactor = 0.1,
                          double const& thicknessRatio = 0.05);

} // namespace

int main(int argc, char* argv[])
{
  CLI::App app{
      "Demonstrate the linear cell types found in VTK. "
      "The numbers define the ordering of the points making the cell."};

  // Define options
  std::string fileName;
  auto wireframeOn{false};
  app.add_flag("-w, --wireframe", wireframeOn, "Render a wireframe.");
  auto backfaceOn{false};
  app.add_flag("-b, --backface", backfaceOn,
               "Display the back face in a different colour.");
  CLI11_PARSE(app, argc, argv);
  if (wireframeOn && backfaceOn)
  {
    std::cerr << "error: argument -b/--backface: not allowed with argument "
                 "-w/--wireframe"
              << std::endl;
    return EXIT_FAILURE;
  }

  std::vector<vtkNew<vtkUnstructuredGrid>> uGrids;
  std::vector<std::string> titles;

  uGrids.push_back(MakeVertex());
  titles.push_back("VTK_VERTEX (=1)");
  uGrids.push_back(MakePolyVertex());
  titles.push_back("VTK_POLY_VERTEX (=2)");
  uGrids.push_back(MakeLine());
  titles.push_back("VTK_LINE (=3)");
  uGrids.push_back(MakePolyLine());
  titles.push_back("VTK_POLY_LINE (=4)");
  uGrids.push_back(MakeTriangle());
  titles.push_back("VTK_TRIANGLE (=5)");
  uGrids.push_back(MakeTriangleStrip());
  titles.push_back("VTK_TRIANGLE_STRIP (=6)");
  uGrids.push_back(MakePolygon());
  titles.push_back("VTK_POLYGON (=7)");
  uGrids.push_back(MakePixel());
  titles.push_back("VTK_PIXEL (=8)");
  uGrids.push_back(MakeQuad());
  titles.push_back("VTK_QUAD (=9)");
  uGrids.push_back(MakeTetra());
  titles.push_back("VTK_TETRA (=10)");
  uGrids.push_back(MakeVoxel());
  titles.push_back("VTK_VOXEL (=11)");
  uGrids.push_back(MakeHexahedron());
  titles.push_back("VTK_HEXAHEDRON (=12)");
  uGrids.push_back(MakeWedge());
  titles.push_back("VTK_WEDGE (=13)");
  uGrids.push_back(MakePyramid());
  titles.push_back("VTK_PYRAMID (=14)");
  uGrids.push_back(MakePentagonalPrism());
  titles.push_back("VTK_PENTAGONAL_PRISM (=15)");
  uGrids.push_back(MakeHexagonalPrism());
  titles.push_back("VTK_HEXAGONAL_PRISM (=16)");

  // std::vector<std::string> needsTile = {
  //     "VTK_TETRA (=10)",           "VTK_VOXEL (=11)",
  //     "VTK_HEXAHEDRON (=12)",      "VTK_WEDGE (=13)",
  //     "VTK_PYRAMID (=14)",         "VTK_PENTAGONAL_PRISM (=15)",
  //     "VTK_HEXAGONAL_PRISM (=16)",
  // };

  vtkNew<vtkNamedColors> colors;

  vtkNew<vtkRenderWindow> renWin;
  renWin->SetWindowName("LinearCellDemo");

  vtkNew<vtkRenderWindowInteractor> iRen;
  iRen->SetRenderWindow(renWin);

  // Create one sphere for all.
  vtkNew<vtkSphereSource> sphere;
  sphere->SetPhiResolution(21);
  sphere->SetThetaResolution(21);
  sphere->SetRadius(0.04);

  int rendererSize = 300;

  // Create one text property for all.
  vtkNew<vtkTextProperty> textProperty;
  textProperty->SetFontSize(int(rendererSize / 18));
  textProperty->BoldOn();
  textProperty->SetJustificationToCentered();
  textProperty->SetColor(colors->GetColor3d("Black").GetData());

  vtkNew<vtkTextProperty> labelProperty;
  labelProperty->SetFontSize(int(rendererSize / 12));
  labelProperty->BoldOn();
  labelProperty->SetJustificationToCentered();
  labelProperty->SetColor(colors->GetColor3d("FireBrick").GetData());

  vtkNew<vtkProperty> backProperty;
  backProperty->SetColor(colors->GetColor3d("Coral").GetData());

  std::vector<vtkSmartPointer<vtkRenderer>> renderers;

  // Create and link the mappers, actors and renderers together.
  for (unsigned int i = 0; i < uGrids.size(); ++i)
  {
    std::cout << "Creating: " << titles[i] << std::endl;

    vtkNew<vtkTextMapper> textMapper;
    textMapper->SetTextProperty(textProperty);
    textMapper->SetInput(titles[i].c_str());
    vtkNew<vtkActor2D> textActor;
    textActor->SetMapper(textMapper);
    textActor->SetPosition(rendererSize / 2.0, 8);

    vtkNew<vtkDataSetMapper> mapper;
    mapper->SetInputData(uGrids[i]);
    vtkNew<vtkActor> actor;
    actor->SetMapper(mapper);
    if (wireframeOn)
    {
      actor->GetProperty()->SetRepresentationToWireframe();
      actor->GetProperty()->SetLineWidth(2);
      actor->GetProperty()->SetOpacity(1);
      actor->GetProperty()->SetColor(colors->GetColor3d("Black").GetData());
    }
    else
    {
      actor->GetProperty()->EdgeVisibilityOn();
      actor->GetProperty()->SetLineWidth(3);
      actor->GetProperty()->SetColor(colors->GetColor3d("Snow").GetData());
      if (backfaceOn)
      {
        actor->GetProperty()->SetOpacity(0.4);
        actor->SetBackfaceProperty(backProperty);
        backProperty->SetOpacity(0.6);
      }
      else
      {
        actor->GetProperty()->SetOpacity(0.8);
      }
    }

    // Label the points.
    vtkNew<vtkLabeledDataMapper> labelMapper;
    labelMapper->SetInputData(uGrids[i]);
    labelMapper->SetLabelTextProperty(labelProperty);
    vtkNew<vtkActor2D> labelActor;
    labelActor->SetMapper(labelMapper);

    // Glyph the points.
    vtkNew<vtkGlyph3DMapper> pointMapper;
    pointMapper->SetInputData(uGrids[i]);
    pointMapper->SetSourceConnection(sphere->GetOutputPort());
    pointMapper->ScalingOff();
    pointMapper->ScalarVisibilityOff();

    vtkNew<vtkActor> pointActor;
    pointActor->SetMapper(pointMapper);
    pointActor->GetProperty()->SetColor(colors->GetColor3d("Yellow").GetData());
    pointActor->GetProperty()->SetSpecular(1.0);
    pointActor->GetProperty()->SetSpecularColor(
        colors->GetColor3d("White").GetData());
    pointActor->GetProperty()->SetSpecularPower(100);

    vtkNew<vtkRenderer> renderer;
    renderer->AddViewProp(textActor);
    renderer->AddViewProp(actor);
    renderer->AddViewProp(labelActor);
    renderer->AddViewProp(pointActor);
    // if (std::find(needsTile.cbegin(), needsTile.cend(), titles[i]) !=
    //     needsTile.cend())
    // {
    //   auto tileActor = MakeTile(uGrids[i]->GetBounds(), 0.1, 0.05);
    //   tileActor->GetProperty()->SetColor(
    //       colors->GetColor3d("SpringGreen").GetData());
    //   tileActor->GetProperty()->SetOpacity(0.3);
    //   renderer->AddViewProp(tileActor);
    // }

    renderers.push_back(renderer);

    renWin->AddRenderer(renderers[i]);
  }

  // Set up the viewports
  int gridRowDimensions = 4;
  int gridColumnDimensions = 4;

  renWin->SetSize(rendererSize * gridColumnDimensions,
                  rendererSize * gridRowDimensions);

  for (int row = 0; row < gridRowDimensions; row++)
  {
    for (int col = 0; col < gridColumnDimensions; col++)
    {
      int index = row * gridColumnDimensions + col;

      // Set the renderer's viewport dimensions (xmin, ymin, xmax, ymax)
      //  within the render window.
      // Note that for the Y values, we need to subtract the row index
      //  from grid rows because the viewport Y axis points upwards
      //  and we want to draw the grid from top to down.
      double viewport[4] = {
          static_cast<double>(col) / gridColumnDimensions,
          static_cast<double>(gridRowDimensions - row - 1) / gridRowDimensions,
          static_cast<double>(col + 1) / gridColumnDimensions,
          static_cast<double>(gridRowDimensions - row) / gridRowDimensions};
      // std::cout << viewport[0] << " " << viewport[1]
      //           << " " << viewport[2] << " "<< viewport[3] << std::endl;
      if (index > int(renderers.size()) - 1)
      {
        // Add a renderer even if there is no actor.
        // This makes the render window background all the same color.
        vtkNew<vtkRenderer> ren;
        ren->SetBackground(colors->GetColor3d("CornflowerBlue").GetData());
        ren->SetViewport(viewport);
        renWin->AddRenderer(ren);
        continue;
      }

      renderers[index]->SetBackground(
          colors->GetColor3d("CornflowerBlue").GetData());
      renderers[index]->SetViewport(viewport);
      renderers[index]->ResetCamera();
      switch (index)
      {
      case 0:
        // VTK_VERTEX (=1)
        renderers[index]->GetActiveCamera()->Azimuth(30);
        renderers[index]->GetActiveCamera()->Elevation(-30);
        renderers[index]->GetActiveCamera()->Dolly(0.1);
        break;
      case 1:
        // VTK_POLY_VERTEX (=2)
        renderers[index]->GetActiveCamera()->Azimuth(30);
        renderers[index]->GetActiveCamera()->Elevation(-30);
        renderers[index]->GetActiveCamera()->Dolly(0.8);
        break;
      case 2:
        // VTK_LINE (=3)
        renderers[index]->GetActiveCamera()->Azimuth(30);
        renderers[index]->GetActiveCamera()->Elevation(-30);
        renderers[index]->GetActiveCamera()->Dolly(0.4);
        break;
      case 3:
        // VTK_POLY_LINE (=4)
        renderers[index]->GetActiveCamera()->Azimuth(30);
        renderers[index]->GetActiveCamera()->Elevation(-30);
        renderers[index]->GetActiveCamera()->Dolly(1.0);
        break;
      case 4:
        // VTK_TRIANGLE (=5)
        renderers[index]->GetActiveCamera()->Azimuth(30);
        renderers[index]->GetActiveCamera()->Elevation(-30);
        renderers[index]->GetActiveCamera()->Dolly(0.7);
        break;
      case 5:
        // VTK_TRIANGLE_STRIP (=6)
        renderers[index]->GetActiveCamera()->Azimuth(30);
        renderers[index]->GetActiveCamera()->Elevation(-30);
        renderers[index]->GetActiveCamera()->Dolly(1.1);
        break;
      case 6:
        // VTK_POLYGON (=7)
        renderers[index]->GetActiveCamera()->Azimuth(0);
        renderers[index]->GetActiveCamera()->Elevation(-45);
        renderers[index]->GetActiveCamera()->Dolly(1.0);
        break;
      case 7:
        // VTK_PIXEL (=8)
        renderers[index]->GetActiveCamera()->Azimuth(0);
        renderers[index]->GetActiveCamera()->Elevation(-45);
        renderers[index]->GetActiveCamera()->Dolly(1.0);
        break;
      case 8:
        // VTK_QUAD (=9)
        renderers[index]->GetActiveCamera()->Azimuth(0);
        renderers[index]->GetActiveCamera()->Elevation(-45);
        renderers[index]->GetActiveCamera()->Dolly(1.0);
        break;
      case 9:
        // VTK_TETRA (=10)
        renderers[index]->GetActiveCamera()->Azimuth(0);
        renderers[index]->GetActiveCamera()->Elevation(-45);
        renderers[index]->GetActiveCamera()->Dolly(0.95);
        break;
      case 10:
        // VTK_VOXEL (=11)
        renderers[index]->GetActiveCamera()->Azimuth(-22.5);
        renderers[index]->GetActiveCamera()->Elevation(15);
        renderers[index]->GetActiveCamera()->Dolly(1.0);
        break;
      case 11:
        // VTK_HEXAHEDRON (=12)
        renderers[index]->GetActiveCamera()->Azimuth(-22.5);
        renderers[index]->GetActiveCamera()->Elevation(15);
        renderers[index]->GetActiveCamera()->Dolly(0.95);
        break;
      case 12:
        // VTK_WEDGE (=13)
        renderers[index]->GetActiveCamera()->Azimuth(-45);
        renderers[index]->GetActiveCamera()->Elevation(15);
        renderers[index]->GetActiveCamera()->Dolly(0.9);
        break;
      case 13:
        // VTK_PYRAMID (=14)
        renderers[index]->GetActiveCamera()->Azimuth(0);
        renderers[index]->GetActiveCamera()->Elevation(-30);
        renderers[index]->GetActiveCamera()->Dolly(1.0);
        break;
      // case 14:
      //   // VTK_PENTAGONAL_PRISM (=15)
      //   renderers[index]->GetActiveCamera()->Azimuth(-22.5);
      //   renderers[index]->GetActiveCamera()->Elevation(15);
      //   renderers[index]->GetActiveCamera()->Dolly(0.95);
      //   break;
      case 14:
        // VTK_PENTAGONAL_PRISM (=15)
        renderers[index]->GetActiveCamera()->Azimuth(-30);
        renderers[index]->GetActiveCamera()->Elevation(15);
        renderers[index]->GetActiveCamera()->Dolly(0.95);
        break;
      case 15:
        // VTK_HEXAGONAL_PRISM (=16)
        renderers[index]->GetActiveCamera()->Azimuth(-30);
        renderers[index]->GetActiveCamera()->Elevation(15);
        renderers[index]->GetActiveCamera()->Dolly(0.95);
        break;
      default:
        renderers[index]->GetActiveCamera()->Azimuth(0);
        renderers[index]->GetActiveCamera()->Elevation(0);
        renderers[index]->GetActiveCamera()->Dolly(1.0);
        break;
      }
      renderers[index]->ResetCameraClippingRange();
    }
  }

  iRen->Initialize();
  renWin->Render();
  iRen->Start();

  return EXIT_SUCCESS;
}

namespace {
vtkNew<vtkUnstructuredGrid> MakeVertex()
{
  // A vertex is a cell that represents a 3D point
  int numberOfVertices = 1;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);

  vtkNew<vtkVertex> vertex;
  for (int i = 0; i < numberOfVertices; ++i)
  {
    vertex->GetPointIds()->SetId(i, i);
  }
  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(points);
  ug->InsertNextCell(vertex->GetCellType(), vertex->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakePolyVertex()
{
  // A polyvertex is a cell represents a set of 0D vertices
  int numberOfVertices = 6;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(1, 0, 0);
  points->InsertNextPoint(0, 1, 0);
  points->InsertNextPoint(0, 0, 1);
  points->InsertNextPoint(1, 0, 0.4);
  points->InsertNextPoint(0, 1, 0.6);

  vtkNew<vtkPolyVertex> polyVertex;
  polyVertex->GetPointIds()->SetNumberOfIds(numberOfVertices);

  for (int i = 0; i < numberOfVertices; ++i)
  {
    polyVertex->GetPointIds()->SetId(i, i);
  }

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(points);
  ug->InsertNextCell(polyVertex->GetCellType(), polyVertex->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakeLine()
{
  // A line is a cell that represents a 1D point
  int numberOfVertices = 2;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(0.5, 0.5, 0);

  vtkNew<vtkLine> line;
  for (int i = 0; i < numberOfVertices; ++i)
  {
    line->GetPointIds()->SetId(i, i);
  }

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(points);
  ug->InsertNextCell(line->GetCellType(), line->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakePolyLine()
{
  // A polyline is a cell that represents a set of 1D lines
  int numberOfVertices = 5;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0.5, 0);
  points->InsertNextPoint(0.5, 0, 0);
  points->InsertNextPoint(1, 0.3, 0);
  points->InsertNextPoint(1.5, 0.4, 0);
  points->InsertNextPoint(2.0, 0.4, 0);

  vtkNew<vtkPolyLine> polyline;
  polyline->GetPointIds()->SetNumberOfIds(numberOfVertices);

  for (int i = 0; i < numberOfVertices; ++i)
  {
    polyline->GetPointIds()->SetId(i, i);
  }

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(points);
  ug->InsertNextCell(polyline->GetCellType(), polyline->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakeTriangle()
{
  // A triangle is a cell that represents a 1D point
  int numberOfVertices = 3;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(0.5, 0.5, 0);
  points->InsertNextPoint(0.2, 1, 0);

  vtkNew<vtkTriangle> triangle;
  for (int i = 0; i < numberOfVertices; ++i)
  {
    triangle->GetPointIds()->SetId(i, i);
  }

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(points);
  ug->InsertNextCell(triangle->GetCellType(), triangle->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakeTriangleStrip()
{
  // A triangle is a cell that represents a triangle strip
  int numberOfVertices = 10;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(1, -0.1, 0);
  points->InsertNextPoint(0.5, 1, 0);
  points->InsertNextPoint(2.0, -0.1, 0);
  points->InsertNextPoint(1.5, 0.8, 0);
  points->InsertNextPoint(3.0, 0, 0);
  points->InsertNextPoint(2.5, 0.9, 0);
  points->InsertNextPoint(4.0, -0.2, 0);
  points->InsertNextPoint(3.5, 0.8, 0);
  points->InsertNextPoint(4.5, 1.1, 0);

  vtkNew<vtkTriangleStrip> trianglestrip;
  trianglestrip->GetPointIds()->SetNumberOfIds(numberOfVertices);
  for (int i = 0; i < numberOfVertices; ++i)
  {
    trianglestrip->GetPointIds()->SetId(i, i);
  }

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(points);
  ug->InsertNextCell(trianglestrip->GetCellType(),
                     trianglestrip->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakePolygon()
{
  // A polygon is a cell that represents a polygon
  int numberOfVertices = 6;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(1, -0.1, 0);
  points->InsertNextPoint(0.8, 0.5, 0);
  points->InsertNextPoint(1, 1, 0);
  points->InsertNextPoint(0.6, 1.2, 0);
  points->InsertNextPoint(0, 0.8, 0);

  vtkNew<vtkPolygon> polygon;
  polygon->GetPointIds()->SetNumberOfIds(numberOfVertices);
  for (int i = 0; i < numberOfVertices; ++i)
  {
    polygon->GetPointIds()->SetId(i, i);
  }

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(points);
  ug->InsertNextCell(polygon->GetCellType(), polygon->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakePixel()

{
  // A pixel is a cell that represents a pixel
  vtkNew<vtkPixel> pixel;
  pixel->GetPoints()->SetPoint(0, 0, 0, 0);
  pixel->GetPoints()->SetPoint(1, 1, 0, 0);
  pixel->GetPoints()->SetPoint(2, 0, 1, 0);
  pixel->GetPoints()->SetPoint(3, 1, 1, 0);

  pixel->GetPointIds()->SetId(0, 0);
  pixel->GetPointIds()->SetId(1, 1);
  pixel->GetPointIds()->SetId(2, 2);
  pixel->GetPointIds()->SetId(3, 3);

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(pixel->GetPoints());
  ug->InsertNextCell(pixel->GetCellType(), pixel->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakeQuad()

{
  // A quad is a cell that represents a quad
  vtkNew<vtkQuad> quad;
  quad->GetPoints()->SetPoint(0, 0, 0, 0);
  quad->GetPoints()->SetPoint(1, 1, 0, 0);
  quad->GetPoints()->SetPoint(2, 1, 1, 0);
  quad->GetPoints()->SetPoint(3, 0, 1, 0);

  quad->GetPointIds()->SetId(0, 0);
  quad->GetPointIds()->SetId(1, 1);
  quad->GetPointIds()->SetId(2, 2);
  quad->GetPointIds()->SetId(3, 3);

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(quad->GetPoints());
  ug->InsertNextCell(quad->GetCellType(), quad->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakeTetra()
{
  // Make a tetrahedron.
  int numberOfVertices = 4;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(1, 0, 0);
  points->InsertNextPoint(1, 1, 0);
  points->InsertNextPoint(0, 1, 1);

  vtkNew<vtkTetra> tetra;
  for (int i = 0; i < numberOfVertices; ++i)
  {
    tetra->GetPointIds()->SetId(i, i);
  }

  vtkNew<vtkCellArray> cellArray;
  cellArray->InsertNextCell(tetra);

  vtkNew<vtkUnstructuredGrid> unstructuredGrid;
  unstructuredGrid->SetPoints(points);
  unstructuredGrid->SetCells(VTK_TETRA, cellArray);

  return unstructuredGrid;
}

vtkNew<vtkUnstructuredGrid> MakeVoxel()
{
  // A voxel is a representation of a regular grid in 3-D space.
  int numberOfVertices = 8;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(1, 0, 0);
  points->InsertNextPoint(0, 1, 0);
  points->InsertNextPoint(1, 1, 0);
  points->InsertNextPoint(0, 0, 1);
  points->InsertNextPoint(1, 0, 1);
  points->InsertNextPoint(0, 1, 1);
  points->InsertNextPoint(1, 1, 1);

  vtkNew<vtkVoxel> voxel;
  for (int i = 0; i < numberOfVertices; ++i)
  {
    voxel->GetPointIds()->SetId(i, i);
  }

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(points);
  ug->InsertNextCell(voxel->GetCellType(), voxel->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakeHexahedron()
{
  // A regular hexagon (cube) with all faces square and three squares around
  // each vertex is created below.

  // Set up the coordinates of eight points
  // (the two faces must be in counter-clockwise
  // order as viewed from the outside).

  int numberOfVertices = 8;

  // Create the points
  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0.0, 0.0, 0.0);
  points->InsertNextPoint(1.0, 0.0, 0.0);
  points->InsertNextPoint(1.0, 1.0, 0.0);
  points->InsertNextPoint(0.0, 1.0, 0.0);
  points->InsertNextPoint(0.0, 0.0, 1.0);
  points->InsertNextPoint(1.0, 0.0, 1.0);
  points->InsertNextPoint(1.0, 1.0, 1.0);
  points->InsertNextPoint(0.0, 1.0, 1.0);

  // Create a hexahedron from the points
  vtkNew<vtkHexahedron> hex;
  for (int i = 0; i < numberOfVertices; ++i)
  {
    hex->GetPointIds()->SetId(i, i);
  }

  // Add the points and hexahedron to an unstructured grid
  vtkNew<vtkUnstructuredGrid> uGrid;
  uGrid->SetPoints(points);
  uGrid->InsertNextCell(hex->GetCellType(), hex->GetPointIds());

  return uGrid;
}

vtkNew<vtkUnstructuredGrid> MakeWedge()
{

  // A wedge consists of two triangular ends and three rectangular faces.

  int numberOfVertices = 6;

  vtkNew<vtkPoints> points;

  points->InsertNextPoint(0, 1, 0);
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(0, 0.5, 0.5);
  points->InsertNextPoint(1, 1, 0);
  points->InsertNextPoint(1, 0.0, 0.0);
  points->InsertNextPoint(1, 0.5, 0.5);

  vtkNew<vtkWedge> wedge;
  for (int i = 0; i < numberOfVertices; ++i)
  {
    wedge->GetPointIds()->SetId(i, i);
  }

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(points);
  ug->InsertNextCell(wedge->GetCellType(), wedge->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakePyramid()
{
  // Make a regular square pyramid.
  int numberOfVertices = 5;

  vtkNew<vtkPoints> points;

  float p0[3] = {1.0, 1.0, 0.0};
  float p1[3] = {-1.0, 1.0, 0.0};
  float p2[3] = {-1.0, -1.0, 0.0};
  float p3[3] = {1.0, -1.0, 0.0};
  float p4[3] = {0.0, 0.0, 1.0};

  points->InsertNextPoint(p0);
  points->InsertNextPoint(p1);
  points->InsertNextPoint(p2);
  points->InsertNextPoint(p3);
  points->InsertNextPoint(p4);

  vtkNew<vtkPyramid> pyramid;
  for (int i = 0; i < numberOfVertices; ++i)
  {
    pyramid->GetPointIds()->SetId(i, i);
  }

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(points);
  ug->InsertNextCell(pyramid->GetCellType(), pyramid->GetPointIds());

  return ug;
}
vtkNew<vtkUnstructuredGrid> MakePentagonalPrism()
{
  vtkNew<vtkPentagonalPrism> pentagonalPrism;

  pentagonalPrism->GetPointIds()->SetId(0, 0);
  pentagonalPrism->GetPointIds()->SetId(1, 1);
  pentagonalPrism->GetPointIds()->SetId(2, 2);
  pentagonalPrism->GetPointIds()->SetId(3, 3);
  pentagonalPrism->GetPointIds()->SetId(4, 4);
  pentagonalPrism->GetPointIds()->SetId(5, 5);
  pentagonalPrism->GetPointIds()->SetId(6, 6);
  pentagonalPrism->GetPointIds()->SetId(7, 7);
  pentagonalPrism->GetPointIds()->SetId(8, 8);
  pentagonalPrism->GetPointIds()->SetId(9, 9);

  double scale = 2.0;
  pentagonalPrism->GetPoints()->SetPoint(0, 11 / scale, 10 / scale, 10 / scale);
  pentagonalPrism->GetPoints()->SetPoint(1, 13 / scale, 10 / scale, 10 / scale);
  pentagonalPrism->GetPoints()->SetPoint(2, 14 / scale, 12 / scale, 10 / scale);
  pentagonalPrism->GetPoints()->SetPoint(3, 12 / scale, 14 / scale, 10 / scale);
  pentagonalPrism->GetPoints()->SetPoint(4, 10 / scale, 12 / scale, 10 / scale);
  pentagonalPrism->GetPoints()->SetPoint(5, 11 / scale, 10 / scale, 14 / scale);
  pentagonalPrism->GetPoints()->SetPoint(6, 13 / scale, 10 / scale, 14 / scale);
  pentagonalPrism->GetPoints()->SetPoint(7, 14 / scale, 12 / scale, 14 / scale);
  pentagonalPrism->GetPoints()->SetPoint(8, 12 / scale, 14 / scale, 14 / scale);
  pentagonalPrism->GetPoints()->SetPoint(9, 10 / scale, 12 / scale, 14 / scale);

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(pentagonalPrism->GetPoints());
  ug->InsertNextCell(pentagonalPrism->GetCellType(),
                     pentagonalPrism->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakeHexagonalPrism()
{
  vtkNew<vtkHexagonalPrism> hexagonalPrism;
  hexagonalPrism->GetPointIds()->SetId(0, 0);
  hexagonalPrism->GetPointIds()->SetId(1, 1);
  hexagonalPrism->GetPointIds()->SetId(2, 2);
  hexagonalPrism->GetPointIds()->SetId(3, 3);
  hexagonalPrism->GetPointIds()->SetId(4, 4);
  hexagonalPrism->GetPointIds()->SetId(5, 5);
  hexagonalPrism->GetPointIds()->SetId(6, 6);
  hexagonalPrism->GetPointIds()->SetId(7, 7);
  hexagonalPrism->GetPointIds()->SetId(8, 8);
  hexagonalPrism->GetPointIds()->SetId(9, 9);
  hexagonalPrism->GetPointIds()->SetId(10, 10);
  hexagonalPrism->GetPointIds()->SetId(11, 11);

  double scale = 2.0;
  hexagonalPrism->GetPoints()->SetPoint(0, 11 / scale, 10 / scale, 10 / scale);
  hexagonalPrism->GetPoints()->SetPoint(1, 13 / scale, 10 / scale, 10 / scale);
  hexagonalPrism->GetPoints()->SetPoint(2, 14 / scale, 12 / scale, 10 / scale);
  hexagonalPrism->GetPoints()->SetPoint(3, 13 / scale, 14 / scale, 10 / scale);
  hexagonalPrism->GetPoints()->SetPoint(4, 11 / scale, 14 / scale, 10 / scale);
  hexagonalPrism->GetPoints()->SetPoint(5, 10 / scale, 12 / scale, 10 / scale);
  hexagonalPrism->GetPoints()->SetPoint(6, 11 / scale, 10 / scale, 14 / scale);
  hexagonalPrism->GetPoints()->SetPoint(7, 13 / scale, 10 / scale, 14 / scale);
  hexagonalPrism->GetPoints()->SetPoint(8, 14 / scale, 12 / scale, 14 / scale);
  hexagonalPrism->GetPoints()->SetPoint(9, 13 / scale, 14 / scale, 14 / scale);
  hexagonalPrism->GetPoints()->SetPoint(10, 11 / scale, 14 / scale, 14 / scale);
  hexagonalPrism->GetPoints()->SetPoint(11, 10 / scale, 12 / scale, 14 / scale);

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(hexagonalPrism->GetPoints());
  ug->InsertNextCell(hexagonalPrism->GetCellType(),
                     hexagonalPrism->GetPointIds());

  return ug;
}

/**
 * Make a tile slightly larger or smaller than the bounds in the
 *   X and Z directions and thinner or thicker in the Y direction.
 *
 * A thickness_ratio of zero reduces the tile to an XZ plane.
 *
 * @param bounds - the bounds for the tile.
 * @param expansionFactor - the expansion factor in the XZ plane.
 * @param thicknessRatio - the thickness ratio in the Y direction, >= 0.
 * @return An actor corresponding to the tile.
 */
vtkNew<vtkActor> MakeTile(double* const& bounds, double const& expansionFactor,
                          double const& thicknessRatio)
{
  std::vector<double> d_xyz = {bounds[1] - bounds[0], bounds[3] - bounds[2],
                               bounds[5] - bounds[4]};
  auto thickness = d_xyz[2] * std::abs(thicknessRatio);
  std::vector<double> center = {(bounds[1] + bounds[0]) / 2.0,
                                bounds[2] - thickness / 2.0,
                                (bounds[5] + bounds[4]) / 2.0};
  auto x_length = bounds[1] - bounds[0] + (d_xyz[0] * expansionFactor);
  auto z_length = bounds[5] - bounds[4] + (d_xyz[2] * expansionFactor);

  vtkNew<vtkCubeSource> plane;
  plane->SetCenter(center[0], center[1], center[2]);
  plane->SetXLength(x_length);
  plane->SetYLength(thickness);
  plane->SetZLength(z_length);

  vtkNew<vtkPolyDataMapper> planeMapper;
  planeMapper->SetInputConnection(plane->GetOutputPort());

  vtkNew<vtkActor> planeActor;
  planeActor->SetMapper(planeMapper);

  return planeActor;
}
} // namespace
