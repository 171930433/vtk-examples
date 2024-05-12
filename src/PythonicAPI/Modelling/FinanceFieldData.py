#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import (
    vtkDataObjectToDataSetFilter,
    vtkFieldDataToAttributeDataFilter,
    vtkTubeFilter
)
from vtkmodules.vtkFiltersGeneral import (
    vtkAxes,
    vtkMarchingContourFilter
)
from vtkmodules.vtkIOLegacy import vtkDataObjectReader
from vtkmodules.vtkImagingHybrid import vtkGaussianSplatter
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkFollower,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkRenderingFreeType import vtkVectorText


def main():
    ifn = get_program_parameters()

    colors = vtkNamedColors()

    reader = vtkDataObjectReader(file_name=ifn)

    size = 3187  # maximum number possible

    axes_parameters = AxesParameters()

    # Extract data from field as a polydata (just points), then extract scalars.
    do2ds = vtkDataObjectToDataSetFilter(data_set_type=DataObjectToDataSetFilter.DataSetType.VTK_POLY_DATA,
                                         default_normalize=True)
    do2ds.SetPointComponent(0, axes_parameters.labels['x'], 0)
    do2ds.SetPointComponent(1, axes_parameters.labels['y'], 0, 0, size, 1)
    do2ds.SetPointComponent(2, axes_parameters.labels['z'], 0)
    fd2ad = vtkFieldDataToAttributeDataFilter(
        input_field=FieldDataToAttributeDataFilter.InputField.VTK_DATA_OBJECT_FIELD,
        output_attribute_data=FieldDataToAttributeDataFilter.OutputAttributeData.VTK_POINT_DATA,
        default_normalize=True
    )
    fd2ad.SetScalarComponent(0, axes_parameters.labels['scalar'], 0)

    pop_splatter = vtkGaussianSplatter(sample_dimensions=(150, 150, 150), radius=0.05, scalar_warping=False)

    pop_surface = vtkMarchingContourFilter()
    pop_surface.SetValue(0, 0.01)

    pop_mapper = vtkPolyDataMapper(scalar_visibility=False)
    reader >> do2ds >> fd2ad >> pop_splatter >> pop_surface >> pop_mapper

    pop_actor = vtkActor(mapper=pop_mapper)
    pop_actor.property.opacity = 0.3
    pop_actor.property.color = colors.GetColor3d('Gold')

    # Construct the pipeline for the delinquent population.
    late_splatter = vtkGaussianSplatter(sample_dimensions=(150, 150, 150), radius=0.05, scale_factor=0.05)

    late_surface = vtkMarchingContourFilter()
    late_surface.SetValue(0, 0.01)

    late_mapper = vtkPolyDataMapper(scalar_visibility=False)
    reader >> do2ds >> fd2ad >> late_splatter >> late_surface >> late_mapper

    late_actor = vtkActor(mapper=late_mapper)
    late_actor.SetMapper(late_mapper)
    late_actor.property.color = colors.GetColor3d('Red')

    # Create axes.
    bounds = pop_splatter.update().output.bounds
    scale_factor = pop_splatter.output.length / 5
    axes = vtkAxes(origin=(bounds[0], bounds[2], bounds[4]), scale_factor=scale_factor)

    axes_tubes = vtkTubeFilter(radius=axes.scale_factor / 55.0, number_of_sides=6)

    axes_mapper = vtkPolyDataMapper()
    axes >> axes_tubes >> axes_mapper

    axes_actor = vtkActor(mapper=axes_mapper)

    # Label the axes.
    axes_parameters = AxesParameters()
    axes = make_axes_labels(axes_parameters)

    # Graphics stuff.
    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    render_window = vtkRenderWindow(size=(650, 480), window_name='FinanceFieldData')
    render_window.AddRenderer(renderer)
    interactor = vtkRenderWindowInteractor()
    interactor.render_window = render_window

    # Add the actors to the renderer.
    renderer.AddActor(axes_actor)
    renderer.AddActor(late_actor)
    for axis_actor in axes:
        renderer.AddActor(axis_actor)
    renderer.AddActor(pop_actor)

    camera = vtkCamera(clipping_range=(.274, 13.72), focal_point=(0.433816, 0.333131, 0.449),
                       position=(-1.96987, 1.15145, 1.49053), view_up=(0.378927, 0.911821, 0.158107)
                       )
    renderer.active_camera = camera
    for axis_actor in axes:
        axis_actor.camera = camera

    # Render and interact with the data.
    render_window.Render()
    interactor.Start()


def make_axes_labels(ap):
    """

    :param ap: The parameters for the axes labels.
    :return:
    """
    nc = vtkNamedColors()

    axes_actors = list()
    indices = ['x', 'y', 'z']
    for idx in indices:
        text = vtkVectorText(text=ap.labels[idx])
        mapper = vtkPolyDataMapper()
        text >> mapper
        actor = vtkFollower(mapper=mapper, scale=ap.scale[idx], position=ap.position[idx])
        actor.property.color = nc.GetColor3d(ap.color[idx])
        axes_actors.append(actor)
    return axes_actors


def get_program_parameters():
    import argparse
    description = 'Visualization of multidimensional financial data.'
    epilogue = '''
    This example is similar to /Python/Modelling/Finance.py, 
    but here we read a .vtk file with vtkDataObjectReader.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('filename', help='financial.vtk')

    args = parser.parse_args()
    return args.filename


class AxesParameters:
    scale = {'x': (0.02, 0.02, 0.02), 'y': (0.02, 0.02, 0.02), 'z': (0.02, 0.02, 0.02)}
    position = {'x': (0.35, -0.05, -0.05), 'y': (-0.05, 0.35, -0.05), 'z': (-0.05, -0.05, 0.35)}
    color = {'x': 'Black', 'y': 'Black', 'z': 'Black'}
    labels = {'x': 'INTEREST_RATE', 'y': 'MONTHLY_PAYMENT', 'z': 'MONTHLY_INCOME', 'scalar': 'TIME_LATE'}


@dataclass(frozen=True)
class DataObjectToDataSetFilter:
    @dataclass(frozen=True)
    class DataSetType:
        VTK_POLY_DATA: int = 0
        VTK_STRUCTURED_POINTS: int = 1
        VTK_STRUCTURED_GRID: int = 2
        VTK_RECTILINEAR_GRID: int = 3
        VTK_UNSTRUCTURED_GRID: int = 4


@dataclass(frozen=True)
class FieldDataToAttributeDataFilter:
    @dataclass(frozen=True)
    class InputField:
        VTK_DATA_OBJECT_FIELD: int = 0
        VTK_POINT_DATA_FIELD: int = 1
        VTK_CELL_DATA_FIELD: int = 2

    @dataclass(frozen=True)
    class OutputAttributeData:
        VTK_CELL_DATA: int = 0
        VTK_POINT_DATA: int = 1


if __name__ == '__main__':
    main()
