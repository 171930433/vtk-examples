#!/usr/bin/env python3

from dataclasses import dataclass

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingFreeType
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import (
    vtkPlanes,
    vtkPolyData
)
from vtkmodules.vtkFiltersCore import vtkHull
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkInteractionWidgets import (
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty
)


def main():
    colors = vtkNamedColors()

    planes = list()
    titles = dict()

    # Using frustum planes.
    titles[0] = 'Using frustum planes'
    camera = vtkCamera()
    planes_array = [0] * 24
    camera.GetFrustumPlanes(1, planes_array)
    planes.append(vtkPlanes())
    planes[0].SetFrustumPlanes(planes_array)

    # Using bounds.
    titles[1] = 'Using bounds'
    sphere_source = vtkSphereSource()
    sphere_source.update()
    bounds = sphere_source.output.bounds
    planes.append(vtkPlanes())
    planes[1].bounds = bounds

    # At this point we have the planes created by both of the methods above.
    # You can do whatever you want with them.

    # For visualization, we will produce an n-sided convex hull
    # and visualise it.

    ren_win = vtkRenderWindow(size=(600, 600), window_name='Planes')

    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    actors = list()
    renderers = list()
    for i in range(0, len(planes)):
        hull = vtkHull(planes=planes[i])
        pd = vtkPolyData()

        # To generate the convex hull we supply a vtkPolyData object and a bounding box.
        # We define the bounding box to be where we expect the resulting polyhedron to lie.
        # Make it a generous fit as it is only used to create the initial
        # polygons that are eventually clipped.
        hull.GenerateHull(pd, -200, 200, -200, 200, -200, 200)

        mapper = vtkPolyDataMapper(input_data=pd)

        actor = vtkActor(mapper=mapper)
        actor.property.color = colors.GetColor3d('Moccasin')
        actor.property.specular = 0.8
        actor.property.specular_power = 30

        actors.append(actor)
        renderers.append(vtkRenderer())
        renderers[i].AddActor(actors[i])

        ren_win.AddRenderer(renderers[i])

    # Define viewport ranges [x_min, y_min, x_max, y_max]
    viewports = {0: [0.0, 0.0, 0.5, 1.0],
                 1: [0.5, 0.0, 1.0, 1.0]
                 }

    # Set up the viewports.
    x_grid_dimensions = 2
    y_grid_dimensions = 1
    renderer_size = 300
    ren_win.SetSize(renderer_size * x_grid_dimensions, renderer_size * y_grid_dimensions)
    for row in range(0, y_grid_dimensions):
        for col in range(0, x_grid_dimensions):
            index = row * x_grid_dimensions + col

            if index > (len(renderers) - 1):
                # Add a renderer even if there is no actor.
                # This makes the render window background all the same color.
                ren = vtkRenderer(background=colors.GetColor3d('DarkSlateGray'), viewport=viewports[index])
                ren_win.AddRenderer(ren)
                continue

            renderers[index].SetViewport(viewports[index])
            renderers[index].SetBackground(colors.GetColor3d('DarkSlateGray'))
            renderers[index].ResetCamera()
            renderers[index].active_camera.Azimuth(30)
            renderers[index].active_camera.Elevation(-30)
            renderers[index].ResetCameraClippingRange()

    # Create the TextActors.
    text_actors = list()
    text_representations = list()
    text_widgets = list()
    text_property = vtkTextProperty(color=colors.GetColor3d('PeachPuff'), bold=False, italic=False, shadow=False,
                                    font_size=12,
                                    justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                    vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_CENTERED)

    text_positions = get_text_positions(list(titles.values()),
                                        justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                        vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_BOTTOM,
                                        width=0.7
                                        )

    for k, v in titles.items():
        text_actors.append(
            vtkTextActor(input=v, text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_NONE, text_property=text_property))

        # Create the text representation. Used for positioning the text actor.
        text_representations.append(vtkTextRepresentation(enforce_normalized_viewport_bounds=True))
        text_representations[k].GetPositionCoordinate().value = text_positions[v]['p']
        text_representations[k].GetPosition2Coordinate().value = text_positions[v]['p2']

        # Create the TextWidget
        text_widgets.append(
            vtkTextWidget(representation=text_representations[k], text_actor=text_actors[k],
                          default_renderer=renderers[k], interactor=iren, selectable=False))

    iren.Initialize()
    ren_win.Render()

    for k in titles.keys():
        text_widgets[k].On()

    iren.Start()


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


if __name__ == '__main__':
    main()
