#!/usr/bin/env python3

"""
Define an implicit function, then, for this function:
 - create the outline
 - surface contours
 - three planes
 - contour each of the three planes
"""

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkQuadric
from vtkmodules.vtkFiltersCore import (
    vtkAppendFilter,
    vtkContourFilter
)
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkImagingCore import vtkExtractVOI
from vtkmodules.vtkImagingHybrid import vtkSampleFunction
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Sample the quadric function.
    quadric = vtkQuadric(coefficients=(1, 2, 3, 0, 1, 0, 0, 0, 0, 0))
    sample = vtkSampleFunction(sample_dimensions=(25, 25, 25), implicit_function=quadric)

    iso_actor = create_isosurface(sample)
    outline_iso_actor = create_outline(sample)

    planes_actor = create_planes(sample, 3)
    planes_actor.property.ambient = 1.0
    outline_planes_actor = create_outline(sample)

    planes_actor.AddPosition(iso_actor.GetBounds()[0] * 2.0, 0, 0)
    outline_planes_actor.AddPosition(iso_actor.GetBounds()[0] * 2.0, 0, 0)

    contour_actor = create_contours(sample, 3, 15)
    contour_actor.property.ambient = 1.0
    outline_contour_actor = create_outline(sample)

    contour_actor.AddPosition(iso_actor.GetBounds()[0] * 4.0, 0, 0)
    outline_contour_actor.AddPosition(iso_actor.GetBounds()[0] * 4.0, 0, 0)

    renderer = vtkRenderer(background=colors.GetColor3d('SlateGray'), two_sided_lighting=True)
    renderer.AddActor(planes_actor)
    renderer.AddActor(outline_planes_actor)
    renderer.AddActor(contour_actor)
    renderer.AddActor(outline_contour_actor)
    renderer.AddActor(iso_actor)
    renderer.AddActor(outline_iso_actor)

    # Try to set the camera to match the figure in the book.
    renderer.active_camera.position = (0, -1, 0)
    renderer.active_camera.focal_point = (0, 0, 0)
    renderer.active_camera.view_up = (0, 0, -1)
    renderer.ResetCamera()
    renderer.active_camera.Elevation(20)
    renderer.active_camera.Azimuth(10)
    renderer.active_camera.Dolly(1.2)
    renderer.ResetCameraClippingRange()

    render_window = vtkRenderWindow(size=(640, 480), window_name='QuadricVisualization')
    render_window.AddRenderer(renderer)

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Interact with the data.
    interactor.Start()


def create_isosurface(func, number_of_iso_surfaces=5):
    """
    Create isosurfaces from the implicit function.
    :param func: The implicit function.
    :param number_of_iso_surfaces: Number of isosurfaces.
    :return: An actor.
    """
    contour = vtkContourFilter()
    ranges = [1.0, 6.0]
    contour.GenerateValues(number_of_iso_surfaces, ranges)
    # Map the contours
    mapper = vtkPolyDataMapper(scalar_range=(0, 7))
    func >> contour >> mapper
    return vtkActor(mapper=mapper)


def create_planes(func, number_of_planes):
    """
    Extract planes from the implicit function.
    :param func: The implicit function.
    :param number_of_planes: Number of planes.
    :return: An actor.
    """
    dims = func.GetSampleDimensions()
    slice_incr = (dims[2] - 1) // (number_of_planes + 1)
    slice_num = -4
    slices = list()
    for i in range(0, number_of_planes):
        extract = vtkExtractVOI(v_o_i=(0, dims[0] - 1, 0, dims[1] - 1,
                                       slice_num + slice_incr, slice_num + slice_incr))
        slices.append(func >> extract)
        slice_num += slice_incr

    append = vtkAppendFilter()
    mapper = vtkDataSetMapper(scalar_range=(0, 7))
    slices >> append >> mapper

    return vtkActor(mapper=mapper)


def create_contours(func, number_of_planes, number_of_contours):
    """
    Extract planes from the implicit function and contour them.
    :param func: The implicit function.
    :param number_of_planes: Number of planes.
    :param number_of_contours: Number of contours.
    :return: An actor.
    """
    #
    dims = func.GetSampleDimensions()
    slice_incr = (dims[2] - 1) // (number_of_planes + 1)
    slice_num = -4
    ranges = [1.0, 6.0]
    contours = list()
    for i in range(0, number_of_planes):
        extract = vtkExtractVOI(v_o_i=(0, dims[0] - 1, 0, dims[1] - 1,
                                       slice_num + slice_incr, slice_num + slice_incr))
        contour = vtkContourFilter(number_of_contours=number_of_contours)
        contour.GenerateValues(number_of_contours, ranges)
        contours.append(func >> extract >> contour)
        slice_num += slice_incr

    append = vtkAppendFilter()
    mapper = vtkDataSetMapper(scalar_range=(0, 7))
    contours >> append >> mapper

    return vtkActor(mapper=mapper)


def create_outline(source):
    source >> vtkOutlineFilter()
    mapper = vtkPolyDataMapper()
    source >> vtkOutlineFilter() >> mapper
    return vtkActor(mapper=mapper)


if __name__ == '__main__':
    main()
