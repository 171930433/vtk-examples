#!/usr/bin/env python

import math

import numpy as np
from vtk.util import numpy_support
from vtkmodules.numpy_interface import dataset_adapter as dsa
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonComputationalGeometry import (
    vtkParametricBour,
    vtkParametricEnneper,
    vtkParametricMobius,
    vtkParametricRandomHills,
    vtkParametricTorus
)
from vtkmodules.vtkCommonCore import (
    VTK_DOUBLE,
    VTK_VERSION_NUMBER,
    vtkDoubleArray,
    vtkFloatArray,
    vtkIdList,
    vtkLookupTable,
    vtkPoints,
    vtkVersion
)
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import (
    vtkDelaunay2D,
    vtkFeatureEdges,
    vtkIdFilter,
    vtkPolyDataNormals,
    vtkPolyDataTangents,
    vtkTriangleFilter
)
from vtkmodules.vtkFiltersGeneral import (
    vtkCurvatures,
    vtkTransformPolyDataFilter
)
from vtkmodules.vtkFiltersModeling import vtkLinearSubdivisionFilter
from vtkmodules.vtkFiltersSources import (
    vtkCubeSource,
    vtkParametricFunctionSource,
    vtkTexturedSphereSource
)
# noinspection PyUnresolvedReferences
from vtkmodules.vtkIOXML import vtkXMLPolyDataWriter
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkInteractionWidgets import (
    vtkCameraOrientationWidget,
    vtkScalarBarRepresentation,
    vtkScalarBarWidget,
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkColorTransferFunction,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty

)


def main(argv):
    # desired_surface = 'Bour'
    # desired_surface = 'Cube'
    # desired_surface = 'Hills'
    # desired_surface = 'Enneper'
    # desired_surface = 'Mobius'
    desired_surface = 'RandomHills'
    # desired_surface = 'Sphere'
    # desired_surface = 'Torus'
    source = get_source(desired_surface)
    if not source:
        print('The surface is not available.')
        return

    curvature_name = 'Gauss_Curvature'
    curvature_type = 0  # Gaussian
    gc = (source >> vtkCurvatures(curvature_type=curvature_type)).update().output
    if desired_surface in ['Bour', 'Enneper', 'Hills', 'RandomHills', 'Torus']:
        adjust_edge_curvatures(gc, 'Gauss_Curvature')
    if desired_surface == 'Bour':
        # Gaussian curvature is -1/(r(r+1)^4))
        constrain_curvatures(gc, curvature_name, -0.0625, -0.0625)
    if desired_surface == 'Enneper':
        # Gaussian curvature is -4/(1 + r^2)^4
        constrain_curvatures(gc, curvature_name, -0.25, -0.25)
    if desired_surface == 'Cube':
        constrain_curvatures(gc, curvature_name, 0.0, 0.0)
    if desired_surface == 'Mobius':
        constrain_curvatures(gc, curvature_name, 0.0, 0.0)
    if desired_surface == 'Sphere':
        # Gaussian curvature is 1/r^2
        constrain_curvatures(gc, curvature_name, 4.0, 4.0)
    source.point_data.AddArray(
        gc.point_data.GetAbstractArray(curvature_name))

    curvature_name = 'Mean_Curvature'
    curvature_type = 1  # Mean
    mc = (source >> vtkCurvatures(curvature_type=curvature_type)).update().output
    if desired_surface in ['Bour', 'Enneper', 'Hills', 'RandomHills', 'Torus']:
        adjust_edge_curvatures(mc, curvature_name)
    if desired_surface == 'Bour':
        # Mean curvature is 0
        constrain_curvatures(mc, curvature_name, 0.0, 0.0)
    if desired_surface == 'Enneper':
        # Mean curvature is 0
        constrain_curvatures(mc, curvature_name, 0.0, 0.0)
    if desired_surface == 'Mobius':
        constrain_curvatures(mc, curvature_name, -0.6, 0.6)
    if desired_surface == 'Sphere':
        # Mean curvature is 1/r
        constrain_curvatures(mc, curvature_name, 2.0, 2.0)
    source.point_data.AddArray(
        mc.point_data.GetAbstractArray(curvature_name))

    # Uncomment the following lines if you want to write out the polydata.
    # writer = vtkXMLPolyDataWriter(file_name='Source.vtp')
    # writer.SetDataModeToBinary()
    # source >> writer
    # writer.Write()

    # Let's visualise what we have done.

    colors = vtkNamedColors()
    colors.SetColor("ParaViewBkg", [82, 87, 110, 255])

    window_width = 1024
    window_height = 512

    ren_win = vtkRenderWindow(size=(window_width, window_height), window_name='CurvaturesAdjustEdges')
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)
    style = vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)

    lut = get_diverging_lut()
    # lut = get_diverging_lut1()

    # Define viewport ranges [x_min, y_min, x_max, y_max]
    viewports = {0: [0.0, 0.0, 0.5, 1.0],
                 1: [0.5, 0.0, 1.0, 1.0],
                 }

    camera = None
    cam_orient_manipulator = None

    has_cow = False
    if vtk_version_ok(9, 0, 20210718):
        cam_orient_manipulator = vtkCameraOrientationWidget()
        has_cow = True

    # Build the renderers and add them to the render window.
    renderers = list()
    scalar_bar_representations = list()
    scalar_bar_widgets = list()
    curvature_types = {0: 'Gauss_Curvature', 1: 'Mean_Curvature'}
    scalar_bar_positions = {0: {'p': [0.85, 0.1, 0], 'p2': [0.13, 0.6, 0]},
                            1: {'p': [0.85, 0.1, 0], 'p2': [0.13, 0.6, 0]},
                            }
    title_text_property = vtkTextProperty(color=colors.GetColor3d('AliceBlue'), bold=True, italic=True, shadow=True,
                                          font_size=14)

    for k, v in curvature_types.items():
        curvature_title = v.replace('_', '\n')

        source.point_data.SetActiveScalars(v)
        scalar_range = source.point_data.GetScalars(v).GetRange()

        bands = get_bands(scalar_range, 10)
        freq = get_frequencies(bands, source)
        bands, freq = adjust_ranges(bands, freq)
        print(v.replace('_', ' '))
        print_bands_frequencies(bands, freq)

        mapper = vtkPolyDataMapper(scalar_range=scalar_range, lookup_table=lut)
        mapper.SetScalarModeToUsePointFieldData()
        mapper.SelectColorArray(v)
        source >> mapper

        actor = vtkActor(mapper=mapper)

        renderers.append(vtkRenderer(background=colors.GetColor3d('ParaViewBkg')))
        renderers[k].AddActor(actor)

        # Create a scalar bar.
        scalar_bar = vtkScalarBarActor(lookup_table=mapper.GetLookupTable(), title=curvature_title + '\n',
                                       unconstrained_font_size=True, number_of_labels=min(5, len(freq)),
                                       title_text_property=title_text_property
                                       )

        # Create the scalar bar representation. Used for positioning the scalar bar actor.
        scalar_bar_representations.append(vtkScalarBarRepresentation(enforce_normalized_viewport_bounds=True))
        scalar_bar_representations[k].GetPositionCoordinate().value = scalar_bar_positions[k]['p']
        scalar_bar_representations[k].GetPosition2Coordinate().value = scalar_bar_positions[k]['p2']

        # Create the scalar_bar_widget.
        scalar_bar_widgets.append(
            vtkScalarBarWidget(representation=scalar_bar_representations[k], scalar_bar_actor=scalar_bar))
        scalar_bar_widgets[k].SetDefaultRenderer(renderers[k])
        scalar_bar_widgets[k].SetInteractor(iren)

        ren_win.AddRenderer(renderers[k])

        if k == 0:
            if has_cow:
                cam_orient_manipulator.SetParentRenderer(renderers[k])
            camera = renderers[k].GetActiveCamera()
            camera.Elevation(60)
        else:
            renderers[k].SetActiveCamera(camera)

        renderers[k].SetViewport(*viewports[k])
        renderers[k].ResetCamera()

    # Create the TextActors.
    text_actors = list()
    text_representations = list()
    text_widgets = list()
    text_scale_mode = {'none': 0, 'prop': 1, 'viewport': 2}
    text_positions = {0: {'p': [0.35, 0.01, 0], 'p2': [0.27, 0.10, 0]},
                      1: {'p': [0.37, 0.01, 0], 'p2': [0.27, 0.10, 0]},
                      }
    text_property = vtkTextProperty(color=colors.GetColor3d('AliceBlue'), bold=True, italic=True, shadow=True,
                                    font_size=24)
    for k, v in curvature_types.items():
        curvature_title = v.replace('_', '\n')
        text_actors.append(
            vtkTextActor(input=curvature_title, text_scale_mode=text_scale_mode['none'], text_property=text_property))

        # Create the text representation. Used for positioning the text actor.
        text_representations.append(vtkTextRepresentation(enforce_normalized_viewport_bounds=True))
        text_representations[k].GetPositionCoordinate().value = text_positions[k]['p']
        text_representations[k].GetPosition2Coordinate().value = text_positions[k]['p2']

        # Create the TextWidget
        text_widgets.append(vtkTextWidget(representation=text_representations[k], text_actor=text_actors[k]))
        text_widgets[k].SetDefaultRenderer(renderers[k])
        text_widgets[k].SetInteractor(iren)
        text_widgets[k].SelectableOff()

    # Enable the widgets.
    if has_cow:
        cam_orient_manipulator.On()

    for k in curvature_types.keys():
        text_widgets[k].On()
        scalar_bar_widgets[k].On()

    ren_win.Render()
    iren.Start()


def vtk_version_ok(major, minor, build):
    """
    Check the VTK version.

    :param major: Major version.
    :param minor: Minor version.
    :param build: Build version.
    :return: True if the requested VTK version is greater or equal to the actual VTK version.
    """
    needed_version = 10000000000 * int(major) \
                     + 100000000 * int(minor) \
                     + int(build)
    try:
        vtk_version_number = VTK_VERSION_NUMBER
    except AttributeError:
        # Expand component-wise comparisons for VTK versions < 8.90.
        ver = vtkVersion()
        vtk_version_number = 10000000000 * ver.v_t_k_major_version() \
                             + 100000000 * ver.v_t_k_minor_version() \
                             + ver.v_t_k_build_version()
    if vtk_version_number >= needed_version:
        return True
    else:
        return False


def adjust_edge_curvatures(source, curvature_name, epsilon=1.0e-08):
    """
    This function adjusts curvatures along the edges of the surface by replacing
     the value with the average value of the curvatures of points in the neighborhood.

    Remember to update the vtkCurvatures object before calling this.

    :param source: A vtkPolyData object corresponding to the vtkCurvatures object.
    :param curvature_name: The name of the curvature, 'Gauss_Curvature' or 'Mean_Curvature'.
    :param epsilon: Absolute curvature values less than this will be set to zero.
    :return:
    """

    def point_neighbourhood(pt_id):
        """
        Find the ids of the neighbours of pt_id.

        :param pt_id: The point id.
        :return: The neighbour ids.
        """
        """
        Extract the topological neighbors for point pId. In two steps:
        1) source.GetPointCells(pt_id, cell_ids)
        2) source.GetCellPoints(cell_id, cell_point_ids) for all cell_id in cell_ids
        """
        cell_ids = vtkIdList()
        source.GetPointCells(pt_id, cell_ids)
        neighbour = set()
        for cell_idx in range(0, cell_ids.GetNumberOfIds()):
            cell_id = cell_ids.GetId(cell_idx)
            cell_point_ids = vtkIdList()
            source.GetCellPoints(cell_id, cell_point_ids)
            for cell_pt_idx in range(0, cell_point_ids.GetNumberOfIds()):
                neighbour.add(cell_point_ids.GetId(cell_pt_idx))
        return neighbour

    def compute_distance(pt_id_a, pt_id_b):
        """
        Compute the distance between two points given their ids.

        :param pt_id_a:
        :param pt_id_b:
        :return:
        """
        pt_a = np.array(source.GetPoint(pt_id_a))
        pt_b = np.array(source.GetPoint(pt_id_b))
        return np.linalg.norm(pt_a - pt_b)

    # Get the active scalars
    source.point_data.SetActiveScalars(curvature_name)
    np_source = dsa.WrapDataObject(source)
    curvatures = np_source.PointData[curvature_name]

    #  Get the boundary point IDs.
    array_name = 'ids'
    id_filter = vtkIdFilter(point_ids=True, cell_ids=False,
                            point_ids_array_name=array_name,
                            cell_ids_array_name=array_name)

    edges = vtkFeatureEdges(boundary_edges=True, manifold_edges=False,
                            non_manifold_edges=False, feature_edges=False)

    (source >> id_filter >> edges).update()

    edge_array = edges.GetOutput().GetPointData().GetArray(array_name)
    boundary_ids = []
    for i in range(edges.GetOutput().GetNumberOfPoints()):
        boundary_ids.append(edge_array.GetValue(i))
    # Remove duplicate Ids.
    p_ids_set = set(boundary_ids)

    # Iterate over the edge points and compute the curvature as the weighted
    # average of the neighbours.
    count_invalid = 0
    for p_id in boundary_ids:
        p_ids_neighbors = point_neighbourhood(p_id)
        # Keep only interior points.
        p_ids_neighbors -= p_ids_set
        # Compute distances and extract curvature values.
        curvs = [curvatures[p_id_n] for p_id_n in p_ids_neighbors]
        dists = [compute_distance(p_id_n, p_id) for p_id_n in p_ids_neighbors]
        curvs = np.array(curvs)
        dists = np.array(dists)
        curvs = curvs[dists > 0]
        dists = dists[dists > 0]
        if len(curvs) > 0:
            weights = 1 / np.array(dists)
            weights /= weights.sum()
            new_curv = np.dot(curvs, weights)
        else:
            # Corner case.
            count_invalid += 1
            # Assuming the curvature of the point is planar.
            new_curv = 0.0
        # Set the new curvature value.
        curvatures[p_id] = new_curv

    #  Set small values to zero.
    if epsilon != 0.0:
        curvatures = np.where(abs(curvatures) < epsilon, 0, curvatures)
        curv = numpy_support.numpy_to_vtk(num_array=curvatures.ravel(),
                                          deep=True,
                                          array_type=VTK_DOUBLE)
        curv.name = curvature_name
        source.point_data.RemoveArray(curvature_name)
        source.point_data.AddArray(curv)
        source.point_data.active_scalars = curvature_name


def constrain_curvatures(source, curvature_name, lower_bound=0.0, upper_bound=0.0):
    """
    This function constrains curvatures to the range [lower_bound ... upper_bound].

    Remember to update the vtkCurvatures object before calling this.

    :param source: A vtkPolyData object corresponding to the vtkCurvatures object.
    :param curvature_name: The name of the curvature, 'Gauss_Curvature' or 'Mean_Curvature'.
    :param lower_bound: The lower bound.
    :param upper_bound: The upper bound.
    :return:
    """

    bounds = list()
    if lower_bound < upper_bound:
        bounds.append(lower_bound)
        bounds.append(upper_bound)
    else:
        bounds.append(upper_bound)
        bounds.append(lower_bound)

    # Get the active scalars
    source.point_data.SetActiveScalars(curvature_name)
    np_source = dsa.WrapDataObject(source)
    curvatures = np_source.PointData[curvature_name]

    # Set upper and lower bounds.
    curvatures = np.where(curvatures < bounds[0], bounds[0], curvatures)
    curvatures = np.where(curvatures > bounds[1], bounds[1], curvatures)
    curv = numpy_support.numpy_to_vtk(num_array=curvatures.ravel(),
                                      deep=True,
                                      array_type=VTK_DOUBLE)
    curv.name = curvature_name
    source.point_data.RemoveArray(curvature_name)
    source.point_data.AddArray(curv)
    source.point_data.active_scalars = curvature_name


def get_diverging_lut():
    """
    See: [Diverging Color Maps for Scientific Visualization](https://www.kennethmoreland.com/color-maps/)
                       start point         midPoint            end point
     cool to warm:     0.230, 0.299, 0.754 0.865, 0.865, 0.865 0.706, 0.016, 0.150
     purple to orange: 0.436, 0.308, 0.631 0.865, 0.865, 0.865 0.759, 0.334, 0.046
     green to purple:  0.085, 0.532, 0.201 0.865, 0.865, 0.865 0.436, 0.308, 0.631
     blue to brown:    0.217, 0.525, 0.910 0.865, 0.865, 0.865 0.677, 0.492, 0.093
     green to red:     0.085, 0.532, 0.201 0.865, 0.865, 0.865 0.758, 0.214, 0.233

    :return:
    """
    ctf = vtkColorTransferFunction()
    ctf.SetColorSpaceToDiverging()
    # Cool to warm.
    ctf.AddRGBPoint(0.0, 0.230, 0.299, 0.754)
    ctf.AddRGBPoint(0.5, 0.865, 0.865, 0.865)
    ctf.AddRGBPoint(1.0, 0.706, 0.016, 0.150)

    table_size = 256
    lut = vtkLookupTable(number_of_table_values=table_size)
    lut.Build()

    for i in range(0, table_size):
        rgba = list(ctf.GetColor(float(i) / table_size)) + [1.0]
        lut.SetTableValue(i, rgba)

    return lut


def get_diverging_lut1():
    colors = vtkNamedColors()
    # Colour transfer function.
    ctf = vtkColorTransferFunction()
    ctf.SetColorSpaceToDiverging()
    p1 = [0.0] + list(colors.GetColor3d('MidnightBlue'))
    p2 = [0.5] + list(colors.GetColor3d('Gainsboro'))
    p3 = [1.0] + list(colors.GetColor3d('DarkOrange'))
    ctf.AddRGBPoint(*p1)
    ctf.AddRGBPoint(*p2)
    ctf.AddRGBPoint(*p3)

    table_size = 256
    lut = vtkLookupTable(number_of_table_values=table_size)
    lut.Build()

    for i in range(0, table_size):
        rgba = list(ctf.GetColor(float(i) / table_size)) + [1.0]
        lut.SetTableValue(i, rgba)

    return lut


def get_bour():
    surface = vtkParametricBour()

    u_resolution = 51
    v_resolution = 51
    source = vtkParametricFunctionSource(parametric_function=surface,
                                         u_resolution=u_resolution, v_resolution=v_resolution,
                                         generate_texture_coordinates=True)

    # Build the tangents.
    tangents = vtkPolyDataTangents()

    transform = vtkTransform()
    transform.RotateX(0.0)

    transform_filter = vtkTransformPolyDataFilter(transform=transform)

    return (source >> tangents >> transform_filter).update().output


def get_cube():
    surface = vtkCubeSource()

    # Triangulate.
    triangulation = vtkTriangleFilter()
    # Subdivide the triangles.
    subdivide = vtkLinearSubdivisionFilter(number_of_subdivisions=3)
    # Build the tangents.
    tangents = vtkPolyDataTangents()

    return (surface >> triangulation >> subdivide >> tangents).update().output


def get_hills():
    # Create four hills on a plane.
    # This will have regions of negative, zero and positive Gsaussian curvatures.

    x_res = 50
    y_res = 50
    x_min = -5.0
    x_max = 5.0
    dx = (x_max - x_min) / (x_res - 1)
    y_min = -5.0
    y_max = 5.0
    dy = (y_max - y_min) / (x_res - 1)

    # Make a grid.
    points = vtkPoints()
    for i in range(0, x_res):
        x = x_min + i * dx
        for j in range(0, y_res):
            y = y_min + j * dy
            points.InsertNextPoint(x, y, 0)

    # Add the grid points to a polydata object.
    plane = vtkPolyData(points=points)

    # Triangulate the grid.
    delaunay = vtkDelaunay2D()

    polydata = (plane >> delaunay).update().output

    elevation = vtkDoubleArray()
    elevation.SetNumberOfTuples(points.GetNumberOfPoints())

    #  We define the parameters for the hills here.
    # [[0: x0, 1: y0, 2: x variance, 3: y variance, 4: amplitude]...]
    hd = [[-2.5, -2.5, 2.5, 6.5, 3.5], [2.5, 2.5, 2.5, 2.5, 2],
          [5.0, -2.5, 1.5, 1.5, 2.5], [-5.0, 5, 2.5, 3.0, 3]]
    xx = [0.0] * 2
    for i in range(0, points.number_of_points):
        x = list(polydata.GetPoint(i))
        for j in range(0, len(hd)):
            xx[0] = (x[0] - hd[j][0] / hd[j][2]) ** 2.0
            xx[1] = (x[1] - hd[j][1] / hd[j][3]) ** 2.0
            x[2] += hd[j][4] * math.exp(-(xx[0] + xx[1]) / 2.0)
            polydata.GetPoints().SetPoint(i, x)
            elevation.SetValue(i, x[2])

    textures = vtkFloatArray(number_of_components=2,
                             number_of_tuples=2 * polydata.GetNumberOfPoints(),
                             name='Textures')

    for i in range(0, x_res):
        tc = [i / (x_res - 1.0), 0.0]
        for j in range(0, y_res):
            # tc[1] = 1.0 - j / (y_res - 1.0)
            tc[1] = j / (y_res - 1.0)
            textures.SetTuple(i * y_res + j, tc)

    polydata.point_data.SetScalars(elevation)
    polydata.point_data.GetScalars().name = "Elevation"
    polydata.point_data.SetTCoords(textures)

    normals = vtkPolyDataNormals(feature_angle=30, splitting=False)

    # Build the tangents.
    tangents = vtkPolyDataTangents()

    transform = vtkTransform()
    transform.RotateX(-90)

    transform_filter = vtkTransformPolyDataFilter()
    transform_filter.SetTransform(transform)

    return (polydata >> normals >> tangents >> transform_filter).update().output


def get_enneper():
    surface = vtkParametricEnneper()

    u_resolution = 51
    v_resolution = 51
    source = vtkParametricFunctionSource(parametric_function=surface,
                                         u_resolution=u_resolution, v_resolution=v_resolution,
                                         generate_texture_coordinates=True)

    # Build the tangents.
    tangents = vtkPolyDataTangents()

    transform = vtkTransform()
    transform.RotateX(0.0)

    transform_filter = vtkTransformPolyDataFilter(transform=transform)

    return (source >> tangents >> transform_filter).update().output


def get_mobius():
    minimum_v = -0.25
    maximum_v = 0.25
    surface = vtkParametricMobius(minimum_v=minimum_v, maximum_v=maximum_v, )

    u_resolution = 51
    v_resolution = 51
    source = vtkParametricFunctionSource(parametric_function=surface,
                                         u_resolution=u_resolution, v_resolution=v_resolution,
                                         generate_texture_coordinates=True)

    # Build the tangents.
    tangents = vtkPolyDataTangents()

    transform = vtkTransform()
    transform.RotateX(-90.0)

    transform_filter = vtkTransformPolyDataFilter(transform=transform)

    return (source >> tangents >> transform_filter).update().output


def get_random_hills():
    random_seed = 1
    number_of_hills = 30
    # If you want a plane
    # hill_amplitude=0
    surface = vtkParametricRandomHills(random_seed=random_seed, number_of_hills=number_of_hills)

    u_resolution = 51
    v_resolution = 51
    source = vtkParametricFunctionSource(parametric_function=surface,
                                         u_resolution=u_resolution, v_resolution=v_resolution,
                                         generate_texture_coordinates=True)

    # Build the tangents.
    tangents = vtkPolyDataTangents()

    transform = vtkTransform()
    transform.Translate(0.0, 5.0, 15.0)
    transform.RotateX(-90.0)

    transform_filter = vtkTransformPolyDataFilter(transform=transform)

    return (source >> tangents >> transform_filter).update().output


def get_sphere():
    theta_resolution = 32
    phi_resolution = 32
    surface = vtkTexturedSphereSource(theta_resolution=theta_resolution, phi_resolution=phi_resolution)

    # Now the tangents.
    tangents = vtkPolyDataTangents()

    return (surface >> tangents).update().output


def get_torus():
    surface = vtkParametricTorus()

    u_resolution = 51
    v_resolution = 51
    source = vtkParametricFunctionSource(parametric_function=surface,
                                         u_resolution=u_resolution, v_resolution=v_resolution,
                                         generate_texture_coordinates=True)

    # Build the tangents.
    tangents = vtkPolyDataTangents()

    transform = vtkTransform()
    transform.RotateX(-90.0)

    transform_filter = vtkTransformPolyDataFilter(transform=transform)

    return (source >> tangents >> transform_filter).update().output


def get_source(source):
    surface = source.lower()
    available_surfaces = ['bour', 'cube', 'enneper', 'hills', 'mobius', 'randomhills', 'sphere', 'torus']
    if surface not in available_surfaces:
        return None
    elif surface == 'bour':
        return get_bour()
    elif surface == 'cube':
        return get_cube()
    elif surface == 'enneper':
        return get_enneper()
    elif surface == 'hills':
        return get_hills()
    elif surface == 'mobius':
        return get_mobius()
    elif surface == 'randomhills':
        return get_random_hills()
    elif surface == 'sphere':
        return get_sphere()
    elif surface == 'torus':
        return get_torus()
    return None


def get_frequencies(bands, src):
    """
    Count the number of scalars in each band.
    The scalars used are the active scalars in the polydata.

    :param: bands - The bands.
    :param: src - The vtkPolyData source.
    :return: The frequencies of the scalars in each band.
    """
    freq = dict()
    for i in range(len(bands)):
        freq[i] = 0
    tuples = src.point_data.GetScalars().GetNumberOfTuples()
    for i in range(tuples):
        x = src.point_data.GetScalars().GetTuple1(i)
        for j in range(len(bands)):
            if x <= bands[j][2]:
                freq[j] += 1
                break
    return freq


def adjust_ranges(bands, freq):
    """
    The bands and frequencies are adjusted so that the first and last
     frequencies in the range are non-zero.
    :param bands: The bands dictionary.
    :param freq: The frequency dictionary.
    :return: Adjusted bands and frequencies.
    """
    # Get the indices of the first and last non-zero elements.
    first = 0
    for k, v in freq.items():
        if v != 0:
            first = k
            break
    rev_keys = list(freq.keys())[::-1]
    last = rev_keys[0]
    for idx in list(freq.keys())[::-1]:
        if freq[idx] != 0:
            last = idx
            break
    # Now adjust the ranges.
    min_key = min(freq.keys())
    max_key = max(freq.keys())
    for idx in range(min_key, first):
        freq.pop(idx)
        bands.pop(idx)
    for idx in range(last + 1, max_key + 1):
        freq.popitem()
        bands.popitem()
    old_keys = freq.keys()
    adj_freq = dict()
    adj_bands = dict()

    for idx, k in enumerate(old_keys):
        adj_freq[idx] = freq[k]
        adj_bands[idx] = bands[k]

    return adj_bands, adj_freq


def get_bands(d_r, number_of_bands, precision=2, nearest_integer=False):
    """
    Divide a range into bands
    :param: d_r - [min, max] the range that is to be covered by the bands.
    :param: number_of_bands - The number of bands, a positive integer.
    :param: precision - The decimal precision of the bounds.
    :param: nearest_integer - If True then [floor(min), ceil(max)] is used.
    :return: A dictionary consisting of the band number and [min, midpoint, max] for each band.
    """
    prec = abs(precision)
    if prec > 14:
        prec = 14

    bands = dict()
    if (d_r[1] < d_r[0]) or (number_of_bands <= 0):
        return bands
    x = list(d_r)
    if nearest_integer:
        x[0] = math.floor(x[0])
        x[1] = math.ceil(x[1])
    dx = (x[1] - x[0]) / float(number_of_bands)
    b = [x[0], x[0] + dx / 2.0, x[0] + dx]
    i = 0
    while i < number_of_bands:
        b = list(map(lambda ele_b: round(ele_b, prec), b))
        if i == 0:
            b[0] = x[0]
        bands[i] = b
        b = [b[0] + dx, b[1] + dx, b[2] + dx]
        i += 1
    return bands


def print_bands_frequencies(bands, freq, precision=2):
    prec = abs(precision)
    if prec > 14:
        prec = 14

    if len(bands) != len(freq):
        print('Bands and Frequencies must be the same size.')
        return
    s = f'Bands & Frequencies:\n'
    total = 0
    width = prec + 6
    for k, v in bands.items():
        total += freq[k]
        for j, q in enumerate(v):
            if j == 0:
                s += f'{k:4d} ['
            if j == len(v) - 1:
                s += f'{q:{width}.{prec}f}]: {freq[k]:8d}\n'
            else:
                s += f'{q:{width}.{prec}f}, '
    width = 3 * width + 13
    s += f'{"Total":{width}s}{total:8d}\n'
    print(s)


if __name__ == '__main__':
    import sys

    main(sys.argv)
