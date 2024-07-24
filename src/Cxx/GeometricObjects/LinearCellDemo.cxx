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
#include <vtk_fmt.h>
// clang-format off
#include VTK_FMT(fmt/format.h)
// clang-format on

#include <cstdlib>
#include <string>
#include <vector>

using cellPair =
    std::pair<vtkSmartPointer<vtkUnstructuredGrid>, std::array<double, 3>>;
using cellMap = std::map<std::string, cellPair>;

namespace {

/**
 * Make a map consisting of the unstructured grid name,
 *  the unstructured grid and it's orientation as
 *  Azimuth, Elevation and Zoom in degrees.
 *
 * @return The map.
 */
cellMap GetUnstructuredGrids();

// These functions return an vtkUnstructured grid corresponding to the object.
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
  auto plinthOff{false};
  app.add_flag("-n, --noPlinth", plinthOff, "Remove the plinth.");
  CLI11_PARSE(app, argc, argv);
  if (wireframeOn && backfaceOn)
  {
    std::cerr << "error: argument -b/--backface: not allowed with argument "
                 "-w/--wireframe"
              << std::endl;
    return EXIT_FAILURE;
  }

  vtkNew<vtkNamedColors> colors;

  // Create one sphere for all.
  vtkNew<vtkSphereSource> sphere;
  sphere->SetPhiResolution(21);
  sphere->SetThetaResolution(21);
  sphere->SetRadius(0.04);

  auto cells = GetUnstructuredGrids();

  // clang-format off
  std::array<std::string, 16> keys = {
      "VTK_VERTEX (=1)",            "VTK_POLY_VERTEX (=2)",
      "VTK_LINE (=3)",              "VTK_POLY_LINE (=4)",
      "VTK_TRIANGLE (=5)",          "VTK_TRIANGLE_STRIP (=6)",
      "VTK_POLYGON (=7)",           "VTK_PIXEL (=8)",
      "VTK_QUAD (=9)",              "VTK_TETRA (=10)",
      "VTK_VOXEL (=11)",            "VTK_HEXAHEDRON (=12)",
      "VTK_WEDGE (=13)",            "VTK_PYRAMID (=14)",
      "VTK_PENTAGONAL_PRISM (=15)", "VTK_HEXAGONAL_PRISM (=16)"};
  // clang-format on

  std::vector<std::string> addPlinth = {
      "VTK_TETRA (=10)",           "VTK_VOXEL (=11)",
      "VTK_HEXAHEDRON (=12)",      "VTK_WEDGE (=13)",
      "VTK_PYRAMID (=14)",         "VTK_PENTAGONAL_PRISM (=15)",
      "VTK_HEXAGONAL_PRISM (=16)",
  };
  std::vector<std::string> lines{"VTK_LINE (=3)", "VTK_POLY_LINE (=4)"};

  // Set up the viewports.
  auto gridRowDimensions = 4;
  auto gridColumnDimensions = 4;
  auto rendererSize = 300;
  std::array<int, 2> windowSize{gridColumnDimensions * rendererSize,
                                gridRowDimensions * rendererSize};

  auto blank = cells.size();
  std::vector<std::string> blankViewports;

  std::map<std::string, std::array<double, 4>> viewports;
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
      std::array<double, 4> viewport{
          static_cast<double>(col) / gridColumnDimensions,
          static_cast<double>(gridRowDimensions - row - 1) / gridRowDimensions,
          static_cast<double>(col + 1) / gridColumnDimensions,
          static_cast<double>(gridRowDimensions - row) / gridRowDimensions};
      // std::cout << viewport[0] << " " << viewport[1]
      //           << " " << viewport[2] << " "<< viewport[3] << std::endl;
      if (index < blank)
      {
        viewports[keys[index]] = viewport;
      }
      else
      {
        auto s = fmt::format("vp_{:d}_{:d}", col, row);
        viewports[s] = viewport;
        blankViewports.push_back(s);
      }
    }
  }

  // Create one text property for all.
  vtkNew<vtkTextProperty> textProperty;
  textProperty->SetFontSize(int(rendererSize / 18));
  textProperty->BoldOn();
  textProperty->SetJustificationToCentered();
  textProperty->SetColor(colors->GetColor3d("Black").GetData());

  vtkNew<vtkTextProperty> labelProperty;
  labelProperty->SetFontSize(int(rendererSize / 12));
  labelProperty->BoldOn();
  labelProperty->ShadowOn();
  labelProperty->SetJustificationToCentered();
  labelProperty->SetColor(colors->GetColor3d("DeepPink").GetData());

  vtkNew<vtkProperty> backProperty;
  backProperty->SetColor(colors->GetColor3d("DodgerBlue").GetData());

  std::map<std::string, vtkSmartPointer<vtkRenderer>> renderers;

  vtkNew<vtkRenderWindow> renWin;
  renWin->SetWindowName("LinearCellDemo");
  renWin->SetSize(windowSize.data());

  vtkNew<vtkRenderWindowInteractor> iRen;
  iRen->SetRenderWindow(renWin);

  // Create and link the mappers, actors and renderers together.
  for (const auto& key : keys)
  {
    std::cout << "Creating: " << key << std::endl;

    vtkNew<vtkTextMapper> textMapper;
    textMapper->SetTextProperty(textProperty);
    textMapper->SetInput(key.c_str());
    vtkNew<vtkActor2D> textActor;
    textActor->SetMapper(textMapper);
    textActor->SetPosition(rendererSize / 2.0, 8);

    vtkNew<vtkDataSetMapper> mapper;
    mapper->SetInputData(cells[key].first);
    vtkNew<vtkActor> actor;
    actor->SetMapper(mapper);
    if (wireframeOn ||
        std::find(lines.cbegin(), lines.cend(), key) != lines.cend())
    {
      std::cout << "wireframe on" << std::endl;
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
    labelMapper->SetInputData(cells[key].first);
    labelMapper->SetLabelTextProperty(labelProperty);
    vtkNew<vtkActor2D> labelActor;
    labelActor->SetMapper(labelMapper);

    // Glyph the points.
    vtkNew<vtkGlyph3DMapper> pointMapper;
    pointMapper->SetInputData(cells[key].first);
    pointMapper->SetSourceConnection(sphere->GetOutputPort());
    pointMapper->ScalingOff();
    pointMapper->ScalarVisibilityOff();

    vtkNew<vtkActor> pointActor;
    pointActor->SetMapper(pointMapper);
    pointActor->GetProperty()->SetColor(colors->GetColor3d("Gold").GetData());

    vtkNew<vtkRenderer> renderer;
    renderer->SetBackground(colors->GetColor3d("LightSteelBlue").GetData());
    renderer->SetViewport(viewports[key].data());

    renderer->AddViewProp(textActor);
    renderer->AddViewProp(actor);
    renderer->AddViewProp(labelActor);
    renderer->AddViewProp(pointActor);
    if (!plinthOff)
    {
      if (std::find(addPlinth.cbegin(), addPlinth.cend(), key) !=
          addPlinth.cend())
      {
        auto tileActor = MakeTile(cells[key].first->GetBounds(), 0.5, 0.05);
        tileActor->GetProperty()->SetColor(
            colors->GetColor3d("Lavender").GetData());
        tileActor->GetProperty()->SetOpacity(0.3);
        renderer->AddViewProp(tileActor);
      }
    }

    renderer->ResetCamera();
    renderer->GetActiveCamera()->Azimuth(cells[key].second[0]);
    renderer->GetActiveCamera()->Elevation(cells[key].second[1]);
    renderer->GetActiveCamera()->Dolly(cells[key].second[2]);
    renderer->ResetCameraClippingRange();

    renWin->AddRenderer(renderer);
    renderers[key] = renderer;
  }

  for (const auto& key : blankViewports)
  {
    vtkNew<vtkRenderer> renderer;
    renderer->SetBackground(colors->GetColor3d("LightSteelBlue").GetData());
    renderer->SetViewport(viewports[key].data());
    renWin->AddRenderer(renderer);
    renderers[key] = renderer;
  }

  iRen->Initialize();
  renWin->Render();
  iRen->Start();

  return EXIT_SUCCESS;
}

namespace {

cellMap GetUnstructuredGrids()
{
  cellMap cells;

  cells["VTK_VERTEX (=1)"] = cellPair(MakeVertex(), {30, -30, 0.1});
  cells["VTK_POLY_VERTEX (=2)"] = cellPair(MakePolyVertex(), {30, -30, 0.8});
  cells["VTK_LINE (=3)"] = cellPair(MakeLine(), {30, -30, 0.4});
  cells["VTK_POLY_LINE (=4)"] = cellPair(MakePolyLine(), {30, -30, 1.0});
  cells["VTK_TRIANGLE (=5)"] = cellPair(MakeTriangle(), {30, -30, 0.7});
  cells["VTK_TRIANGLE_STRIP (=6)"] =
      cellPair(MakeTriangleStrip(), {30, -30, 1.1});
  cells["VTK_POLYGON (=7)"] = cellPair(MakePolygon(), {0, -45, 1.0});
  cells["VTK_PIXEL (=8)"] = cellPair(MakePixel(), {0, -45, 1.0});
  cells["VTK_QUAD (=9)"] = cellPair(MakeQuad(), {0, -45, 1.0});
  cells["VTK_TETRA (=10)"] = cellPair(MakeTetra(), {20, 20, 1.0});
  cells["VTK_VOXEL (=11)"] = cellPair(MakeVoxel(), {-22.5, 15, 0.95});
  cells["VTK_HEXAHEDRON (=12)"] = cellPair(MakeHexahedron(), {-22.5, 15, 0.95});
  cells["VTK_WEDGE (=13)"] = cellPair(MakeWedge(), {-30, 15, 1.0});
  cells["VTK_PYRAMID (=14)"] = cellPair(MakePyramid(), {-60, 15, 1.0});
  cells["VTK_PENTAGONAL_PRISM (=15)"] =
      cellPair(MakePentagonalPrism(), {-60, 10, 1.0});
  cells["VTK_HEXAGONAL_PRISM (=16)"] =
      cellPair(MakeHexagonalPrism(), {-60, 15, 1.0});

  return cells;
}

vtkNew<vtkUnstructuredGrid> MakeVertex()
{
  // A vertex is a cell that represents a 3D point.
  auto numberOfVertices = 1;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);

  vtkNew<vtkVertex> vertex;
  for (auto i = 0; i < numberOfVertices; ++i)
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
  // A polyvertex is a cell that represents a set of 0D vertices.
  auto numberOfVertices = 6;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(1, 0, 0);
  points->InsertNextPoint(0, 1, 0);
  points->InsertNextPoint(0, 0, 1);
  points->InsertNextPoint(1, 0, 0.4);
  points->InsertNextPoint(0, 1, 0.6);

  vtkNew<vtkPolyVertex> polyVertex;
  polyVertex->GetPointIds()->SetNumberOfIds(numberOfVertices);

  for (auto i = 0; i < numberOfVertices; ++i)
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
  // A line is a cell that represents a 1D point.
  auto numberOfVertices = 2;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(0.5, 0.5, 0);

  vtkNew<vtkLine> line;
  for (auto i = 0; i < numberOfVertices; ++i)
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
  // A polyline is a cell that represents a set of 1D lines.
  auto numberOfVertices = 5;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0.5, 0);
  points->InsertNextPoint(0.5, 0, 0);
  points->InsertNextPoint(1, 0.3, 0);
  points->InsertNextPoint(1.5, 0.4, 0);
  points->InsertNextPoint(2.0, 0.4, 0);

  vtkNew<vtkPolyLine> polyline;
  polyline->GetPointIds()->SetNumberOfIds(numberOfVertices);

  for (auto i = 0; i < numberOfVertices; ++i)
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
  // A triangle is a cell that represents a triangle.
  auto numberOfVertices = 3;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(0.5, 0.5, 0);
  points->InsertNextPoint(0.2, 1, 0);

  vtkNew<vtkTriangle> triangle;
  for (auto i = 0; i < numberOfVertices; ++i)
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
  // A triangle is a cell that represents a triangle strip.
  auto numberOfVertices = 10;

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
  for (auto i = 0; i < numberOfVertices; ++i)
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
  // A polygon is a cell that represents a polygon.
  auto numberOfVertices = 6;

  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(1, -0.1, 0);
  points->InsertNextPoint(0.8, 0.5, 0);
  points->InsertNextPoint(1, 1, 0);
  points->InsertNextPoint(0.6, 1.2, 0);
  points->InsertNextPoint(0, 0.8, 0);

  vtkNew<vtkPolygon> polygon;
  polygon->GetPointIds()->SetNumberOfIds(numberOfVertices);
  for (auto i = 0; i < numberOfVertices; ++i)
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
  // A pixel is a cell that represents a pixel.
  auto numberOfVertices = 4;

  vtkNew<vtkPixel> pixel;
  pixel->GetPoints()->SetPoint(0, 0, 0, 0);
  pixel->GetPoints()->SetPoint(1, 1, 0, 0);
  pixel->GetPoints()->SetPoint(2, 0, 1, 0);
  pixel->GetPoints()->SetPoint(3, 1, 1, 0);

  for (auto i = 0; i < numberOfVertices; ++i)
  {
    pixel->GetPointIds()->SetId(i, i);
  }

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(pixel->GetPoints());
  ug->InsertNextCell(pixel->GetCellType(), pixel->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakeQuad()

{
  // A quad is a cell that represents a quad.
  auto numberOfVertices = 4;

  vtkNew<vtkQuad> quad;
  quad->GetPoints()->SetPoint(0, 0, 0, 0);
  quad->GetPoints()->SetPoint(1, 1, 0, 0);
  quad->GetPoints()->SetPoint(2, 1, 1, 0);
  quad->GetPoints()->SetPoint(3, 0, 1, 0);

  for (auto i = 0; i < numberOfVertices; ++i)
  {
    quad->GetPointIds()->SetId(i, i);
  }

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(quad->GetPoints());
  ug->InsertNextCell(quad->GetCellType(), quad->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakeTetra()
{
  // Make a tetrahedron.
  auto numberOfVertices = 4;

  // vtkNew<vtkPoints> points;
  // points->InsertNextPoint(0, 0, 0);
  // points->InsertNextPoint(1, 0, 0);
  // points->InsertNextPoint(1, 1, 0);
  // points->InsertNextPoint(0, 1, 1);

  // Rotate the above points -90° about the X-axis.
  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(1, 0, 0);
  points->InsertNextPoint(1, 0, -1);
  points->InsertNextPoint(0, 1, -1);

  vtkNew<vtkTetra> tetra;
  for (auto i = 0; i < numberOfVertices; ++i)
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
  auto numberOfVertices = 8;

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
  for (auto i = 0; i < numberOfVertices; ++i)
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

  auto numberOfVertices = 8;

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
  for (auto i = 0; i < numberOfVertices; ++i)
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

  auto numberOfVertices = 6;

  // vtkNew<vtkPoints> points;
  // points->InsertNextPoint(0, 1, 0);
  // points->InsertNextPoint(0, 0, 0);
  // points->InsertNextPoint(0, 0.5, 0.5);
  // points->InsertNextPoint(1, 1, 0);
  // points->InsertNextPoint(1, 0.0, 0.0);
  // points->InsertNextPoint(1, 0.5, 0.5);

  // Rotate the above points -90° about the X-axis
  //  and translate -1 along the Y-axis.
  vtkNew<vtkPoints> points;
  points->InsertNextPoint(0, 0, 0);
  points->InsertNextPoint(0, 0, 1);
  points->InsertNextPoint(0, 0.5, 0.5);
  points->InsertNextPoint(1, 0, 0);
  points->InsertNextPoint(1, 0, 1);
  points->InsertNextPoint(1, 0.5, 0.5);

  vtkNew<vtkWedge> wedge;
  for (auto i = 0; i < numberOfVertices; ++i)
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
  auto numberOfVertices = 5;

  vtkNew<vtkPoints> points;

  // float p0[3] = {1.0, 1.0, 0.0};
  // float p1[3] = {-1.0, 1.0, 0.0};
  // float p2[3] = {-1.0, -1.0, 0.0};
  // float p3[3] = {1.0, -1.0, 0.0};
  // float p4[3] = {0.0, 0.0, 1.0};

  // Rotate the above points -90° about the X-axis.
  float p0[3] = {1.0, 0.0, -1.0};
  float p1[3] = {-1.0, 0.0, -1.0};
  float p2[3] = {-1.0, 0.0, 1.0};
  float p3[3] = {1.0, 0.0, 1.0};
  float p4[3] = {0.0, 2.0, 0.0};

  points->InsertNextPoint(p0);
  points->InsertNextPoint(p1);
  points->InsertNextPoint(p2);
  points->InsertNextPoint(p3);
  points->InsertNextPoint(p4);

  vtkNew<vtkPyramid> pyramid;
  for (auto i = 0; i < numberOfVertices; ++i)
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
  auto numberOfVertices = 10;

  vtkNew<vtkPentagonalPrism> pentagonalPrism;

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

  for (auto i = 0; i < numberOfVertices; ++i)
  {
    pentagonalPrism->GetPointIds()->SetId(i, i);
  }

  vtkNew<vtkUnstructuredGrid> ug;
  ug->SetPoints(pentagonalPrism->GetPoints());
  ug->InsertNextCell(pentagonalPrism->GetCellType(),
                     pentagonalPrism->GetPointIds());

  return ug;
}

vtkNew<vtkUnstructuredGrid> MakeHexagonalPrism()
{
  auto numberOfVertices = 12;

  vtkNew<vtkHexagonalPrism> hexagonalPrism;

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

  for (auto i = 0; i < numberOfVertices; ++i)
  {
    hexagonalPrism->GetPointIds()->SetId(i, i);
  }

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
