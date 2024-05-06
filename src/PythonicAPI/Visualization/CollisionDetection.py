#!/usr/bin/env python3

import time
from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingFreeType
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonMath import vtkMatrix4x4
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersModeling import vtkCollisionDetectionFilter
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkInteractionWidgets import (
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty
)


def get_program_parameters():
    import argparse
    description = 'Collision detection.'
    epilogue = '''
This examples uses vtkCollisionDetectionFilter to find the intersection between a
 fixed (solid white) and moving (red wireframe) sphere.
The animation places the moving sphere some distance from the fixed sphere and
 moves the moving sphere until it contacts the fixed sphere.

Three collision modes are available and can be set as the first argument on the command line.

1. All contacts (0) finds all the contacting cell pairs with two points per collision.
2. First contact (1) quickly find the first contact point.
3. Half contacts (2) finds all the contacting cell pairs with one points per collision.

    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('contactMode', nargs='?', default=0, type=int, help='Contact mode 0 (default), 1, or 2.')
    args = parser.parse_args()
    return args.contactMode


def main():
    contact_mode = get_program_parameters()

    # Define colors
    colors = vtkNamedColors()

    sphere0 = vtkSphereSource(radius=0.29, center=(0.0, 0, 0), phi_resolution=31, theta_resolution=31)

    sphere1 = vtkSphereSource(radius=0.3, center=(0.0, 0, 0), phi_resolution=30, theta_resolution=30)

    matrix1 = vtkMatrix4x4()
    transform0 = vtkTransform()

    collide = vtkCollisionDetectionFilter(transform=(0, transform0), matrix=(1, matrix1),
                                          box_tolerance=0.0, cell_tolerance=0.0, number_of_cells_per_node=2)
    collide.input_connection = (0, sphere0.GetOutputPort())
    collide.input_connection = (1, sphere1.GetOutputPort())
    if contact_mode == 0:
        collide.collision_mode = vtkCollisionDetectionFilter.VTK_ALL_CONTACTS
    elif contact_mode == 1:
        collide.collision_mode = vtkCollisionDetectionFilter.VTK_FIRST_CONTACT
    else:
        collide.collision_mode = vtkCollisionDetectionFilter.VTK_HALF_CONTACTS

    collide.GenerateScalarsOn()

    # Visualize
    mapper1 = vtkPolyDataMapper(scalar_visibility=False)
    mapper1.input_connection = collide.GetOutputPort(0)
    actor1 = vtkActor(mapper=mapper1, user_transform=transform0)
    actor1.property.backface_culling = True
    actor1.property.diffuse_color = colors.GetColor3d("Tomato")
    actor1.property.representation = Property.Representation.VTK_WIREFRAME

    mapper2 = vtkPolyDataMapper()
    mapper2.input_connection = collide.GetOutputPort(1)
    actor2 = vtkActor(mapper=mapper2, user_matrix=matrix1)
    actor2.property.backface_culling = True

    mapper3 = vtkPolyDataMapper(
        resolve_coincident_topology=Mapper.ResolveCoincidentTopology.VTK_RESOLVE_POLYGON_OFFSET)
    mapper3.input_connection = collide.GetContactsOutputPort()
    actor3 = vtkActor(mapper=mapper3)
    actor3.property.color = colors.GetColor3d("Black")
    actor3.property.line_width = 3.0

    renderer = vtkRenderer(background=colors.GetColor3d('Gray'))
    renderer.UseHiddenLineRemovalOn()
    renderer.AddActor(actor1)
    renderer.AddActor(actor2)
    renderer.AddActor(actor3)

    render_window = vtkRenderWindow(size=(640, 480), window_name='CollisionDetection')
    render_window.AddRenderer(renderer)

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Move the first object
    num_steps = 100
    dx = 1.0 / float(num_steps) * 2.0
    transform0.Translate(-num_steps * dx - .3, 0.0, 0.0)
    render_window.Render()
    renderer.GetActiveCamera().Azimuth(-60)
    renderer.GetActiveCamera().Elevation(45)
    renderer.GetActiveCamera().Dolly(1.2)

    render_window.Render()

    for i in range(0, num_steps):
        transform0.Translate(dx, 0.0, 0.0)
        renderer.ResetCameraClippingRange()
        render_window.Render()
        if collide.number_of_contacts > 0:
            text_property = vtkTextProperty(color=colors.GetColor3d('White'), bold=True, italic=False, shadow=True,
                                            font_size=16, justification=TextProperty.Justification.VTK_TEXT_CENTERED)

            s = f'{collide.GetCollisionModeAsString()}, the number of contact cells is {collide.GetNumberOfContacts():d}'

            text_positions = get_text_positions([s],
                                                justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                                width=0.5, height=0.1)
            text_actor = vtkTextActor(input=s,
                                      text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_NONE,
                                      text_property=text_property)

            # Create the text representation. Used for positioning the text actor.
            text_representation = vtkTextRepresentation(enforce_normalized_viewport_bounds=True)
            text_representation.GetPositionCoordinate().value = text_positions[s]['p']
            text_representation.GetPosition2Coordinate().value = text_positions[s]['p2']

            # Create the text widget, setting the default renderer and interactor.
            text_widget = vtkTextWidget(representation=text_representation, text_actor=text_actor,
                                        default_renderer=renderer,
                                        interactor=interactor, selectable=False)
            text_widget.On()
            break
        # The total animation time is 3 seconds
        time.sleep(3.0 / num_steps)

    renderer.ResetCamera()
    render_window.Render()
    interactor.Start()
    # In Field Data there will be an array named "ContactCells".
    # This array indexes contacting cells (e.g.) index 10 of array 0
    #  points to a cell (triangle) which contacts/intersects a cell
    #  at index 10 of array 1.
    # You can directly obtain these, see GetContactCells(int i)
    #  in the documentation.
    # print(collide.GetOutput(0))
    # print(collide.GetOutput(1))


def get_text_positions(names, justification=0, vertical_justification=0, width=0.96, height=0.1):
    """
    Get viewport positioning information for a list of names.

    :param names: The list of names.
    :param justification: Horizontal justification of the text, default is left.
    :param vertical_justification: Vertical justification of the text, default is bottom.
    :param width: Width of the bounding_box of the text in screen coordinates.
    :param height: Height of the bounding_box of the text in screen coordinates.
    :return: A list of positioning information.
    """
    # The gap between the left or right edge of the screen and the text.
    dx = 0.02
    width = abs(width)
    if width > 0.96:
        width = 0.96

    y0 = 0.01
    height = abs(height)
    if height > 0.9:
        height = 0.9
    dy = height
    if vertical_justification == TextProperty.VerticalJustification.VTK_TEXT_TOP:
        y0 = 1.0 - (dy + y0)
        dy = height
    if vertical_justification == TextProperty.VerticalJustification.VTK_TEXT_CENTERED:
        y0 = 0.5 - (dy / 2.0 + y0)
        dy = height

    name_len_min = 0
    name_len_max = 0
    first = True
    for k in names:
        sz = len(k)
        if first:
            name_len_min = name_len_max = sz
            first = False
        else:
            name_len_min = min(name_len_min, sz)
            name_len_max = max(name_len_max, sz)
    text_positions = dict()
    for k in names:
        sz = len(k)
        delta_sz = width * sz / name_len_max
        if delta_sz > width:
            delta_sz = width

        if justification == TextProperty.Justification.VTK_TEXT_CENTERED:
            x0 = 0.5 - delta_sz / 2.0
        elif justification == TextProperty.Justification.VTK_TEXT_RIGHT:
            x0 = 1.0 - dx - delta_sz
        else:
            # Default is left justification.
            x0 = dx

        # For debugging!
        # print(
        #     f'{k:16s}: (x0, y0) = ({x0:3.2f}, {y0:3.2f}), (x1, y1) = ({x0 + delta_sz:3.2f}, {y0 + dy:3.2f})'
        #     f', width={delta_sz:3.2f}, height={dy:3.2f}')
        text_positions[k] = {'p': [x0, y0, 0], 'p2': [delta_sz, dy, 0]}

    return text_positions


@dataclass(frozen=True)
class Mapper:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_MODE_DEFAULT: int = 0
        VTK_COLOR_MODE_MAP_SCALARS: int = 1
        VTK_COLOR_MODE_DIRECT_SCALARS: int = 2

    @dataclass(frozen=True)
    class ResolveCoincidentTopology:
        VTK_RESOLVE_OFF: int = 0
        VTK_RESOLVE_POLYGON_OFFSET: int = 1
        VTK_RESOLVE_SHIFT_ZBUFFER: int = 2

    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_DEFAULT: int = 0
        VTK_SCALAR_MODE_USE_POINT_DATA: int = 1
        VTK_SCALAR_MODE_USE_CELL_DATA: int = 2
        VTK_SCALAR_MODE_USE_POINT_FIELD_DATA: int = 3
        VTK_SCALAR_MODE_USE_CELL_FIELD_DATA: int = 4
        VTK_SCALAR_MODE_USE_FIELD_DATA: int = 5


@dataclass(frozen=True)
class TextProperty:
    @dataclass(frozen=True)
    class Justification:
        VTK_TEXT_LEFT: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_RIGHT: int = 2

    @dataclass(frozen=True)
    class VerticalJustification:
        VTK_TEXT_BOTTOM: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_TOP: int = 2


@dataclass(frozen=True)
class Property:
    @dataclass(frozen=True)
    class Interpolation:
        VTK_FLAT: int = 0
        VTK_GOURAUD: int = 1
        VTK_PHONG: int = 2
        VTK_PBR: int = 3

    @dataclass(frozen=True)
    class Representation:
        VTK_POINTS: int = 0
        VTK_WIREFRAME: int = 1
        VTK_SURFACE: int = 2


if __name__ == '__main__':
    main()
