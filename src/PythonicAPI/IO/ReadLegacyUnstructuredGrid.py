#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingContextOpenGL2
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkChartsCore import vtkCategoryLegend
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkLookupTable,
    vtkVariantArray
)
from vtkmodules.vtkCommonDataModel import (
    vtkCellTypes,
    vtkGenericCell
)
from vtkmodules.vtkFiltersCore import vtkTubeFilter

# vtkExtractEdges moved from vtkFiltersExtraction to vtkFiltersCore in
# VTK commit d9981b9aeb93b42d1371c6e295d76bfdc18430bd
try:
    from vtkmodules.vtkFiltersCore import vtkExtractEdges
except ImportError:
    from vtkmodules.vtkFiltersExtraction import vtkExtractEdges
from vtkmodules.vtkFiltersGeneral import vtkShrinkFilter
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOLegacy import vtkUnstructuredGridReader
from vtkmodules.vtkRenderingContext2D import vtkContextTransform
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkActor2D,
    vtkCamera,
    vtkDataSetMapper,
    vtkGlyph3DMapper,
    vtkPolyDataMapper,
    vtkRenderWindowInteractor
)
from vtkmodules.vtkRenderingLabel import vtkLabeledDataMapper
from vtkmodules.vtkViewsContext2D import vtkContextView


def get_program_parameters():
    import argparse
    description = 'Display a vtkUnstructuredGrid that contains eleven linear cells.'
    epilogue = '''
    This example also shows how to add a vtkCategoryLegend to a visualization.
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='VTKCellTypes.vtk')
    args = parser.parse_args()
    return args.filename


def main():
    colors = vtkNamedColors()

    filename = get_program_parameters()

    # Create the reader for the data.
    print('Loading ', filename)
    reader = vtkUnstructuredGridReader(file_name=filename)
    reader.update()

    extract_edges = vtkExtractEdges()

    legend_values = vtkVariantArray()
    it = reader.output.NewCellIterator()
    it.InitTraversal()
    while not it.IsDoneWithTraversal():
        cell = vtkGenericCell()
        it.GetCell(cell)
        cell_name = vtkCellTypes.GetClassNameFromTypeId(cell.GetCellType())
        print(f'{cell_name:16s} NumberOfPoints: {cell.number_of_points} CellDimension: {cell.cell_dimension}')
        legend_values.InsertNextValue(cell_name)
        it.GoToNextCell()

    # Tube the edges.
    tubes = vtkTubeFilter(radius=0.05, number_of_sides=21)

    edge_mapper = vtkPolyDataMapper(scalar_range=(0, 26))
    reader >> extract_edges >> tubes >> edge_mapper

    edge_actor = vtkActor(mapper=edge_mapper)
    edge_actor.property.specular = 0.6
    edge_actor.property.specular_power = 30

    # Glyph the points.
    sphere = vtkSphereSource(phi_resolution=21, theta_resolution=21, radius=0.08)

    point_mapper = vtkGlyph3DMapper(source_data=sphere.update().output, scaling=False, scalar_visibility=False)
    reader >> point_mapper

    point_actor = vtkActor(mapper=point_mapper)
    point_actor.property.diffuse_color = colors.GetColor3d('Banana')
    point_actor.property.specular = 0.6
    point_actor.property.specular_color = colors.GetColor3d('White')
    point_actor.property.specular_power = 100

    # Label the points.
    label_mapper = vtkLabeledDataMapper()
    reader >> label_mapper
    label_actor = vtkActor2D(mapper=label_mapper)

    # The geometry.
    geometry_shrink = vtkShrinkFilter(shrink_factor=0.8)

    geometry_mapper = vtkDataSetMapper(scalar_range=(0, 11))
    geometry_mapper.SetScalarModeToUseCellData()
    reader >> geometry_shrink >> geometry_mapper

    geometry_actor = vtkActor()
    geometry_actor.SetMapper(geometry_mapper)
    geometry_actor.GetProperty().SetLineWidth(3)
    geometry_actor.GetProperty().EdgeVisibilityOn()
    geometry_actor.GetProperty().SetEdgeColor(0, 0, 0)

    # NOTE: We must copy the original_lut because the categorical legend
    # needs an indexed lookup table, but the geometry_mapper uses a
    # non-index lookup table.
    original_lut = reader.output.cell_data.scalars.lookup_table

    categorical_lut = vtkLookupTable()
    categorical_lut.DeepCopy(original_lut)
    categorical_lut.IndexedLookupOn()

    # Legend
    for v in range(0, legend_values.GetNumberOfTuples()):
        categorical_lut.SetAnnotation(legend_values.GetValue(v), legend_values.GetValue(v).ToString())
    legend = vtkCategoryLegend()
    legend.SetScalarsToColors(categorical_lut)
    legend.SetValues(legend_values)
    legend.SetTitle('Cell Type')
    legend.GetBrush().SetColor(colors.GetColor4ub('Silver'))

    width = 640
    height = 480
    place_legend = vtkContextTransform()
    place_legend.AddItem(legend)
    place_legend.Translate(width - 20, height - 12 * 16)

    context_view = vtkContextView()
    context_view.scene.AddItem(place_legend)

    renderer = context_view.renderer
    renderer.background = colors.GetColor3d('SlateGray')

    render_window = context_view.render_window
    render_window.size = (width, height)
    render_window.window_name = 'ReadLegacyUnstructuredGrid'

    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    renderer.AddActor(geometry_actor)
    renderer.AddActor(label_actor)
    renderer.AddActor(edge_actor)
    renderer.AddActor(point_actor)

    a_camera = vtkCamera()
    a_camera.Azimuth(-40.0)
    a_camera.Elevation(50.0)

    renderer.SetActiveCamera(a_camera)
    renderer.ResetCamera()

    render_window.Render()

    render_window_interactor.Start()


if __name__ == '__main__':
    main()
