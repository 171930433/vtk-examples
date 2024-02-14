#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkFloatArray
from vtkmodules.vtkCommonDataModel import (
    vtkAMRBox,
    vtkOverlappingAMR,
    vtkSphere,
    vtkUniformGrid
)
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkFiltersGeometry import vtkCompositeDataGeometryFilter
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def MakeScalars(dims, origin, spacing):
    """

    :param dims: The dimensions.
    :param origin: The origin.
    :param spacing: The spacing.
    :return:
    """
    # Implicit function used to compute scalars.
    sphere = vtkSphere(radius=3, center=(5, 5, 5))
    scalars = vtkFloatArray(number_of_tuples=dims[0] * dims[1] * dims[2])
    for k in range(0, dims[2]):
        z = origin[2] + spacing[2] * k
        for j in range(0, dims[1]):
            y = origin[1] + spacing[1] * j
            for i in range(0, dims[0]):
                x = origin[0] + spacing[0] * i
                scalars.SetValue(k * dims[0] * dims[1] + j * dims[0] + i, sphere.EvaluateFunction(x, y, z))
    return scalars


def main():
    colors = vtkNamedColors()

    # Create and populate the AMR dataset
    # The dataset should look like
    # Level 0
    #   uniform grid, dimensions 11, 11, 11, AMR box (0, 0, 0) - (9, 9, 9) 
    # Level 1 - refinement ratio : 2
    #   uniform grid, dimensions 11, 11, 11, AMR box (0, 0, 0) - (9, 9, 9)
    #   uniform grid, dimensions 11, 11, 11, AMR box (10, 10, 10) - (19, 19, 19)
    # Use MakeScalars() above to fill the scalar arrays.

    amr = vtkOverlappingAMR()
    num_levels = 2
    blocks_per_level = (1, 2)
    amr.Initialize(num_levels, blocks_per_level)

    origin = ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [5, 5, 5])
    spacing = ([1.0, 1.0, 1.0], [0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    dims = [11, 11, 11]

    box = list()
    ug = list()
    for i in range(0, 3):
        ug.append(vtkUniformGrid(origin=origin[i], spacing=spacing[i], dimensions=dims))
        ug[i].point_data.SetScalars(MakeScalars(dims, origin[i], spacing[i]))
        box.append(vtkAMRBox())
    # Fill the dataset.
    amr.SetAMRBox(0, 0, box[0])
    amr.SetDataSet(0, 0, ug[0])
    amr.SetAMRBox(1, 0, box[1])
    amr.SetDataSet(1, 0, ug[1])
    amr.SetAMRBox(1, 1, box[2])
    amr.SetDataSet(1, 1, ug[2])
    amr.SetRefinementRatio(0, 2)

    # Render the amr data here.
    of = vtkOutlineFilter()
    # Associate the geometry with a mapper and the mapper to an actor.
    mapper = vtkPolyDataMapper()
    amr >> of >> mapper
    actor1 = vtkActor(mapper=mapper)
    actor1.GetProperty().SetColor(colors.GetColor3d('Yellow'))

    # Create an iso-surface - at 10.
    cf = vtkContourFilter(number_of_contours=1, value=(0, 10.0))
    geomFilter = vtkCompositeDataGeometryFilter()
    # Associate the geometry with a mapper and the mapper to an actor.
    mapper2 = vtkPolyDataMapper()
    amr >> cf >> geomFilter >> mapper2
    actor2 = vtkActor(mapper=mapper2)

    # Create the render window, renderer, and interactor.
    ren = vtkRenderer(background=colors.GetColor3d('CornflowerBlue'))
    # Add the actor to the renderer.
    ren.AddActor(actor1)
    ren.AddActor(actor2)

    ren_win = vtkRenderWindow()
    ren_win.SetWindowName('OverlappingAMR')
    ren_win.AddRenderer(ren)

    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    # Start handling events.
    ren_win.Render()
    iren.Start()


if __name__ == '__main__':
    main()
