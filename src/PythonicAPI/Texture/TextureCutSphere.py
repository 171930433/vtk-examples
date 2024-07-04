#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkDoubleArray,
    vtkPoints
)
from vtkmodules.vtkCommonDataModel import vtkPlanes
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkFiltersTexture import vtkImplicitTextureCoords
from vtkmodules.vtkIOLegacy import vtkStructuredPointsReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTexture
)


def main():
    colors = vtkNamedColors()

    file_name = get_program_parameters()

    # The hidden sphere
    sphere1 = vtkSphereSource(radius=0.5)

    inner_mapper = vtkPolyDataMapper()
    sphere1 >> inner_mapper

    inner_sphere = vtkActor(mapper=inner_mapper)
    inner_sphere.property.color = colors.GetColor3d('BlanchedAlmond')

    # The sphere to texture.
    sphere2 = vtkSphereSource(radius=1, phi_resolution=21, theta_resolution=21)

    pts = [0.0] * 6
    points = vtkPoints()
    points.SetNumberOfPoints(2)
    points.SetPoint(0, pts[:3])
    points.SetPoint(1, pts[3:])

    nrms = [0.0] * 6
    nrms[0] = 1.0
    nrms[4] = 1.0
    normals = vtkDoubleArray(number_of_components=3, number_of_tuples=2)
    normals.SetTuple(0, nrms[:3])
    normals.SetTuple(1, nrms[3:])

    planes = vtkPlanes(points=points, normals=normals)

    tcoords = vtkImplicitTextureCoords(r_function=planes)
    sphere2 >> tcoords

    outer_mapper = vtkDataSetMapper()
    sphere2 >> tcoords >> outer_mapper

    tmap = vtkStructuredPointsReader(file_name=file_name)

    texture = vtkTexture(interpolate=False, repeat=False)
    tmap >> texture

    outer_sphere = vtkActor(mapper=outer_mapper, texture=texture)
    outer_sphere.property.color = colors.GetColor3d('LightSalmon')

    ren_win = vtkRenderWindow(size=(500, 500), window_name='TextureCutSphere')
    iren = vtkRenderWindowInteractor()
    aren = vtkRenderer(background=colors.GetColor3d('SlateGray'))
    iren.render_window = ren_win
    ren_win.AddRenderer(aren)

    aren.AddActor(inner_sphere)
    aren.AddActor(outer_sphere)
    aren.active_camera.Azimuth(-30)
    aren.active_camera.Elevation(-30)
    aren.ResetCamera()

    # Interact with the data.
    ren_win.Render()

    iren.Initialize()
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'Cut an outer sphere to reveal an inner sphere.'
    epilogue = '''
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='File name e.g. texThres.vtk.')
    args = parser.parse_args()
    return args.filename


if __name__ == '__main__':
    main()
