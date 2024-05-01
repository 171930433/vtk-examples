#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkQuadric
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkFiltersTexture import vtkImplicitTextureCoords
from vtkmodules.vtkImagingHybrid import vtkBooleanTexture
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTexture
)


def main():
    positions = [
        [-4, 4, 0], [-2, 4, 0], [0, 4, 0], [2, 4, 0],
        [-4, 2, 0], [-2, 2, 0], [0, 2, 0], [2, 2, 0],
        [-4, 0, 0], [-2, 0, 0], [0, 0, 0], [2, 0, 0],
        [-4, -2, 0], [-2, -2, 0], [0, -2, 0], [2, -2, 0]
    ]

    colors = vtkNamedColors()

    ren_win = vtkRenderWindow(size=(500, 500), window_name='TextureCutQuadric')

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    aren = vtkRenderer(background=colors.GetColor3d('SlateGray'))

    # define two elliptical cylinders
    quadric1 = vtkQuadric(coefficients=(1, 2, 0, 0, 0, 0, 0, 0, 0, -.07))
    quadric2 = vtkQuadric(coefficients=(2, 1, 0, 0, 0, 0, 0, 0, 0, -.07))

    # Create a sphere for all to use.
    a_sphere = vtkSphereSource(phi_resolution=21, theta_resolution=21)

    # Create texture coordinates for all.
    tcoords = vtkImplicitTextureCoords(r_function=quadric1, s_function=quadric2)

    a_mapper = vtkDataSetMapper()
    a_sphere >> tcoords >> a_mapper

    # Create a mapper, sphere and texture map for each case.
    for i in range(0, 16):
        a_texture2 = vtkTexture(interpolate=False, repeat=False)
        make_boolean_texture(i, 64, 0) >> a_texture2
        an_actor2 = vtkActor(mapper=a_mapper, texture=a_texture2, position=positions[i], scale=(2.0, 2.0, 2.0))
        an_actor2.property.color = colors.GetColor3d('MistyRose')
        aren.AddActor(an_actor2)

    ren_win.AddRenderer(aren)

    # Interact with the data.
    ren_win.Render()

    iren.Start()


def make_boolean_texture(case_number, resolution, thickness):
    solid = [255, 255]
    clear = [255, 0]
    edge = [0, 255]

    boolean_texture = vtkBooleanTexture(x_size=resolution, y_size=resolution, thickness=thickness)
    if case_number == 0:
        boolean_texture.in_in = solid
        boolean_texture.out_in = solid
        boolean_texture.in_out = solid
        boolean_texture.out_out = solid
        boolean_texture.on_on = solid
        boolean_texture.on_in = solid
        boolean_texture.on_out = solid
        boolean_texture.in_on = solid
        boolean_texture.out_on = solid
    elif case_number == 1:  # cut inside 1
        boolean_texture.in_in = clear
        boolean_texture.out_in = solid
        boolean_texture.in_out = solid
        boolean_texture.out_out = solid
        boolean_texture.on_on = edge
        boolean_texture.on_in = edge
        boolean_texture.on_out = solid
        boolean_texture.in_on = edge
        boolean_texture.out_on = solid
    elif case_number == 2:  # cut outside 1
        boolean_texture.in_in = solid
        boolean_texture.out_in = clear
        boolean_texture.in_out = solid
        boolean_texture.out_out = solid
        boolean_texture.on_on = edge
        boolean_texture.on_in = edge
        boolean_texture.on_out = solid
        boolean_texture.in_on = solid
        boolean_texture.out_on = edge
    elif case_number == 3:  # cut all 1
        boolean_texture.in_in = clear
        boolean_texture.out_in = clear
        boolean_texture.in_out = solid
        boolean_texture.out_out = solid
        boolean_texture.on_on = edge
        boolean_texture.on_in = clear
        boolean_texture.on_out = solid
        boolean_texture.in_on = edge
        boolean_texture.out_on = edge
    elif case_number == 4:
        boolean_texture.in_in = solid
        boolean_texture.out_in = solid
        boolean_texture.in_out = clear
        boolean_texture.out_out = solid
        boolean_texture.on_on = edge
        boolean_texture.on_in = solid
        boolean_texture.on_out = edge
        boolean_texture.in_on = edge
        boolean_texture.out_on = solid
    elif case_number == 5:
        boolean_texture.in_in = clear
        boolean_texture.out_in = solid
        boolean_texture.in_out = clear
        boolean_texture.out_out = solid
        boolean_texture.on_on = edge
        boolean_texture.on_in = edge
        boolean_texture.on_out = edge
        boolean_texture.in_on = clear
        boolean_texture.out_on = solid
    elif case_number == 6:
        boolean_texture.in_in = solid
        boolean_texture.out_in = clear
        boolean_texture.in_out = clear
        boolean_texture.out_out = solid
        boolean_texture.on_on = edge
        boolean_texture.on_in = edge
        boolean_texture.on_out = edge
        boolean_texture.in_on = edge
        boolean_texture.out_on = edge
    elif case_number == 7:
        boolean_texture.in_in = clear
        boolean_texture.out_in = clear
        boolean_texture.in_out = clear
        boolean_texture.out_out = solid
        boolean_texture.on_on = edge
        boolean_texture.on_in = clear
        boolean_texture.on_out = edge
        boolean_texture.in_on = clear
        boolean_texture.out_on = edge
    elif case_number == 8:
        boolean_texture.in_in = solid
        boolean_texture.out_in = solid
        boolean_texture.in_out = solid
        boolean_texture.out_out = clear
        boolean_texture.on_on = edge
        boolean_texture.on_in = solid
        boolean_texture.on_out = edge
        boolean_texture.in_on = solid
        boolean_texture.out_on = edge
    elif case_number == 9:
        boolean_texture.in_in = clear
        boolean_texture.in_out = solid
        boolean_texture.out_in = solid
        boolean_texture.out_out = clear
        boolean_texture.on_on = edge
        boolean_texture.on_in = edge
        boolean_texture.on_out = edge
        boolean_texture.in_on = edge
        boolean_texture.out_on = edge
    elif case_number == 10:
        boolean_texture.in_in = solid
        boolean_texture.in_out = solid
        boolean_texture.out_in = clear
        boolean_texture.out_out = clear
        boolean_texture.on_on = edge
        boolean_texture.on_in = edge
        boolean_texture.on_out = edge
        boolean_texture.in_on = solid
        boolean_texture.out_on = clear
    elif case_number == 11:
        boolean_texture.in_in = clear
        boolean_texture.in_out = solid
        boolean_texture.out_in = clear
        boolean_texture.out_out = clear
        boolean_texture.on_on = edge
        boolean_texture.on_in = clear
        boolean_texture.on_out = edge
        boolean_texture.in_on = edge
        boolean_texture.out_on = clear
    elif case_number == 12:
        boolean_texture.in_in = solid
        boolean_texture.in_out = clear
        boolean_texture.out_in = solid
        boolean_texture.out_out = clear
        boolean_texture.on_on = edge
        boolean_texture.on_in = solid
        boolean_texture.on_out = clear
        boolean_texture.in_on = edge
        boolean_texture.out_on = edge
    elif case_number == 13:
        boolean_texture.in_in = clear
        boolean_texture.in_out = clear
        boolean_texture.out_in = solid
        boolean_texture.out_out = clear
        boolean_texture.on_on = edge
        boolean_texture.on_in = edge
        boolean_texture.on_out = clear
        boolean_texture.in_on = clear
        boolean_texture.out_on = edge
    elif case_number == 14:
        boolean_texture.in_in = solid
        boolean_texture.in_out = clear
        boolean_texture.out_in = clear
        boolean_texture.out_out = clear
        boolean_texture.on_on = edge
        boolean_texture.on_in = edge
        boolean_texture.on_out = clear
        boolean_texture.in_on = edge
        boolean_texture.out_on = clear
    else:  # case_number ==  15:
        boolean_texture.in_in = clear
        boolean_texture.in_out = clear
        boolean_texture.out_in = clear
        boolean_texture.out_out = clear
        boolean_texture.on_on = clear
        boolean_texture.on_in = clear
        boolean_texture.on_out = clear
        boolean_texture.in_on = clear
        boolean_texture.out_on = clear

    return boolean_texture


if __name__ == '__main__':
    main()
